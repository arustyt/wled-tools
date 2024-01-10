import os
from pathlib import Path

from wled_constants import LIGHTS_KEY, HOLIDAY_KEY

YAML_EXTENSION = '.yaml'


def build_path(directory, file):
    return "{dir}/{file}".format(dir=directory, file=file) if file is not None and len(file) > 0 else None


def get_presets_file_name(day_type):
    return "presets-{day_type}.yaml".format(day_type=day_type)


def get_wled_path(data_dir, wled_rel_dir, presets_yaml):
    return "{base}/{rel_dir}/{file}".format(base=data_dir, rel_dir=wled_rel_dir, file=presets_yaml)


def choose_existing_presets(base_dir, sub_dir, candidates):
    for candidate in candidates:
        if presets_file_exists(base_dir, sub_dir, candidate[LIGHTS_KEY]):
            return candidate

    return {HOLIDAY_KEY: None, LIGHTS_KEY: None}


def presets_file_exists(data_dir, wled_rel_dir, day_type):
    day_presets_file = get_presets_file_name(day_type)
    day_presets_path = get_wled_path(data_dir, wled_rel_dir, day_presets_file)
    path_exists = os.path.exists(day_presets_path)
    return path_exists


def find_path_list(directory: str, environment: str, files_str: str, file_base: str):
    paths = []
    if files_str is not None and len(files_str) > 0:
        for file_nickname in files_str.split(','):
            path = find_path(directory, environment, file_nickname, file_base)
            if path is not None:
                paths.append(path)

    return paths


def find_path(directory: str, environment: str, file_nickname: str, file_base: str):
    candidates = get_file_name_candidates(environment, file_nickname, file_base)

    if len(candidates) == 0:
        raise ValueError("No candidates found for '{base}' file.".format(base=file_base))

    for candidate in candidates:
        file_path = "{dir}/{file}".format(dir=directory, file=candidate) if len(candidate) > 0 else None
        if file_path is not None:
            path = Path(file_path)
            if path.is_file():
                return file_path

    raise ValueError("None of the candidate files exist: '{candidates}'.".format(candidates=str(candidates)))


def get_file_name_candidates(environment: str, file_option: str, file_base: str):
    candidates = []
    if file_option is not None and file_option.endswith(YAML_EXTENSION):
        candidates.append(file_option)
    else:
        if file_option is not None:
            add_file_option_candidates(candidates, file_option, environment)
        else:
            add_file_option_candidates(candidates, file_base, environment)

    return candidates


def add_file_option_candidates(candidates, file_option, environment):
    if file_option is not None:
        if environment is not None:
            file_name = "{file_option}-{env}.yaml".format(file_option=file_option, env=environment)
            if file_name not in candidates:
                candidates.append(file_name)

        file_name = "{file_option}.yaml".format(file_option=file_option)
        if file_name not in candidates:
            candidates.append("{file_option}.yaml".format(file_option=file_option))
