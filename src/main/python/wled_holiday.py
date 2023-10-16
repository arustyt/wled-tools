import argparse
import sys

from dateutil.relativedelta import *
from dateutil.easter import *
from dateutil.rrule import *
from dateutil.parser import *
from datetime import *

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
    parser.add_argument("date", type=str, help="Date (YYYY-MM-DD) for which holiday lights it to be evaluated. "
                                               "If not specified today's date is used.",
                        action="store", nargs='?', default=None)

    args = parser.parse_args()
    definitions_dir = args.definitions_dir
    months_file = args.months
    lights_file = args.lights
    date_str = args.date

    print("\nOPTION VALUES ...")
    print("  definitions_dir: " + definitions_dir)
    print("  months_file: " + months_file)
    print("  lights_file: " + lights_file)
    print("  date_str: " + str(date_str))

    if date_str is None:
        date_str = get_todays_date()

    print("  date to process: " + str(date_str))

    evaluate_lights_for_date(definitions_dir=definitions_dir, months_file=months_file, lights_file=lights_file,
                             date_str=date_str)


def get_todays_date():
    return datetime.today().strftime('%Y-%m-%d')


def evaluate_lights_for_date(*, definitions_dir, months_file, lights_file, date_str):
    pass


if __name__ == '__main__':
    main(sys.argv[0], sys.argv[1:])
