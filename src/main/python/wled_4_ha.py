import argparse
import sys

from wled_utils.date_utils import get_todays_date_str
from wled_utils.dict_tools import get_env_property
from wled_utils.yaml_multi_file_loader import load_yaml_file

DEFINITIONS_DIR_KEY = "definitions_dir"
LIGHTS_FILE_KEY = "wled_holiday.lights_file"
DEFAULT_LIGHTS_NAME_KEY = "wled_holiday.default_lights_name"
HOLIDAYS_FILE_KEY = "wled_holiday.holidays_file"


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

    args = arg_parser.parse_args()
    job = args.job
    env = args.env
    date_str = args.date_str

    print("job: " + job)
    print("env: " + env)

    if date_str is None:
        date_str = get_todays_date_str()

    print("date_str: " + date_str)

    job_data = load_yaml_file(job)

    definitions_dir = get_env_property(env, DEFINITIONS_DIR_KEY, job_data)
    holidays_file = get_env_property(env, HOLIDAYS_FILE_KEY, job_data)
    lights_file = get_env_property(env, LIGHTS_FILE_KEY, job_data)
    default_lights_name = get_env_property(env, DEFAULT_LIGHTS_NAME_KEY, job_data)

    wled_dir = get_env_property(env, "wled_dir", job_data)







#     wled_yaml2json.py --properties properties-all.yaml --env lab_300 --wled_dir . --presets presets-sunset.yaml,presets-halloween.yaml --definitions_dir ../../wled-tools/etc --suffix halloween

#../../wled-tools/src/main/python/wled_upload.py --host 192.168.196.11 --presets presets-sunset-halloween-lab_300.json


if __name__ == '__main__':
    main(sys.argv[0], sys.argv[1:])
