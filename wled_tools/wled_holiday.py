import argparse
import calendar
import datetime
import re
import sys
from datetime import *
from operator import itemgetter

from dateutil.rrule import *

from wled_constants import DEFAULT_DEFINITIONS_DIR, DEFAULT_HOLIDAYS_FILE, DEFAULT_LIGHTS_FILE, DEFAULT_HOLIDAY_NAME, \
    HOLIDAYS_KEY, DATE_KEY, RRULE_KEY, DAY_OF_YEAR_KEY, DEFAULT_DATA_DIR, DEFAULT_WLED_DIR, HOLIDAY_KEY, LIGHTS_KEY
from wled_utils.date_utils import get_date_str, get_todays_date_str, parse_date_str
from wled_utils.logger_utils import get_logger, init_logger
from wled_utils.path_utils import build_path, presets_file_exists, choose_existing_presets
from wled_utils.rrule_utils import get_frequency, get_byweekday
from wled_utils.yaml_multi_file_loader import load_yaml_file

PLACEHOLDER_RE = re.compile(r'([a-zA-Z0-9_]*)([+-][1-9][0-9]*)')
DATE_RE = re.compile(r'([0-9][0-9][0-9][0-9])([+-][1-9][0-9]*)*')

BY_EASTER_KEY = 'by_easter'

END_DAY_OF_YEAR_KEY = 'end_day_of_year'
START_DAY_OF_YEAR_KEY = 'start_day_of_year'
START_DATE_KEY = 'start_date'
END_DATE_KEY = 'end_date'
HOLIDAY_LIGHTS_KEY = "lights"

ALL_DATES = '*'


def main(name, args):
    arg_parser = argparse.ArgumentParser(
        description="Returns suffix for wled lights corresponding to provided date or today if none provided",
    )
    arg_parser.add_argument("--data_dir", type=str,
                            help="Directory from which --definitions_rel_dir is relative.",
                            action="store")
    arg_parser.add_argument("--definitions_dir", type=str,
                            help="Definition file location. Applies to --holidays and --lights files. If not "
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
    arg_parser.add_argument("--lights", type=str,
                            help="WLED holiday lights definitions file-name (YAML) relative to the "
                                 "--definitions_rel_dir directory. If not specified, '" +
                                 DEFAULT_LIGHTS_FILE + "' is used.",
                            action="store", default=DEFAULT_LIGHTS_FILE)
    arg_parser.add_argument('--all', help="Display all dates for entire year specified by the 'date' argument.",
                            action='store_true')
    arg_parser.add_argument('--missing', help="Display only dates with missing_only presets file. Ignored unless "
                                              "--all is specified.",
                            action='store_true')
    arg_parser.add_argument('--verbose', help="Intermediate output will be generated in addition to result output.",
                            action='store_true')

    arg_parser.add_argument("date", type=str, help="Date (YYYY-MM-DD) for which holiday lights it to be evaluated. "
                                                   "If not specified, today's date is used.",
                            action="store", nargs='?', default=None)

    args = arg_parser.parse_args()
    data_dir = args.data_dir
    definitions_rel_dir = args.definitions_dir
    wled_rel_dir = args.wled_dir
    holidays_file = args.holidays
    lights_file = args.lights
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
        get_logger().info("  lights_file: " + lights_file)
        get_logger().info("  date_str: " + str(date_str))

    if date_str is None:
        date_str = get_todays_date_str()

    if not all_dates:
        process_one_date(date_str, data_dir, definitions_rel_dir, holidays_file, lights_file, verbose_mode)
    else:
        process_all_dates(date_str, data_dir, definitions_rel_dir, wled_rel_dir, holidays_file, lights_file, missing_only)


def process_one_date(date_str, data_dir, definitions_dir, holidays_file, lights_file, verbose_mode):
    try:
        evaluation_date = parse_date_str(date_str)
    except ValueError:
        raise ValueError("Invalid date format. Must be YYYY-MM-DD.")
    if verbose_mode:
        get_logger().info("  date to process: " + str(evaluation_date))

    wled_lights = WledHoliday(data_dir=data_dir, definitions_rel_dir=definitions_dir, holidays_file=holidays_file,
                              lights_file=lights_file, evaluation_date=evaluation_date, verbose_mode=verbose_mode)
    matched_holiday_lights_list = wled_lights.evaluate_lights_for_date(evaluation_date=evaluation_date)

    if verbose_mode:
        get_logger().info("  Matched Holiday: " + str(matched_holiday_lights_list))


def process_all_dates(date_str, data_dir, definitions_dir, wled_dir, holidays_file, lights_file, missing_only):
    try:
        evaluation_date = parse_date_str(date_str)
    except ValueError:
        raise ValueError("Invalid date format. Must be YYYY-MM-DD.")
    first_day_of_year = calculate_date(evaluation_date, 1, 1)
    count = 365

    if calendar.isleap(first_day_of_year.year):
        count += 1

    dates = list(rrule(DAILY, dtstart=first_day_of_year, count=count))

    wled_lights = WledHoliday(data_dir=data_dir, definitions_rel_dir=definitions_dir, holidays_file=holidays_file,
                              lights_file=lights_file, evaluation_date=evaluation_date, verbose_mode=False)

    holidays_without_presets = set()
    holidays_without_specific_presets = set()
    for evaluation_date in dates:
        matched_holiday_lights_list = wled_lights.evaluate_lights_for_date(evaluation_date=evaluation_date)
        if len(matched_holiday_lights_list) > 0:
            holiday_name = matched_holiday_lights_list[0][HOLIDAY_KEY]
            matched_holiday_lights = matched_holiday_lights_list[0][LIGHTS_KEY]
            chosen_presets = choose_existing_presets(data_dir, wled_dir, matched_holiday_lights_list)
            chosen_holiday_lights = chosen_presets[LIGHTS_KEY]
            if chosen_holiday_lights is not None:
                if not missing_only:
                    get_logger().info(
                        "{date}: {holiday}, candidates: {candidates}, {match}: EXISTS".
                        format(date=get_date_str(evaluation_date), holiday=holiday_name,
                               candidates=matched_holiday_lights_list, match=chosen_holiday_lights))
                if chosen_holiday_lights != matched_holiday_lights:
                    holidays_without_specific_presets.add(holiday_name)
            else:
                if not missing_only:
                    get_logger().info(
                        "{date}: {holiday}, candidates: {candidates} DO NOT EXIST".
                        format(date=get_date_str(evaluation_date), holiday=holiday_name,
                               candidates=matched_holiday_lights_list))
                holidays_without_presets.add(holiday_name)
        else:
            if not missing_only:
                get_logger().info("{date}: NOT A DEFINED HOLIDAY".format(date=get_date_str(evaluation_date)))

    get_logger().info("The following holidays have no presets file: {holidays}".
                      format(holidays=holidays_without_presets))
    get_logger().info("The following holidays do not have a holiday-specific presets file: {holidays}".
                      format(holidays=holidays_without_specific_presets))


def calculate_date(evaluation_date: datetime, evaluation_day, evaluation_month):
    evaluation_year = evaluation_date.year
    if evaluation_month is None:
        evaluation_month = evaluation_date.month
    if evaluation_day is None:
        evaluation_day = evaluation_date.day
    calc_date = datetime(evaluation_year, evaluation_month, evaluation_day)
    return calc_date


class WledHoliday:

    def __init__(self, *, data_dir, definitions_rel_dir, holidays_file, lights_file, evaluation_date,
                 verbose_mode):

        definitions_dir = "{base}/{rel_dir}".format(base=data_dir, rel_dir=definitions_rel_dir)
        holidays_path = build_path(definitions_dir, holidays_file)
        self.holidays_data = load_yaml_file(holidays_path)
        self.evaluate_holidays(self.holidays_data, evaluation_date)
        self.normalize_keys(self.holidays_data)

        lights_path = build_path(definitions_dir, lights_file)
        self.lights_data = load_yaml_file(lights_path)
        self.normalize_keys(self.lights_data)
        self.verbose_mode = verbose_mode

        self.holiday_dates = self.evaluate_holiday_lights_dates(evaluation_date)

    def evaluate_lights_for_date(self, evaluation_date):

        evaluation_day_of_year = self.calculate_day_of_year(evaluation_date)
        matched_holidays = []
        for holiday in self.holiday_dates:
            candidate_holiday = self.holiday_dates[holiday]
            start_day_of_year = candidate_holiday[START_DAY_OF_YEAR_KEY]
            end_day_of_year = candidate_holiday[END_DAY_OF_YEAR_KEY]
            if start_day_of_year <= evaluation_day_of_year <= end_day_of_year:
                day_of_year_range = end_day_of_year - start_day_of_year + 1
                matched_holidays.append((holiday, candidate_holiday[HOLIDAY_LIGHTS_KEY], day_of_year_range))

        # candidates = []
        # for item in sorted(matched_holidays, key=itemgetter(1)):
        #     candidates.append(item[0])
        sorted_matched_holidays = sorted(matched_holidays, key=itemgetter(2))
        if len(sorted_matched_holidays) > 0:
            matched_holiday_name = sorted_matched_holidays[0][0]
        else:
            matched_holiday_name = None

        candidates = [{HOLIDAY_KEY: item[0], LIGHTS_KEY: item[1]} for item in sorted_matched_holidays]

        return candidates

    def evaluate_holiday_lights_dates(self, evaluation_date):
        holiday_dates = dict()
        all_holidays = self.lights_data[HOLIDAYS_KEY]
        for holiday in all_holidays:
            holiday_dates[holiday] = dict()
            holiday_data = all_holidays[holiday]
            holiday_dates[holiday][START_DAY_OF_YEAR_KEY], holiday_dates[holiday][END_DAY_OF_YEAR_KEY] = \
                self.evaluate_holiday_dates(holiday_data, evaluation_date)
            holiday_dates[holiday][HOLIDAY_LIGHTS_KEY] = holiday_data[HOLIDAY_LIGHTS_KEY]

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

        day_of_year = self.calculate_day_of_year(evaluation_date, month, day)

        return day_of_year + sign * delta

    def calculate_day_of_year(self, evaluation_date: datetime, evaluation_month=None, evaluation_day=None):
        calc_date = calculate_date(evaluation_date, evaluation_day, evaluation_month)

        return calc_date.timetuple().tm_yday

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
        first_day_of_year = calculate_date(evaluation_date, 1, 1)
        frequency = get_frequency(holiday_rrule['frequency'])
        if BY_EASTER_KEY in holiday_rrule:
            holiday_date = self.interpret_easter_rrule(frequency, holiday_rrule[BY_EASTER_KEY], first_day_of_year)
        else:
            by_month = holiday_rrule['month']
            day_of_week = holiday_rrule['day_of_week']
            occurrence = holiday_rrule['occurrence']
            by_weekday = get_byweekday(day_of_week, occurrence)

            holiday_date = self.interpret_general_rrule(frequency, by_month, by_weekday, first_day_of_year)

        return holiday_date.timetuple().tm_yday

    def interpret_general_rrule(self, frequency, by_month, by_weekday, first_day_of_year):
        holiday_date = rrule(frequency, dtstart=first_day_of_year, count=1, bymonth=by_month, byweekday=by_weekday)

        return holiday_date[0]

    def interpret_easter_rrule(self, frequency, by_easter, first_day_of_year):
        holiday_date = rrule(frequency, dtstart=first_day_of_year, count=1, byeaster=by_easter)

        return holiday_date[0]

    def normalize_keys(self, lights_data: dict):
        holidays = lights_data[HOLIDAYS_KEY]
        new_holidays = dict()
        for key in holidays:
            new_key = self.normalize_name(key)
            if new_key != key:
                new_holidays[new_key] = holidays[key]

        holidays.update(new_holidays)

    def normalize_name(self, name: str):
        return re.sub(r"[^a-zA-Z0-9_]", '', name.lower().replace(" ", "_"))


if __name__ == '__main__':
    main(sys.argv[0], sys.argv[1:])
