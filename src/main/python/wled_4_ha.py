import argparse
import sys

from wled_holiday import WledHoliday
from wled_upload import upload
from wled_utils.date_utils import get_todays_date_str, parse_date_str
from wled_utils.property_tools import PropertyEvaluator
from wled_utils.yaml_multi_file_loader import load_yaml_file
from wled_yaml2json import wled_yaml2json

TEST_MODE = False

PROPERTIES_FILE_KEY = "properties"

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
    host = property_evaluator.get_property(env, section, HOST_KEY)
    wled_dir = property_evaluator.get_property(env, section, WLED_DIR_KEY)

    if verbose:
        print()
        print("definitions_dir: " + str(definitions_dir))
        print("holidays_file: " + str(holidays_file))
        print("lights_file: " + str(lights_file))
        print("default_lights_name: " + str(default_lights_name))
        print("wled_dir: " + str(wled_dir))
        print("host: " + str(host))

    evaluation_date = parse_date_str(date_str)

    wled_lights = WledHoliday(definitions_dir=definitions_dir, holidays_file=holidays_file,
                              lights_file=lights_file, evaluation_date=evaluation_date,
                              default_lights_name=default_lights_name, verbose_mode=verbose)
    matched_holiday = wled_lights.evaluate_lights_for_date(evaluation_date=evaluation_date)

    if verbose:
        print("\nmatched_holiday: " + str(matched_holiday))

    properties_file = property_evaluator.get_property(env, section, PROPERTIES_FILE_KEY)
    presets_file = build_presets_option(matched_holiday)

    presets_json_path, cfg_json_path = wled_yaml2json(wled_dir=wled_dir,
                                                      environment=env,
                                                      properties=properties_file,
                                                      presets=presets_file,
                                                      definitions_dir=definitions_dir,
                                                      suffix="-{holiday}".format(holiday=matched_holiday),
                                                      test_mode=TEST_MODE)

    if verbose:
        print("\npresets_json_path: " + str(presets_json_path))
        print("cfg_json_path: " + str(cfg_json_path))

    file_uploaded = upload(host=host, presets_file=presets_json_path)

    if verbose:
        if file_uploaded:
            print("\nFile upload successful.")
        else:
           print("\nFile upload failed.")


def build_presets_option(matched_holiday):
    return "presets-sunset.yaml,presets-{holiday}.yaml".format(holiday=matched_holiday)


if __name__ == '__main__':
    main(sys.argv[0], sys.argv[1:])
