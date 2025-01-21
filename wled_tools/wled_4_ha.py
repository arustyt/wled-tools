import argparse
import os
import sys

from wled_configuration import WledConfiguration
from wled_constants import WLED_HOLIDAY_KEY, DEFINITIONS_DIR_KEY, HOLIDAYS_FILE_KEY, HOLIDAY_PRESETS_FILE_KEY, \
    DEFAULT_PRESETS_NAME_KEY, HOST_KEY, WLED_DIR_KEY, DEFAULT_HOLIDAY_NAME_KEY, PRESETS_KEY, HOLIDAY_KEY, \
    RESULT_KEY, CANDIDATES_KEY
from wled_holiday import WledHoliday
from wled_upload import upload
from wled_utils.date_utils import get_todays_date_str, parse_date_str
from wled_utils.logger_utils import get_logger, init_logger
from wled_utils.path_utils import presets_file_exists, get_presets_file_name, choose_existing_presets
from wled_utils.property_tools import PropertyEvaluator
from wled_utils.yaml_multi_file_loader import load_yaml_file
from wled_yaml2json import wled_yaml2json

DEFAULT_STARTING_PRESETS_FILE = "presets-sunset.yaml"

PROD_MODE = False
TEST_MODE = True
QUIET_MODE = True

PROPERTIES_FILE_KEY = "properties"
SEGMENTS_FILE_KEY = "segments"
STARTING_PRESETS_FILE_KEY = "starting_presets_file"


# wled_f_ha.py job_file env [date_str]


def main(name, args):
    arg_parser = argparse.ArgumentParser(
        description="Determines and uploads appropriate presets based on env and date_str",
    )
    arg_parser.add_argument("job_file", type=str,
                            help="Job YAML file defining details of job to be executed.",
                            action="store")
    arg_parser.add_argument("env", type=str,
                            help="Environment to be used for job execution.",
                            action="store")
    arg_parser.add_argument("date_str", type=str, help="Date (YYYY-MM-DD) for which holiday presets it to "
                                                       "be evaluated. If not specified, today's date is used.",
                            action="store", default=None, nargs='?')
    arg_parser.add_argument("--presets", type=str,
                            help="Override of presets to be used for job execution.",
                            action="store")
    arg_parser.add_argument("--holiday", type=str,
                            help="Override of holiday to be used for job execution.",
                            action="store")
    arg_parser.add_argument('--verbose', help="Intermediate output will be generated in addition to result output.",
                            action='store_true')
    arg_parser.add_argument('--log_dir', help="Directory where log file will be located.",
                            action='store_true')

    args = arg_parser.parse_args()
    job_file = args.job_file
    env = args.env
    presets_override = args.presets
    holiday_override = args.holiday
    date_str = args.date_str
    verbose = args.verbose

    init_logger()

    wled_4_ha_result = wled_4_ha(job_file=job_file, env=env, date_str=date_str, verbose=verbose,
                                   presets_override=presets_override, holiday_override=holiday_override)
    process_successful = wled_4_ha_result[RESULT_KEY]
    return 0 if process_successful else 1


def wled_4_ha(*, job_file, env, date_str=None, verbose=False, presets_override=None, holiday_override=None,
              holidays_only=False):
    candidates = None
    holiday_name = None
    presets = None
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
        property_evaluator = PropertyEvaluator(job_data, verbose=False, strings_only=True)
        section = WLED_HOLIDAY_KEY
        definitions_rel_dir = property_evaluator.get_property(env, section, DEFINITIONS_DIR_KEY)
        holidays_file = property_evaluator.get_property(env, section, HOLIDAYS_FILE_KEY)
        holiday_presets_file = property_evaluator.get_property(env, section, HOLIDAY_PRESETS_FILE_KEY)
        default_holiday_presets_name = property_evaluator.get_property(env, section, DEFAULT_PRESETS_NAME_KEY)
        default_holiday_name = property_evaluator.get_property(env, section, DEFAULT_HOLIDAY_NAME_KEY)
        host = property_evaluator.get_property(env, section, HOST_KEY)
        wled_rel_dir = property_evaluator.get_property(env, section, WLED_DIR_KEY)
        starting_presets_file = property_evaluator.get_property(env, section, STARTING_PRESETS_FILE_KEY)
        if starting_presets_file is None:
            starting_presets_file = DEFAULT_STARTING_PRESETS_FILE

        if verbose:
            get_logger().info("data_dir: " + str(data_dir))
            get_logger().info("definitions_rel_dir: " + str(definitions_rel_dir))
            get_logger().info("holidays_file: " + str(holidays_file))
            get_logger().info("holiday_presets_file: " + str(holiday_presets_file))
            get_logger().info("default_holiday_presets_name: " + str(default_holiday_presets_name))
            get_logger().info("wled_rel_dir: " + str(wled_rel_dir))
            get_logger().info("host: " + str(host))
            get_logger().info("starting_presets_file: " + str(starting_presets_file))

        evaluation_date = parse_date_str(date_str)

        wled_presets = WledHoliday(data_dir=data_dir, definitions_rel_dir=definitions_rel_dir,
                                   holidays_file=holidays_file, holiday_presets_file=holiday_presets_file,
                                   evaluation_date=evaluation_date,
                                   verbose_mode=verbose)
        presets = default_holiday_presets_name
        holiday_name = default_holiday_name
        candidates = wled_presets.evaluate_presets_for_date(evaluation_date=evaluation_date)
        if len(candidates) > 0:
            matched_candidate = choose_existing_presets(data_dir, wled_rel_dir, candidates)
            if matched_candidate is None:
                if verbose:
                    get_logger().info("Date is not a recognized holiday.")
            elif PRESETS_KEY not in matched_candidate or matched_candidate[PRESETS_KEY] is None:
                if verbose:
                    get_logger().info('No candidate presets exist for {candidates}.'.format(
                        candidates=[item[HOLIDAY_KEY] for item in candidates]))
            elif not presets_file_exists(data_dir, wled_rel_dir, matched_candidate[PRESETS_KEY]):
                if verbose:
                    get_logger().info(
                        'Presets file for "{presets}" does not exist.'.format(presets=matched_candidate[PRESETS_KEY]))
            else:
                presets = matched_candidate[PRESETS_KEY]
                holiday_name = matched_candidate[HOLIDAY_KEY]

        if presets_override is not None:
            presets = presets_override

        if holiday_override is not None:
            holiday_name = holiday_override

        if not holidays_only:
            process_successful = install_holiday_lights(data_dir=data_dir, definitions_rel_dir=definitions_rel_dir,
                                                        env=env, holiday_name=holiday_name, host=host,
                                                        job_file=job_file, presets=presets,
                                                        property_evaluator=property_evaluator,
                                                        section=section, starting_presets_file=starting_presets_file,
                                                        verbose=verbose, wled_rel_dir=wled_rel_dir)
        else:
            process_successful = True
    except Exception as ex:
        if verbose:
            get_logger().error(ex)
        process_successful = False

    if verbose:
        if process_successful:
            get_logger().info("WLED_4_HA SUCCESSFUL")
        else:
            get_logger().error("WLED_4_HA FAILED")
    return {RESULT_KEY: process_successful, CANDIDATES_KEY: candidates, HOLIDAY_KEY: holiday_name, PRESETS_KEY: presets}


def install_holiday_lights(*, data_dir, definitions_rel_dir, env, holiday_name, host, job_file, presets,
                           property_evaluator, section, starting_presets_file, verbose,
                           wled_rel_dir):
    if verbose:
        get_logger().info("Holiday: " + str(holiday_name))
        get_logger().info("Presets to be applied: " + str(presets))
    properties_file = property_evaluator.get_property(env, section, PROPERTIES_FILE_KEY)
    segments_file = property_evaluator.get_property(env, section, SEGMENTS_FILE_KEY)
    property_definitions = get_property_definitions(holiday_name, presets)
    if verbose:
        get_logger().info("Testing presets generation to determine JSON file name.")
    configuration = WledConfiguration(data_dir, wled_rel_dir, definitions_rel_dir, env,
                                      properties_file, segments_file)
    presets_file = build_presets_option(starting_presets_file, presets)
    presets_json_path, cfg_json_path = evaluate_presets(configuration, holiday_name, presets_file,
                                                        property_definitions, False, TEST_MODE)
    if need_to_generate_presets(job_file, configuration, starting_presets_file, presets, presets_json_path):
        if verbose:
            get_logger().info("Generating presets file: {file}".format(file=presets_json_path))
        presets_json_path, cfg_json_path = evaluate_presets(configuration, holiday_name, presets_file,
                                                            property_definitions, verbose, PROD_MODE)
    else:
        if verbose:
            get_logger().info("{file} is up-to-date.".format(file=presets_json_path))
    process_successful = upload_presets(host, presets_json_path, verbose)
    return process_successful


def get_property_definitions(holiday_name: str, matched_presets: str):
    properties = []
    if holiday_name is not None:
        properties.append('holiday=' + holiday_name)

    if matched_presets is not None:
        properties.append('presets=' + matched_presets)

    return properties


def evaluate_presets(configuration, holiday_name, presets_file, property_definitions, verbose: bool, test_mode: bool):
    presets_json_path, cfg_json_path = wled_yaml2json(data_dir=configuration.data_dir,
                                                      wled_rel_dir=configuration.wled_rel_dir,
                                                      environment=configuration.environment,
                                                      properties=configuration.properties_file,
                                                      segments=configuration.segments_file,
                                                      definitions_rel_dir=configuration.definitions_rel_dir,
                                                      presets=presets_file,
                                                      property_definitions=property_definitions,
                                                      suffix="-{holiday}".format(holiday=holiday_name),
                                                      test_mode=test_mode,
                                                      quiet_mode=not verbose)

    if verbose and test_mode == PROD_MODE:
        get_logger().info("presets_json_path: " + str(presets_json_path))
        get_logger().info("cfg_json_path: " + str(cfg_json_path))

    return presets_json_path, cfg_json_path


def upload_presets(host, presets_json_path, verbose):
    if verbose:
        get_logger().info("Uploading presets file ... ")
    upload_successful = upload(host=host, presets_file=presets_json_path)
    if verbose:
        if upload_successful:
            get_logger().info("UPLOAD SUCCESSFUL")
        else:
            get_logger().error("UPLOAD FAILED")

    return upload_successful


def build_presets_option(starting_presets_file, holiday):
    presets_files = get_presets_files(starting_presets_file, holiday)
    return ",".join(presets_files)


def get_presets_files(starting_presets_file, holiday_presets):
    return [starting_presets_file, get_presets_file_name(holiday_presets)]


def need_to_generate_presets(job_file, configuration: WledConfiguration, starting_presets_file, holiday, presets_json):
    presets_files = get_presets_files(starting_presets_file, holiday)
    presets_paths = []

    add_path_to_list(presets_paths, job_file)
    add_path_to_list(presets_paths, configuration.properties_path)
    add_path_to_list(presets_paths, configuration.segments_path)
    add_path_to_list(presets_paths, configuration.effects_path)
    add_path_to_list(presets_paths, configuration.palettes_path)
    add_path_to_list(presets_paths, configuration.colors_path)

    wled_dir = configuration.wled_dir

    for presets_yaml in presets_files:
        presets_path = "{dir}/{file}".format(dir=wled_dir, file=presets_yaml)
        add_path_to_list(presets_paths, presets_path)

    if not os.path.exists(presets_json):
        return True

    presets_json_mtime = os.stat(presets_json).st_mtime

    for presets_yaml in presets_paths:
        presets_yaml_mtime = os.stat(presets_yaml).st_mtime
        if presets_json_mtime <= presets_yaml_mtime:
            return True

    return False


def add_path_to_list(presets_paths, presets_path):
    presets_paths.append(presets_path)
    if not os.path.exists(presets_path):
        raise ValueError('File "{path}" does not exist.'.format(path=presets_path))


if __name__ == '__main__':
    result = main(sys.argv[0], sys.argv[1:])
    exit(result)
