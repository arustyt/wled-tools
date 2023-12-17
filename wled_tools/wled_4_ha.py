import argparse
import os
import sys

from wled_constants import WLED_HOLIDAY_KEY, DEFINITIONS_DIR_KEY, HOLIDAYS_FILE_KEY, LIGHTS_FILE_KEY, \
    DEFAULT_LIGHTS_NAME_KEY, HOST_KEY, WLED_DIR_KEY
from wled_holiday import WledHoliday
from wled_upload import upload
from wled_utils.date_utils import get_todays_date_str, parse_date_str
from wled_utils.logger_utils import get_logger, init_logger
from wled_utils.property_tools import PropertyEvaluator
from wled_utils.yaml_multi_file_loader import load_yaml_file
from wled_yaml2json import wled_yaml2json

PROD_MODE = False
TEST_MODE = True
QUIET_MODE = True

PROPERTIES_FILE_KEY = "properties"

# wled_f_ha.py job_file env [date_str]


def main(name, args):
    arg_parser = argparse.ArgumentParser(
        description="Determines and uploads appropriate lights based on env and date_str",
    )
    arg_parser.add_argument("job_file", type=str,
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
    arg_parser.add_argument('--log_dir', help="Directory where log file will be located.",
                            action='store_true')

    args = arg_parser.parse_args()
    job_file = args.job_file
    env = args.env
    date_str = args.date_str
    verbose = args.verbose

    init_logger()

    process_successful = wled_4_ha(job_file=job_file, env=env, date_str=date_str, verbose=verbose)

    return 0 if process_successful else 1


def wled_4_ha(*, job_file, env, date_str=None, verbose=False):
    process_successful = False
    try:
        if date_str is None:
            date_str = get_todays_date_str()

        if verbose:
            get_logger().info("job_file: " + job_file)
            get_logger().info("env: " + env)
            get_logger().info("date_str: " + date_str)

        data_dir = os.path.dirname(job_file)
        if data_dir is None or len(data_dir) == 0:
            data_dir = '.'
        job_data = load_yaml_file(job_file)
        property_evaluator = PropertyEvaluator(job_data, False)
        section = WLED_HOLIDAY_KEY
        definitions_rel_dir = property_evaluator.get_property(env, section, DEFINITIONS_DIR_KEY)
        holidays_file = property_evaluator.get_property(env, section, HOLIDAYS_FILE_KEY)
        lights_file = property_evaluator.get_property(env, section, LIGHTS_FILE_KEY)
        default_lights_name = property_evaluator.get_property(env, section, DEFAULT_LIGHTS_NAME_KEY)
        host = property_evaluator.get_property(env, section, HOST_KEY)
        wled_rel_dir = property_evaluator.get_property(env, section, WLED_DIR_KEY)

#        wled_dir = "{base}/{rel_dir}".format(base=data_dir, rel_dir=wled_rel_dir)
#        definitions_dir = "{base}/{rel_dir}".format(base=data_dir, rel_dir=definitions_rel_dir)


        if verbose:
            get_logger().info("data_dir: " + str(data_dir))
            get_logger().info("definitions_rel_dir: " + str(definitions_rel_dir))
            get_logger().info("holidays_file: " + str(holidays_file))
            get_logger().info("lights_file: " + str(lights_file))
            get_logger().info("default_lights_name: " + str(default_lights_name))
            get_logger().info("wled_rel_dir: " + str(wled_rel_dir))
            get_logger().info("host: " + str(host))

        evaluation_date = parse_date_str(date_str)

        wled_lights = WledHoliday(data_dir=data_dir, definitions_rel_dir=definitions_rel_dir, holidays_file=holidays_file,
                                  lights_file=lights_file, evaluation_date=evaluation_date,
                                  default_lights_name=default_lights_name, verbose_mode=verbose)
        matched_holiday = wled_lights.evaluate_lights_for_date(evaluation_date=evaluation_date)

        if verbose:
            get_logger().info("matched_holiday: " + str(matched_holiday))

        properties_file = property_evaluator.get_property(env, section, PROPERTIES_FILE_KEY)
        presets_file = build_presets_option(matched_holiday)

        if verbose:
            get_logger().info("Testing presets generation to determine JSON file name.")

        presets_json_path = test_presets(data_dir, definitions_rel_dir, env, matched_holiday, presets_file,
                                         properties_file, wled_rel_dir, False)

        if need_to_generate_presets(data_dir, wled_rel_dir, matched_holiday, presets_json_path):
            if verbose:
                get_logger().info("Generating presets file: {file}".format(file=presets_json_path))
            presets_json_path = generate_presets(data_dir, definitions_rel_dir, env, matched_holiday, presets_file,
                                                 properties_file, wled_rel_dir, verbose)
        else:
            if verbose:
                get_logger().info("{file} is up-to-date.".format(file=presets_json_path))

        process_successful = upload_presets(host, presets_json_path, verbose)
    except Exception as ex:
        if verbose:
            get_logger().error(ex)
    return process_successful


def test_presets(data_dir, definitions_rel_dir, env, matched_holiday, presets_file, properties_file, wled_rel_dir,
                 verbose: bool):
    presets_json_path, cfg_json_path = wled_yaml2json(data_dir=data_dir,
                                                      wled_rel_dir=wled_rel_dir,
                                                      environment=env,
                                                      properties=properties_file,
                                                      presets=presets_file,
                                                      definitions_rel_dir=definitions_rel_dir,
                                                      suffix="-{holiday}".format(holiday=matched_holiday),
                                                      test_mode=TEST_MODE,
                                                      quiet_mode=not verbose)
    return presets_json_path


def upload_presets(host, presets_json_path, verbose):
    if verbose:
        get_logger().info("Uploading presets file ... ")
    upload_successful = upload(host=host, presets_file=presets_json_path)
    if verbose:
        if upload_successful:
            get_logger().info("SUCCESSFUL")
        else:
            get_logger().info("FAILED")

    return upload_successful


def generate_presets(data_dir, definitions_rel_dir, env, matched_holiday, presets_file, properties_file, wled_rel_dir,
                     verbose):
    presets_json_path, cfg_json_path = wled_yaml2json(data_dir=data_dir,
                                                      wled_rel_dir=wled_rel_dir,
                                                      environment=env,
                                                      properties=properties_file,
                                                      presets=presets_file,
                                                      definitions_rel_dir=definitions_rel_dir,
                                                      suffix="-{holiday}".format(holiday=matched_holiday),
                                                      test_mode=PROD_MODE,
                                                      quiet_mode=not verbose)
    if verbose:
        get_logger().info("presets_json_path: " + str(presets_json_path))
        get_logger().info("cfg_json_path: " + str(cfg_json_path))

    return presets_json_path


def build_presets_option(holiday):
    presets_files = get_presets_files(holiday)
    return ",".join(presets_files)


def get_presets_files(holiday):
    return ["presets-sunset.yaml", "presets-{holiday}.yaml".format(holiday=holiday)]


def need_to_generate_presets(data_dir, wled_rel_dir, holiday, presets_json):
    presets_files = get_presets_files(holiday)
    presets_paths = []

    wled_dir = "{base}/{rel_dir}".format(base=data_dir, rel_dir=wled_rel_dir)

    for presets_yaml in presets_files:
        presets_path = "{dir}/{file}".format(dir=wled_dir, file=presets_yaml)
        presets_paths.append(presets_path)
        if not os.path.exists(presets_path):
            raise ValueError('File "{path}" does not exist.'.format(path=presets_path))

    if not os.path.exists(presets_json):
        return True

    presets_json_mtime = os.stat(presets_json).st_mtime

    for presets_yaml in presets_paths:
        presets_yaml_mtime = os.stat(presets_yaml).st_mtime
        if presets_json_mtime <= presets_yaml_mtime:
            return True

    return False


if __name__ == '__main__':
    result = main(sys.argv[0], sys.argv[1:])
    exit(result)
