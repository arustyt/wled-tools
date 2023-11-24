import argparse
import sys

from wled_utils.date_utils import get_todays_date_str
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
    definitions_dir = property_evaluator.get_property(env, section, DEFINITIONS_DIR_KEY)
    holidays_file = property_evaluator.get_property(env, section, HOLIDAYS_FILE_KEY)
    lights_file = property_evaluator.get_property(env, section, LIGHTS_FILE_KEY)
    default_lights_name = property_evaluator.get_property(env, section, DEFAULT_LIGHTS_NAME_KEY)
    wled_dir = property_evaluator.get_property(env, section, WLED_DIR_KEY)
    host = property_evaluator.get_property(env, section, HOST_KEY)

    if verbose:
        print()
        print("definitions_dir: " + str(definitions_dir))
        print("holidays_file: " + str(holidays_file))
        print("lights_file: " + str(lights_file))
        print("default_lights_name: " + str(default_lights_name))
        print("wled_dir: " + str(wled_dir))
        print("host: " + str(host))


#     wled_yaml2json.py --properties properties-all.yaml --env lab_300 --wled_dir . --presets presets-sunset.yaml,presets-halloween.yaml --definitions_dir ../../wled-tools/etc --suffix halloween

#../../wled-tools/src/main/python/wled_upload.py --host 192.168.196.11 --presets presets-sunset-halloween-lab_300.json


if __name__ == '__main__':
    main(sys.argv[0], sys.argv[1:])
