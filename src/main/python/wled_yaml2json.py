import argparse
import json
import os
import sys
from os.path import exists
from pathlib import Path

import yaml

from presets_exclude_filter import PresetsExcludeFilter
from presets_include_filter import PresetsIncludeFilter
from wled_cfg import WledCfg
from wled_placeholder_replacer import WledPlaceholderReplacer
from wled_presets import WledPresets
from yaml_multi_file_loader import load_yaml_files, load_yaml_file

YAML_EXTENSION = '.yaml'

DEFAULT_DEFINITIONS_DIR = "../../../etc"
DEFAULT_WLED_DIR = "."
DEFAULT_COLORS_FILE = "colors.yaml"
DEFAULT_PALETTES_FILE = "palettes.yaml"
DEFAULT_EFFECTS_FILE = "effects.yaml"
DEFAULT_SEGMENTS_FILE_BASE = "segments"
DEFAULT_PRESETS_FILE_BASE = "presets"
DEFAULT_PROPERTIES_FILE_BASE = "properties"
DEFAULT_ENVIRONMENT = None
DEFAULT_CFG_FILE = "cfg"
ENVIRONMENTS = ['lab_300', 'lab_50', 'roof', 'trailer']

FILE_NAME_OPTIONS = ("   env     file     file\n"
                     "  option   option   option ends\n"
                     "  present  present  with .yaml\n"
                     "  =======  =======  ===========\n"
                     "     Y        Y         N        <file option value>-<env option value>.yaml\n"
                     "     N        Y         N        <file option value>.yaml\n"
                     "     *        Y         Y        <file option value>\n"
                     "     Y        N         N        <default file base>-<env option value>.yaml\n"
                     "     N        N         N        <default file base>.yaml\n")


def main(name, args):
    parser = argparse.ArgumentParser(
        description="Convert YAML files to WLED JSON.  The names of files located in --wled_dir \n"
                    "(--properties, --segments, --presets, and --cfg) follow these rules to\n"
                    "determine the file name.\n" +
                    FILE_NAME_OPTIONS,
        # formatter_class=argparse.RawTextHelpFormatter
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--wled_dir", type=str,
                        help="WLED data file location. Applies to presets, cfg, and segments files. If not specified, "
                             "'" + DEFAULT_WLED_DIR + "' is used.",
                        action="store", default=DEFAULT_WLED_DIR)
    parser.add_argument("--env", type=str, help="The name of the environment for this execution.  Currently recognized "
                                                "environments are: {environments}. The environment name is used to "
                                                "construct file names for properties, presets, segments, and cfg "
                                                "files per the rules above in the description."
                                                "".format(environments=ENVIRONMENTS),
                        action="store", default=DEFAULT_ENVIRONMENT)
    parser.add_argument("--properties", type=str, help="A file (YAML) defining properties for placeholder replacement "
                                                       "within config and preset files.  The file name is relative to "
                                                       "the --wled_dir directory. The properties file name will be "
                                                       "determined as described above where the default file base is "
                                                       "'properties'.",
                        action="store", default=None)

    parser.add_argument("--presets", type=str, help="A comma-separated list of WLED preset file names (YAML). The "
                                                    "file names are relative to the --wled_dir directory. Note that "
                                                    "preset IDs must be unique across all preset files. The "
                                                    "presets file name will be determined as described above where "
                                                    "the default file base is 'presets'.",
                        action="store", default=None)
    parser.add_argument("--segments", type=str, help="Segments definition file name (YAML) relative to the --wled_dir "
                                                     "directory. The segments file name will be determined as "
                                                     "described above where the default file base is 'segments'.",
                        action="store", default=DEFAULT_SEGMENTS_FILE_BASE)
    parser.add_argument("--cfg", type=str, help="WLED cfg file name (YAML) relative to the --wled_dir directory. The "
                                                "cfg file name will be determined as described above where the "
                                                "default file base is 'cfg'.",
                        action="store", default=None)
    parser.add_argument("--definitions_dir", type=str,
                        help="Definition file location. Applies to effects, palettes, and colors files. If not "
                             "specified, '" + DEFAULT_DEFINITIONS_DIR + "' is used.",
                        action="store", default=DEFAULT_DEFINITIONS_DIR)
    parser.add_argument("--effects", type=str, help="WLED effect definition file name (YAML) relative to the "
                                                    "--definitions_dir directory. If not specified, '" +
                                                    DEFAULT_EFFECTS_FILE + "' is used.",
                        action="store", default=DEFAULT_EFFECTS_FILE)
    parser.add_argument("--palettes", type=str, help="WLED palette definitions file-name (YAML) relative to the "
                                                     "--definitions_dir directory. If not specified, '" +
                                                     DEFAULT_PALETTES_FILE + "' is used.",
                        action="store", default=DEFAULT_PALETTES_FILE)
    parser.add_argument("--colors", type=str, help="HTML color-name definitions file-name (YAML) relative to the "
                                                   "--definitions_dir directory. If not specified, '" +
                                                   DEFAULT_COLORS_FILE + "' is used.",
                        action="store", default=DEFAULT_COLORS_FILE)
    parser.add_argument("--suffix", type=str, help=("Suffix to be appended to the output file names, preceded by a "
                                                    "'-',  before the '.json' extension."),
                        action="store", default=None)
    parser.add_argument("--include", type=str, help=("A comma-separated list of preset/playlist IDs/names to INCLUDE "
                                                     "in the output presets file. When this option is provided the "
                                                     "script will start with an empty set of presets and include only "
                                                     "those in the list. If a playlist is provided in the list "
                                                     " the playlist itself will be included. If the --deep option is "
                                                     "present presets referenced in the playlist will also be "
                                                     "included. The --include and --exclude "
                                                     "options are mutually exclusive.  Providing both will result in "
                                                     "an error and script termination."), action="store",
                        default=None)
    parser.add_argument("--exclude", type=str, help=("A comma-separated list of preset/playlist IDs/names to EXCLUDE "
                                                     "from the output presets file. When this option is provided the "
                                                     "script will start with all presets in the --presets file "
                                                     "exclude those in the list. If a playlist is provided in the "
                                                     "list the playlist itself will be excluded. If the --deep option "
                                                     "is present presets referenced in the playlist will also be"
                                                     "excluded. The --include and --exclude options are mutually "
                                                     "exclusive.  Providing both will result in an error and script "
                                                     "termination."), action="store",
                        default=None)
    parser.add_argument('--deep', help=("If the --deep option is present, presets referenced in playlists will "
                                        "be included/excluded depending on the presence of the --include or --exclude "
                                        "options.  If neither the --include or --exclude options are present the "
                                        "--deep option will be ignored."), action='store_true')

    parser.add_argument('--test', help="If the --deep processing will be performed, but no files will be saved.",
                        action='store_true')

    args = parser.parse_args()
    wled_dir = str(args.wled_dir)
    environment = str(args.env) if args.env is not None else None
    properties_option = str(args.properties) if args.properties is not None else None
    # properties_file = get_file_name(environment, properties_option, DEFAULT_PROPERTIES_FILE_BASE)
    presets_option = str(args.presets) if args.presets is not None else None
    # presets_files = get_file_names(environment, presets_option, DEFAULT_PRESETS_FILE_BASE)
    segments_option = str(args.segments) if args.segments is not None else None
    # segments_file = get_file_name(environment, segments_option, DEFAULT_SEGMENTS_FILE_BASE)
    cfg_option = str(args.cfg) if args.cfg is not None else None
    # cfg_file = get_file_name(environment, cfg_option, DEFAULT_CONFIG_FILE)
    definitions_dir = str(args.definitions_dir)
    effects_file = str(args.effects)
    palettes_file = str(args.palettes)
    colors_file = str(args.colors)
    suffix = '-' + str(args.suffix) if args.suffix is not None else ''
    include_list = str(args.include).split(',') if args.include is not None else None
    exclude_list = str(args.exclude).split(',') if args.exclude is not None else None
    deep = args.deep
    test_mode = args.test

    segments_path = build_path(wled_dir, environment, segments_option, DEFAULT_SEGMENTS_FILE_BASE)

    placeholder_replacer = load_placeholder_replacer(wled_dir, environment, properties_option, DEFAULT_PROPERTIES_FILE_BASE)

    print("wled_dir: " + wled_dir)
    print("environment: " + str(environment))
    print("segments_path: {path}".format(path=segments_path))
    print("suffix: '{suffix}'".format(suffix=suffix))
    print("include_list: " + str(include_list))
    print("exclude_list: " + str(exclude_list))
    print("deep: " + str(deep))
    print("test: " + str(test_mode))

    print()

    if include_list is not None and exclude_list is not None:
        raise ValueError("The --include and --exclude options are mutually exclusive and cannot both be provided.")

    if cfg_option is not None and presets_option is None:
        raise ValueError("Cannot process config file without presets file.")

    effects_path = build_path(definitions_dir, environment, effects_file, DEFAULT_EFFECTS_FILE)
    palettes_path = build_path(definitions_dir, environment, palettes_file, DEFAULT_PALETTES_FILE)
    colors_path = build_path(definitions_dir, environment, colors_file, DEFAULT_COLORS_FILE)

    print("definitions_dir: " + definitions_dir)
    print("effects_path: {path}".format(path=effects_path))
    print("palettes_path: {path}".format(path=palettes_path))
    print("colors_path: {path}".format(path=colors_path))

    presets_data = None

    if presets_option is not None:
        presets_paths = build_path_list(wled_dir, environment, presets_option, DEFAULT_PRESETS_FILE_BASE)
        print("presets_path: {paths}".format(paths=presets_paths))
        wled_presets = WledPresets(colors_path, palettes_path, effects_path)
        print("Processing {file}".format(file=presets_paths))

        raw_presets_data = load_yaml_files(presets_paths)

        if placeholder_replacer is not None:
            prepped_presets_data = placeholder_replacer.process_wled_data(raw_presets_data)
        else:
            prepped_presets_data = raw_presets_data

        presets_data = wled_presets.process_wled_data(prepped_presets_data, segments_file=segments_path)

        if len(presets_paths) > 1:
            yaml_file_path = get_output_file_name(presets_paths[0],
                                                  "{suffix}{env}-merged".format(suffix=suffix,
                                                                                env="-" + environment
                                                                                if environment is not None else ""),
                                                  'yaml')
            if not test_mode:
                print("Saving merged YAML to {file}".format(file=yaml_file_path))
                with open(yaml_file_path, "w", newline='\n') as out_file:
                    yaml.dump(presets_data, out_file, indent=2)
            else:
                print("Would have saved merged YAML to {file}".format(file=yaml_file_path))

        if include_list is not None:
            include_filter = PresetsIncludeFilter(presets_data, deep)
            presets_data = include_filter.apply(include_list)
        elif exclude_list is not None:
            exclude_filter = PresetsExcludeFilter(presets_data, deep)
            presets_data = exclude_filter.apply(exclude_list)

        json_file_path = get_output_file_name(presets_paths[0],
                                              "{suffix}{env}".format(suffix=suffix,
                                                                     env="-" + environment
                                                                     if environment is not None else ""))
        if not test_mode:
            if exists(json_file_path):
                rename_existing_file(json_file_path)
            print("Generating {file}".format(file=json_file_path))
            with open(json_file_path, "w", newline='\n') as out_file:
                json.dump(presets_data, out_file, indent=2)
        else:
            print("Would have generated {file}".format(file=json_file_path))

    if cfg_option is not None:
        cfg_paths = build_path_list(wled_dir, environment, cfg_option, DEFAULT_CFG_FILE)
        print()
        print("cfg_path: {paths}".format(paths=cfg_paths))
        wled_cfg = WledCfg(presets_data=presets_data)
        print("Processing {file}".format(file=cfg_paths))

        raw_cfg_data = load_yaml_files(cfg_paths)

        if placeholder_replacer is not None:
            prepped_cfg_data = placeholder_replacer.process_wled_data(raw_cfg_data)
        else:
            prepped_cfg_data = raw_cfg_data

        cfg_data = wled_cfg.process_wled_data(prepped_cfg_data)
        json_file_path = get_output_file_name(cfg_paths[0], suffix)
        if not test_mode:
            if exists(json_file_path):
                rename_existing_file(json_file_path)
            print("Generating {file}".format(file=json_file_path))
            with open(json_file_path, "w", newline='\n') as out_file:
                json.dump(cfg_data, out_file, indent=2)
        else:
            print("Would have generated {file}".format(file=json_file_path))


def load_placeholder_replacer(directory: str, environment: str, file_option: str, file_base: str):
    properties_path = build_path(directory, environment, file_option, file_base)
    print("Loading properties from: {file}".format(file=properties_path))
    if properties_path is not None:
        properties_data = load_yaml_file(properties_path)
        placeholder_replacer = WledPlaceholderReplacer(properties_data)
    else:
        placeholder_replacer = None

    return placeholder_replacer


def build_path_list(directory: str, environment: str, files_option: str, file_base: str):
    paths = []
    if files_option is not None and len(files_option) > 0:
        for file in files_option.split(','):
            path = build_path(directory, environment, file, file_base)
            if path is not None:
                paths.append(path)

    return paths


def build_path(directory: str, environment: str, file_option: str, file_base: str):
    candidates = get_file_name_candidates(environment, file_option, file_base)

    if len(candidates) == 0:
        raise ValueError("No candidates found for '{base}' file.".format(base=file_base))

    for candidate in candidates:
        file_path = "{dir}/{file}".format(dir=directory, file=candidate) if len(candidate) > 0 else None
        if file_path is not None:
            path = Path(file_path)
            if path.is_file():
                return file_path

    return None


def get_file_name_candidates(environment: str, file_option: str, file_base: str):
    candidates = []
    if file_option is not None and file_option.endswith(YAML_EXTENSION):
        candidates.append(file_option)
    else:
        if file_option is not None:
            if environment is not None:
                candidates.append("{option}-{env}.yaml".format(option=file_option, env=environment))

            candidates.append("{option}.yaml".format(option=file_option))

        if environment is not None:
            candidates.append("{base}-{env}.yaml".format(base=file_base, env=environment))

        candidates.append("{base}.yaml".format(base=file_base))

    return candidates


def get_file_names(environment: str, file_option_list: [str], file_base: str):
    file_names = []
    if file_option_list is not None and len(file_option_list) > 0:
        for file in file_option_list.split(','):
            if file is not None and len(file) > 0:
                file_names.append(get_file_name(environment, file, file_base))

    return file_names


def get_output_file_name(yaml_file_name: str, suffix: str, extension: str = "json"):
    file_base_name = yaml_file_name.replace('.yaml', '', 1)
    if file_base_name.endswith(suffix):
        json_file_name = '{base_name}.{extension}'.format(base_name=file_base_name, extension=extension)
    else:
        json_file_name = '{base_name}{suffix}.{extension}'.format(base_name=file_base_name, suffix=suffix,
                                                                  extension=extension)

    return json_file_name


def rename_existing_file(file_path):
    backup_file_path = "{file_path}.backup".format(file_path=file_path)
    if exists(backup_file_path):
        print("Removing existing backup file: {file}".format(file=backup_file_path))
        os.remove(backup_file_path)

    print("Renaming existing file from {file}\n                         to {backup_file}".format(file=file_path,
                                                                                                 backup_file=backup_file_path))
    os.rename(file_path, backup_file_path)


if __name__ == '__main__':
    main(sys.argv[0], sys.argv[1:])
