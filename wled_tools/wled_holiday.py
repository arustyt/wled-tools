import argparse
import calendar
import re
import sys
from operator import itemgetter

from dateutil.rrule import *

from wled_constants import DEFAULT_DEFINITIONS_DIR, DEFAULT_HOLIDAYS_FILE, DEFAULT_HOLIDAY_PRESETS_FILE, \
    DEFAULT_HOLIDAY_NAME, \
    HOLIDAYS_KEY, DATE_KEY, RRULE_KEY, DAY_OF_YEAR_KEY, DEFAULT_DATA_DIR, DEFAULT_WLED_DIR, HOLIDAY_KEY, PRESETS_KEY, \
    ABBREVIATION_KEY
from wled_utils.date_utils import get_date_str, get_todays_date_str, parse_date_str, calculate_date, \
    calculate_day_of_year_and_week
from wled_utils.dict_utils import normalize_keys
from wled_utils.logger_utils import get_logger, init_logger
from wled_utils.path_utils import build_path, presets_file_exists, choose_existing_presets
from wled_utils.rrule_utils import get_frequency, get_byweekday, interpret_general_rrule, interpret_easter_rrule
from wled_utils.yaml_multi_file_loader import load_yaml_file

RRULE_FREQUENCY_KEY = 'frequency'
RRULE_INTERVAL_KEY = 'interval'
RRULE_MOD_KEY = 'mod'
RRULE_BY_MONTH_KEY = 'month'
RRULE_MONTHDAY_KEY = 'day_of_month'
RRULE_WEEKDAY_KEY = 'day_of_week'

PLACEHOLDER_RE = re.compile(r'([a-zA-Z0-9_]*)([+-][1-9][0-9]*)')
DATE_RE = re.compile(r'([0-9][0-9][0-9][0-9])([+-][1-9][0-9]*)*')

BY_EASTER_KEY = 'by_easter'

END_DAY_OF_YEAR_KEY = 'end_day_of_year'
START_DAY_OF_YEAR_KEY = 'start_day_of_year'
START_DATE_KEY = 'start_date'
END_DATE_KEY = 'end_date'
HOLIDAY_PRESETS_KEY = "presets"

ALL_DATES = '*'


def main(name, args):
    arg_parser = argparse.ArgumentParser(
        description="Returns suffix for wled presets corresponding to provided date or today if none provided",
    )
    arg_parser.add_argument("--data_dir", type=str,
                            help="Directory from which --definitions_rel_dir is relative.",
                            action="store")
    arg_parser.add_argument("--definitions_dir", type=str,
                            help="Definition file location. Applies to --holidays and --holiday_presets files. If not "
                                 "specified, '" + DEFAULT_DEFINITIONS_DIR + "' is used.",
                            action="store", default=DEFAULT_DEFINITIONS_DIR)
    arg_parser.add_argument("--wled_dir", type=str,
                            help="WLED data file location. Applies to presets, cfg, and segments files. If not "
                                 "specified, '" + DEFAULT_WLED_DIR + "' is used.",
                            action="store", default=DEFAULT_WLED_DIR)
    arg_parser.add_argument("--holidays", type=str, help="Holiday definitions file name (YAML) relative to the "
                                                         "--definitions_rel_dir directory. If not specified, '" +
                                                         DEFAULT_HOLIDAYS_FILE + "' is used.",
                            action="store", default=DEFAULT_HOLIDAYS_FILE)
    arg_parser.add_argument("--holiday_presets", type=str,
                            help="WLED holiday presets definitions file-name (YAML) relative to the "
                                 "--definitions_rel_dir directory. If not specified, '" +
                                 DEFAULT_HOLIDAY_PRESETS_FILE + "' is used.",
                            action="store", default=DEFAULT_HOLIDAY_PRESETS_FILE)
    arg_parser.add_argument('--all', help="Display all dates for entire year specified by the 'date' argument.",
                            action='store_true')
    arg_parser.add_argument('--missing', help="Display only dates with missing_only presets file. Ignored unless "
                                              "--all is specified.",
                            action='store_true')
    arg_parser.add_argument('--verbose', help="Intermediate output will be generated in addition to result output.",
                            action='store_true')

    arg_parser.add_argument("date", type=str, help="Date (YYYY-MM-DD) for which holiday presets are to be "
                                                   "evaluated. If not specified, today's date is used.",
                            action="store", nargs='?', default=None)

    args = arg_parser.parse_args()
    data_dir = args.data_dir
    definitions_rel_dir = args.definitions_dir
    wled_rel_dir = args.wled_dir
    holidays_file = args.holidays
    holiday_presets_file = args.holiday_presets
    verbose_mode = args.verbose
    all_dates = args.all
    missing_only = args.missing
    date_str = args.date

    init_logger()

    if verbose_mode:
        get_logger().info("OPTION VALUES ...")
        get_logger().info("  data_dir: " + data_dir)
        get_logger().info("  definitions_rel_dir: " + definitions_rel_dir)
        get_logger().info("  wled_rel_dir: " + wled_rel_dir)
        get_logger().info("  holidays_file: " + holidays_file)
        get_logger().info("  holiday_presets_file: " + holiday_presets_file)
        get_logger().info("  date_str: " + str(date_str))

    if date_str is None:
        date_str = get_todays_date_str()

    if not all_dates:
        process_one_date(date_str, data_dir, definitions_rel_dir, holidays_file, holiday_presets_file, verbose_mode)
    else:
        process_all_dates(date_str, data_dir, definitions_rel_dir, wled_rel_dir, holidays_file, holiday_presets_file,
                          missing_only)


def process_one_date(date_str, data_dir, definitions_dir, holidays_file, holiday_presets_file, verbose_mode):
    try:
        evaluation_date = parse_date_str(date_str)
    except ValueError:
        raise ValueError("Invalid date format. Must be YYYY-MM-DD.")
    if verbose_mode:
        get_logger().info("  date to process: " + str(evaluation_date))

    wled_holiday_presets = WledHoliday(data_dir=data_dir, definitions_rel_dir=definitions_dir,
                                       holidays_file=holidays_file,
                                       holiday_presets_file=holiday_presets_file, evaluation_date=evaluation_date,
                                       verbose_mode=verbose_mode)
    matched_holiday_presets_list = wled_holiday_presets.evaluate_presets_for_date(evaluation_date=evaluation_date)

    if verbose_mode:
        get_logger().info("  Matched Holiday: " + str(matched_holiday_presets_list))


def process_all_dates(date_str, data_dir, definitions_dir, wled_dir, holidays_file, holiday_presets_file, missing_only):
    try:
        evaluation_date = parse_date_str(date_str)
    except ValueError:
        raise ValueError("Invalid date format. Must be YYYY-MM-DD.")
    first_day_of_year = calculate_date(evaluation_date, 1, 1)
    count = 365

    if calendar.isleap(first_day_of_year.year):
        count += 1

    dates = list(rrule(DAILY, dtstart=first_day_of_year, count=count))

    wled_presets = WledHoliday(data_dir=data_dir, definitions_rel_dir=definitions_dir, holidays_file=holidays_file,
                               holiday_presets_file=holiday_presets_file, evaluation_date=evaluation_date,
                               verbose_mode=False)

    holidays_without_presets = set()
    holidays_without_specific_presets = set()
    for evaluation_date in dates:
        matched_holiday_presets_list = wled_presets.evaluate_presets_for_date(evaluation_date=evaluation_date)
        if len(matched_holiday_presets_list) > 0:
            holiday_name = matched_holiday_presets_list[0][HOLIDAY_KEY]
            matched_holiday_presets = matched_holiday_presets_list[0][PRESETS_KEY]
            chosen_presets = choose_existing_presets(data_dir, wled_dir, matched_holiday_presets_list)
            chosen_holiday_presets = chosen_presets[PRESETS_KEY]
            if chosen_holiday_presets is not None:
                if not missing_only:
                    get_logger().info(
                        "{date}: {holiday}, candidates: {candidates}, {match}: EXISTS".
                        format(date=get_date_str(evaluation_date), holiday=holiday_name,
                               candidates=matched_holiday_presets_list, match=chosen_holiday_presets))
                if chosen_holiday_presets != matched_holiday_presets:
                    holidays_without_specific_presets.add(holiday_name)
            else:
                if not missing_only:
                    get_logger().info(
                        "{date}: {holiday}, candidates: {candidates} DO NOT EXIST".
                        format(date=get_date_str(evaluation_date), holiday=holiday_name,
                               candidates=matched_holiday_presets_list))
                holidays_without_presets.add(holiday_name)
        else:
            if not missing_only:
                get_logger().info("{date}: NOT A DEFINED HOLIDAY".format(date=get_date_str(evaluation_date)))

    get_logger().info("The following holidays have no presets file: {holidays}".
                      format(holidays=holidays_without_presets))
    get_logger().info("The following holidays do not have a holiday-specific presets file: {holidays}".
                      format(holidays=holidays_without_specific_presets))


def get_wled_holiday_presets(*, data_dir, definitions_rel_dir=None, holidays_file=None, holiday_presets_file=None,
                             evaluation_date=None, verbose_mode=False):
    definitions_rel_dir = get_optional_arg(definitions_rel_dir, DEFAULT_DEFINITIONS_DIR)
    holidays_file = get_optional_arg(holidays_file, DEFAULT_HOLIDAYS_FILE)
    holiday_presets_file = get_optional_arg(holiday_presets_file, DEFAULT_HOLIDAY_PRESETS_FILE)
    if evaluation_date is None:
        evaluation_date = get_todays_date_str()
    wled_holiday_presets = WledHoliday(data_dir=data_dir, definitions_rel_dir=definitions_rel_dir,
                                       holidays_file=holidays_file,
                                       holiday_presets_file=holiday_presets_file, evaluation_date=evaluation_date,
                                       verbose_mode=verbose_mode)
    matched_holiday_presets_list = wled_holiday_presets.evaluate_presets_for_date(evaluation_date=evaluation_date)

    return matched_holiday_presets_list


def get_optional_arg(arg_value, default):
    return arg_value if arg_value is None else default


class WledHoliday:

    def __init__(self, *, data_dir, definitions_rel_dir, holidays_file, holiday_presets_file, evaluation_date,
                 verbose_mode):

        definitions_dir = "{base}/{rel_dir}".format(base=data_dir, rel_dir=definitions_rel_dir)
        holidays_path = build_path(definitions_dir, holidays_file)
        self.holidays_data = load_yaml_file(holidays_path)
        self.evaluate_holidays(self.holidays_data, evaluation_date)
        normalize_keys(self.holidays_data[HOLIDAYS_KEY])

        holiday_presets_path = build_path(definitions_dir, holiday_presets_file)
        self.presets_data = load_yaml_file(holiday_presets_path)
        normalize_keys(self.presets_data[HOLIDAYS_KEY])
        self.verbose_mode = verbose_mode

        self.holiday_dates = self.evaluate_holiday_presets_dates(evaluation_date)

    def evaluate_presets_for_date(self, evaluation_date):
        evaluation_day_of_year, evaluation_day_of_week = calculate_day_of_year_and_week(evaluation_date)
        matched_holidays = []
        for holiday in self.holiday_dates:
            candidate_holiday = self.holiday_dates[holiday]
            start_day_of_year = candidate_holiday[START_DAY_OF_YEAR_KEY]
            end_day_of_year = candidate_holiday[END_DAY_OF_YEAR_KEY]
            if start_day_of_year is None or end_day_of_year is None:
                continue
            if start_day_of_year <= evaluation_day_of_year <= end_day_of_year:
                day_of_year_range = end_day_of_year - start_day_of_year + 1
                matched_holiday, matched_presets = self.get_holiday_and_presets(candidate_holiday,
                                                                                evaluation_day_of_week, holiday,
                                                                                candidate_holiday[HOLIDAY_PRESETS_KEY])
                matched_holidays.append((matched_holiday, matched_presets, day_of_year_range))

        sorted_matched_holidays = sorted(matched_holidays, key=itemgetter(2))
        candidates = [{HOLIDAY_KEY: item[0], PRESETS_KEY: item[1]} for item in sorted_matched_holidays]

        return candidates

    @staticmethod
    def get_holiday_and_presets(candidate_holiday: dict, day_of_week: dict, holiday, presets):
        matched_holiday = holiday
        matched_presets = presets
        if day_of_week[ABBREVIATION_KEY] in candidate_holiday:
            dow = candidate_holiday[day_of_week[ABBREVIATION_KEY]]
            if PRESETS_KEY in dow:
                matched_presets = dow[PRESETS_KEY]
            if HOLIDAY_KEY in dow:
                matched_holiday = dow[HOLIDAY_KEY]

        return matched_holiday, matched_presets

    def evaluate_holiday_presets_dates(self, evaluation_date):
        holiday_dates = dict()
        all_holidays = self.presets_data[HOLIDAYS_KEY]
        for holiday in all_holidays:
            holiday_dates[holiday] = dict()
            holiday_data = all_holidays[holiday]
            holiday_dates[holiday][START_DAY_OF_YEAR_KEY], holiday_dates[holiday][END_DAY_OF_YEAR_KEY] = \
                self.evaluate_holiday_dates(holiday_data, evaluation_date)
            holiday_dates[holiday][HOLIDAY_PRESETS_KEY] = holiday_data[HOLIDAY_PRESETS_KEY]
            for key in holiday_data:
                if key not in [START_DATE_KEY, END_DATE_KEY]:
                    holiday_dates[holiday][key] = holiday_data[key]

        return holiday_dates

    def evaluate_holiday_dates(self, holiday, evaluation_date):
        start_day_of_year = self.interpret_date_expr(holiday[START_DATE_KEY], evaluation_date)
        end_day_of_year = self.interpret_date_expr(holiday[END_DATE_KEY], evaluation_date)

        return start_day_of_year, end_day_of_year

    def interpret_date_expr(self, date_expr, evaluation_date):

        day_of_year = self.interpret_numeric_expr(date_expr, evaluation_date)
        if day_of_year is None:
            day_of_year = self.interpret_placeholder_expr(date_expr)

        return day_of_year

    def interpret_placeholder_expr(self, date_expr):
        delta = 0
        sign = 1

        matches = re.match(PLACEHOLDER_RE, date_expr)
        if matches is not None:
            holiday = matches.groups()[0]
            delta_str = matches.groups()[1]
            sign = 1 if delta_str[0] == '+' else -1
            delta = int(delta_str[1:])
        else:
            holiday = date_expr

        holiday_date = self.holidays_data[HOLIDAYS_KEY][holiday][DAY_OF_YEAR_KEY]

        if holiday_date is None:
            return None

        day_of_year = holiday_date + sign * delta
        return day_of_year

    def interpret_numeric_expr(self, date_expr, evaluation_date):
        matches = re.match(DATE_RE, date_expr)
        if matches is None:
            return None

        mmdd = matches.groups()[0]
        delta_str = matches.groups()[1]
        if delta_str is not None:
            sign = 1 if delta_str[0] == '+' else -1
            delta = int(delta_str[1:])
        else:
            sign = 1
            delta = 0

        month = int(mmdd[0:2])
        day = int(mmdd[2:4])

        day_of_year, day_of_week = calculate_day_of_year_and_week(evaluation_date, month, day)

        return day_of_year + sign * delta

    def evaluate_holidays(self, holidays_data: dict, evaluation_date):
        holidays = holidays_data[HOLIDAYS_KEY]
        for holiday_key in holidays:
            holiday = holidays[holiday_key]
            if DATE_KEY in holiday:
                holiday_day_of_year = self.interpret_numeric_expr(holiday[DATE_KEY], evaluation_date)
            elif RRULE_KEY in holiday:
                holiday_day_of_year = self.interpret_rrule(holiday[RRULE_KEY], evaluation_date)
            else:
                raise ValueError(
                    "Invalid holiday specification. Must include either {date} or {rrule}".format(date=DATE_KEY,
                                                                                                  rrule=RRULE_KEY))

            holiday[DAY_OF_YEAR_KEY] = holiday_day_of_year

    def interpret_rrule(self, holiday_rrule: dict, evaluation_date):
        frequency_str = holiday_rrule.get(RRULE_FREQUENCY_KEY)
        if frequency_str is None:
            raise LookupError("Missing required field: {}.".format(RRULE_FREQUENCY_KEY))
        frequency = get_frequency(frequency_str)

        interval = holiday_rrule.get(RRULE_INTERVAL_KEY, 1)
        mod = holiday_rrule.get(RRULE_MOD_KEY, 0)
        start_date = calculate_date(evaluation_date, 1, 1, frequency_str, interval, mod)
        if start_date.year != evaluation_date.year:
            return None
        if BY_EASTER_KEY in holiday_rrule:
            holiday_date = interpret_easter_rrule(frequency, interval, holiday_rrule.get(BY_EASTER_KEY), start_date)
        else:
            by_month = holiday_rrule.get(RRULE_BY_MONTH_KEY)
            days_of_week = holiday_rrule.get(RRULE_WEEKDAY_KEY)
            by_weekday = self.get_by_weekday(days_of_week)
            days_of_month = holiday_rrule.get(RRULE_MONTHDAY_KEY)
            by_monthday = self.get_by_monthday(days_of_month)

            holiday_date = interpret_general_rrule(frequency, interval, by_month, by_weekday, by_monthday, start_date)

        return holiday_date.timetuple().tm_yday

    @staticmethod
    def get_by_monthday(days_of_month):
        if days_of_month is None:
            return None
        if isinstance(days_of_month, str):
            by_monthday = days_of_month
        elif isinstance(days_of_month, list):
            by_monthday = tuple(days_of_month)
        else:
            raise ValueError('Invalid day_of_month: {}'.format(days_of_month))
        return by_monthday

    @staticmethod
    def get_by_weekday(days_of_week):
        if days_of_week is None:
            return None
        if isinstance(days_of_week, str):
            by_weekday = get_byweekday(days_of_week)
        elif isinstance(days_of_week, list):
            week_days = []
            for day_of_week in days_of_week:
                week_days.append(get_byweekday(day_of_week))
            by_weekday = tuple(week_days)
        else:
            raise ValueError('Invalid day_of_week: {}'.format(days_of_week))

        return by_weekday


if __name__ == '__main__':
    main(sys.argv[0], sys.argv[1:])
