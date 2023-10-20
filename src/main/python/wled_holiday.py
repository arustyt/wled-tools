import argparse
import datetime
import re
import sys

from dateutil.relativedelta import *
from dateutil.easter import *
from dateutil.rrule import *
from dateutil.parser import *
from datetime import *

from wled_utils.path_utils import build_path
from wled_utils.rrule_utils import get_frequency, get_byweekday
from wled_utils.yaml_multi_file_loader import load_yaml_file

BY_EASTER_KEY = 'by_easter'

END_DAY_OF_YEAR_KEY = 'end_day_of_year'
ySTART_DAY_OF_YEAR_KEY = 'start_day_of_year'
START_DATE_KEY = 'start_date'
END_DATE_KEY = 'end_date'

HOLIDAYS_KEY = 'holidays'
NORMALIZED_HOLIDAYS_KEY = 'normalized_holidays'
DATE_FORMAT = '%Y-%m-%d'
YAML_EXTENSION = '.yaml'
INDENT = '  '
DEFAULT_DEFINITIONS_DIR = "../../../etc"
DEFAULT_HOLIDAYS_FILE = "holidays.yaml"
DEFAULT_LIGHTS_FILE = "holiday_lights.yaml"
DEFAULT_HOLIDAY_NAME = "normal"
DATE_KEY = 'date'
RRULE_KEY = 'rrule'
DAY_OF_YEAR_KEY = 'day_of_year'


def main(name, args):
    parser = argparse.ArgumentParser(
        description="Returns suffix for wled lights corresponding to provided date or today if none provided",
    )
    parser.add_argument("--definitions_dir", type=str,
                        help="Definition file location. Applies to holiday months and lights files. If not "
                             "specified, '" + DEFAULT_DEFINITIONS_DIR + "' is used.",
                        action="store", default=DEFAULT_DEFINITIONS_DIR)
    parser.add_argument("--holidays", type=str, help="Holiday definitions file name (YAML) relative to the "
                                                     "--definitions_dir directory. If not specified, '" +
                                                     DEFAULT_HOLIDAYS_FILE + "' is used.",
                        action="store", default=DEFAULT_HOLIDAYS_FILE)
    parser.add_argument("--lights", type=str, help="WLED holiday lights definitions file-name (YAML) relative to the "
                                                   "--definitions_dir directory. If not specified, '" +
                                                   DEFAULT_LIGHTS_FILE + "' is used.",
                        action="store", default=DEFAULT_LIGHTS_FILE)
    parser.add_argument("--default", type=str, help="WLED lights name that will be used if not a provided date is not "
                                                    "a holiday. If not specified, '" + DEFAULT_HOLIDAY_NAME +
                                                    "' is used.",
                        action="store", default=DEFAULT_HOLIDAY_NAME)
    parser.add_argument('--verbose', help="Intermediate output will be generated in addition to result output.",
                        action='store_true')

    parser.add_argument("date", type=str, help="Date (YYYY-MM-DD) for which holiday lights it to be evaluated. "
                                               "If not specified today's date is used.",
                        action="store", nargs='?', default=None)

    args = parser.parse_args()
    definitions_dir = args.definitions_dir
    holidays_file = args.months
    lights_file = args.lights
    verbose_mode = args.verbose
    default_lights_name = args.default
    date_str = args.date

    if verbose_mode:
        print("\nOPTION VALUES ...")
        print("  definitions_dir: " + definitions_dir)
        print("  holidays_file: " + holidays_file)
        print("  lights_file: " + lights_file)
        print("  date_str: " + str(date_str))

    if date_str is None:
        date_str = get_todays_date()

    try:
        evaluation_date = parse_date_string(date_str)
    except ValueError:
        raise ValueError("Invalid date format. Must be YYYY-MM-DD.")

    if verbose_mode:
        print("  date to process: " + str(evaluation_date))

    matched_holiday = evaluate_lights_for_date(definitions_dir=definitions_dir, holidays_file=holidays_file,
                                               lights_file=lights_file, evaluation_date=evaluation_date,
                                               default_lights_name=default_lights_name, verbose_mode=verbose_mode)

    print(matched_holiday)


def get_todays_date():
    return datetime.today().strftime(DATE_FORMAT)


def evaluate_lights_for_date(*, definitions_dir, holidays_file, lights_file, evaluation_date, default_lights_name,
                             verbose_mode):
    holidays_path = build_path(definitions_dir, holidays_file)
    holidays_data = load_yaml_file(holidays_path)
    evaluate_holidays(holidays_data, evaluation_date)

    lights_path = build_path(definitions_dir, lights_file)
    lights_data = load_yaml_file(lights_path)
    normalize_keys(lights_data)

    evaluation_month = str(evaluation_date.month)

    month_holidays = months_data[MONTHS_KEY][evaluation_month][NORMALIZED_HOLIDAYS_KEY]
    if verbose_mode:
        print(str(month_holidays))

    month_holiday_dates = generate_holiday_dates(lights_data, month_holidays, evaluation_date)
    evaluation_day_of_year = calculate_day_of_year(evaluation_date)
    matched_holiday = None
    min_range = None
    for holiday in month_holiday_dates:
        candidate_holiday = month_holiday_dates[holiday]
        start_day_of_year = candidate_holiday[START_DAY_OF_YEAR_KEY]
        end_day_of_year = candidate_holiday[END_DAY_OF_YEAR_KEY]
        if start_day_of_year <= evaluation_day_of_year <= end_day_of_year:
            range = end_day_of_year - start_day_of_year + 1
            if min_range is None or range < min_range:
                min_range = range
                matched_holiday = holiday

    return matched_holiday if matched_holiday is not None else default_lights_name


def generate_holiday_dates(lights_data, month_holidays, evaluation_date):
    holiday_dates = dict()
    all_holidays = lights_data[HOLIDAYS_KEY]
    for holiday in month_holidays:
        holiday_dates[holiday] = dict()
        holiday_dates[holiday][START_DAY_OF_YEAR_KEY], holiday_dates[holiday][END_DAY_OF_YEAR_KEY] = \
            get_holiday_dates(all_holidays[holiday], evaluation_date)

    return holiday_dates


def get_holiday_dates(holiday, evaluation_date):
    start_day_of_year = interpret_date_expr(holiday[START_DATE_KEY], evaluation_date)
    end_day_of_year = interpret_date_expr(holiday[END_DATE_KEY], evaluation_date)

    return start_day_of_year, end_day_of_year


def interpret_date_expr(date_expr, evaluation_date):
    if date_expr[0].isdigit():
        jdate = interpret_numeric_expr(date_expr, evaluation_date)
    else:
        jdate = interpret_placeholder_expr(date_expr, evaluation_date)
    return jdate


def interpret_numeric_expr(date_expr, evaluation_date):
    delta = 0
    expr_len = len(date_expr)
    if expr_len >= 4:
        month = int(date_expr[0:2])
        day = int(date_expr[2:4])
    else:
        raise ValueError('Date expression must be formatted, "MMDD[+/-delta].')

    sign = 1
    if expr_len > 4:
        if date_expr[4] == "+":
            sign = 1
        elif date_expr[4] == "-":
            sign = -1
        else:
            raise ValueError('Delta operator must be "+" or "-".')

        if expr_len > 5:
            delta = sign * int(date_expr[5:])
        else:
            raise ValueError('Date expression must be formatted, "MMDD[{+/-}delta].')

    jdate = calculate_day_of_year(evaluation_date, month, day)

    return jdate + delta


def calculate_day_of_year(evaluation_date: datetime, evaluation_month=None, evaluation_day=None):
    calc_date = calculate_date(evaluation_date, evaluation_day, evaluation_month)

    return calc_date.timetuple().tm_yday


def calculate_date(evaluation_date, evaluation_day, evaluation_month):
    evaluation_year = evaluation_date.year
    if evaluation_month is None:
        evaluation_month = evaluation_date.month
    if evaluation_day is None:
        evaluation_day = evaluation_date.day
    calc_date = datetime(evaluation_year, evaluation_month, evaluation_day)
    return calc_date


def evaluate_holidays(holidays_data: dict, evaluation_date):
    holidays = holidays_data[HOLIDAYS_KEY]
    for holiday_key in holidays:
        holiday = holidays[holiday_key]
        if DATE_KEY in holiday:
            holiday_day_of_year = interpret_numeric_expr(holiday[DATE_KEY], evaluation_date)
        elif RRULE_KEY in holiday:
            holiday_day_of_year = interpret_rrule(holiday[RRULE_KEY], evaluation_date)
        else:
            raise ValueError("Invalid holiday specification. Must include either {date} or {rrule}".format(date=DATE_KEY, rrule=RRULE_KEY))

        holiday[DAY_OF_YEAR_KEY] = holiday_day_of_year


def interpret_rrule(holiday_rrule: dict, evaluation_date):
    first_day_of_year = calculate_date(evaluation_date, 1, 1)
    frequency = get_frequency(rrule['frequency'])
    if BY_EASTER_KEY in rrule:
        holiday_date = interpret_easter_rrule(frequency, rrule[BY_EASTER_KEY], first_day_of_year)
    else:
        month = rrule['month']
        day_of_week = rrule['day_of_week']
        occurrence = rrule['occurrence']
        weekday = get_byweekday(day_of_week, occurrence)

        holiday_date = interpret_general_rrule(frequency, month, weekday, first_day_of_year)

    return holiday_date.timetuple().tm_yday


def interpret_general_rrule(frequency, month, weekday, evaluation_date):
    holiday_date = rrule(frequency, dtstart=test_date, count=1, bymonth=month, byweekday=weekday)

    return holiday_date


def interpret_easter_rrule(frequency, by_easter, evaluation_date):
    holiday_date = rrule(frequency, dtstart=test_date, count=1, byeaster=by_easter)

    return holiday_date


def normalize_keys(lights_data: dict):
    holidays = lights_data[HOLIDAYS_KEY]
    new_holidays = dict()
    for key in holidays:
        new_key = normalize_name(key)
        if new_key != key:
            new_holidays[new_key] = holidays[key]

    holidays.update(new_holidays)


def normalize_name(name: str):
    return re.sub(r"[^a-zA-Z0-9_]", '', name.lower().replace(" ", "_"))


def parse_date_string(date_str):
    return datetime.strptime(date_str, DATE_FORMAT)


if __name__ == '__main__':
    main(sys.argv[0], sys.argv[1:])
