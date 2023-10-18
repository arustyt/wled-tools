import argparse
import re
import sys

from dateutil.relativedelta import *
from dateutil.easter import *
from dateutil.rrule import *
from dateutil.parser import *
from datetime import *

from wled_utils.path_utils import build_path
from wled_utils.yaml_multi_file_loader import load_yaml_file

MONTHS_KEY = 'months'
HOLIDAYS_KEY = 'holidays'
DATE_FORMAT = '%Y-%m-%d'
YAML_EXTENSION = '.yaml'
INDENT = '  '
DEFAULT_DEFINITIONS_DIR = "../../../etc"
DEFAULT_MONTHS_FILE = "holiday_months.yaml"
DEFAULT_LIGHTS_FILE = "holiday_lights.yaml"


def main(name, args):
    parser = argparse.ArgumentParser(
        description="Returns suffix for wled lights corresponding to provided date or today if none provided",
    )
    parser.add_argument("--definitions_dir", type=str,
                        help="Definition file location. Applies to holiday months and lights files. If not "
                             "specified, '" + DEFAULT_DEFINITIONS_DIR + "' is used.",
                        action="store", default=DEFAULT_DEFINITIONS_DIR)
    parser.add_argument("--months", type=str, help="WLED holiday months definition file name (YAML) relative to the "
                                                   "--definitions_dir directory. If not specified, '" +
                                                   DEFAULT_MONTHS_FILE + "' is used.",
                        action="store", default=DEFAULT_MONTHS_FILE)
    parser.add_argument("--lights", type=str, help="WLED holiday lights definitions file-name (YAML) relative to the "
                                                   "--definitions_dir directory. If not specified, '" +
                                                   DEFAULT_LIGHTS_FILE + "' is used.",
                        action="store", default=DEFAULT_LIGHTS_FILE)
    parser.add_argument('--verbose', help="Intermediate output will be generated in addition to result output.",
                        action='store_true')

    parser.add_argument("date", type=str, help="Date (YYYY-MM-DD) for which holiday lights it to be evaluated. "
                                               "If not specified today's date is used.",
                        action="store", nargs='?', default=None)

    args = parser.parse_args()
    definitions_dir = args.definitions_dir
    months_file = args.months
    lights_file = args.lights
    verbose_mode = args.verbose
    date_str = args.date

    if verbose_mode:
        print("\nOPTION VALUES ...")
        print("  definitions_dir: " + definitions_dir)
        print("  months_file: " + months_file)
        print("  lights_file: " + lights_file)
        print("  date_str: " + str(date_str))

    if date_str is None:
        date_str = get_todays_date()

    try:
        processing_date = parse_date_string(date_str)
    except ValueError:
        if verbose_mode:
            print("Invalid date format. Must be YYYY-MM-DD.")
        quit(1)

    if verbose_mode:
        print("  date to process: " + str(processing_date))

    evaluate_lights_for_date(definitions_dir=definitions_dir, months_file=months_file, lights_file=lights_file,
                             processing_date=processing_date, verbose_mode=verbose_mode)


def get_todays_date():
    return datetime.today().strftime(DATE_FORMAT)


def evaluate_lights_for_date(*, definitions_dir, months_file, lights_file, processing_date, verbose_mode):
    months_path = build_path(definitions_dir, months_file)
    months_data = load_yaml_file(months_path)

    lights_path = build_path(definitions_dir, lights_file)
    lights_data = load_yaml_file(lights_path)
    normalize_keys(lights_data)

    processing_month = str(processing_date.month)

    holidays = months_data[MONTHS_KEY][processing_month][HOLIDAYS_KEY]
    if verbose_mode:
        print(str(holidays))

    holidays_data = prepare_holidays_data(lights_data, holidays)

    for holiday in holidays:
        holiday_normalized = normalize_name(holiday)
        if verbose_mode:
            print(holiday_normalized)
        if holiday_normalized in lights_data[HOLIDAYS_KEY]:
            if verbose_mode:
                print("Found {holiday_norm}, a.k.a. {holiday}".format(holiday_norm=holiday_normalized, holiday=holiday))

            break

    pass


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
