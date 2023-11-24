import argparse
import sys

from wled_holiday import WledHoliday
from wled_utils.date_utils import get_todays_date_str, parse_date_str
from wled_utils.property_tools import PropertyEvaluator
from wled_utils.yaml_multi_file_loader import load_yaml_file

HOST_KEY = "host"

WLED_HOLIDAY_KEY = "wled_holiday"
WLED_YAML2JSON_KEY = "wled_yaml2json"
WLED_UPLOAD_KEY = "wled_upload"

WLED_DIR_KEY = "wled_dir"

DEFINITIONS_DIR_KEY = "definitions_dir"
LIGHTS_FILE_KEY = "lights_file"
DEFAULT_LIGHTS_NAME_KEY = "default_lights_name"
HOLIDAYS_FILE_KEY = "holidays_file"


# wled_f_ha.py job_file env [date_str]
def main(name, args):
    arg_parser = argparse.ArgumentParser(
        description="Determines and uploads appropriate lights based on env and date_str",
    )
    arg_parser.add_argument("job", type=str,
                            help="Job YAML file defining details of job to be executed.",
                            action="store")
    arg_parser.add_argument("env", type=str,
                            help="Environment to be used for job execution.",
                            action="store")
    arg_parser.add_argument("date_str", type=str, help="Date (YYYY-MM-DD) for which holiday lights it to be evaluated. "
                                                       "If not specified, today's date is used.",
                            action="store", default=None, nargs='?')
    arg_parser.add_argument('--verbose', help="Intermediate output will be generated in addition to result output.",
                            action='store_true')

    args = arg_parser.parse_args()
    job = args.job
    env = args.env
    date_str = args.date_str
    verbose = args.verbose

    if date_str is None:
        date_str = get_todays_date_str()

    if verbose:
        print()
        print("job: " + job)
        print("env: " + env)
        print("date_str: " + date_str)

    job_data = load_yaml_file(job)
    property_evaluator = PropertyEvaluator(job_data, False)
    section = WLED_HOLIDAY_KEY
    definitions_dir_tuple = property_evaluator.get_property(env, section, DEFINITIONS_DIR_KEY)
    holidays_file_tuple = property_evaluator.get_property(env, section, HOLIDAYS_FILE_KEY)
    lights_file_tuple = property_evaluator.get_property(env, section, LIGHTS_FILE_KEY)
    default_lights_name_tuple = property_evaluator.get_property(env, section, DEFAULT_LIGHTS_NAME_KEY)
    wled_dir_tuple = property_evaluator.get_property(env, section, WLED_DIR_KEY)
    host_tuple = property_evaluator.get_property(env, section, HOST_KEY)

    if verbose:
        print()
        print("definitions_dir_tuple: " + str(definitions_dir_tuple))
        print("holidays_file_tuple: " + str(holidays_file_tuple))
        print("lights_file_tuple: " + str(lights_file_tuple))
        print("default_lights_name_tuple: " + str(default_lights_name_tuple))
        print("wled_dir_tuple: " + str(wled_dir_tuple))
        print("host_tuple: " + str(host_tuple))

    evaluation_date = parse_date_str(date_str)

    wled_lights = WledHoliday(definitions_dir=definitions_dir_tuple[0], holidays_file=holidays_file_tuple[0],
                              lights_file=lights_file_tuple[0], evaluation_date=evaluation_date,
                              default_lights_name=default_lights_name_tuple[0], verbose_mode=verbose)
    matched_holiday = wled_lights.evaluate_lights_for_date(evaluation_date=evaluation_date)
    print(matched_holiday)


#     wled_yaml2json.py --properties properties-all.yaml --env lab_300 --wled_dir . --presets presets-sunset.yaml,presets-halloween.yaml --definitions_dir ../../wled-tools/etc --suffix halloween

# ../../wled-tools/src/main/python/wled_upload.py --host 192.168.196.11 --presets presets-sunset-halloween-lab_300.json


if __name__ == '__main__':
    main(sys.argv[0], sys.argv[1:])
