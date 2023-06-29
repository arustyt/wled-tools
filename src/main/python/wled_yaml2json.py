import argparse
import os
import sys
import json
from os.path import exists

from presets_exclude_filter import PresetsExcludeFilter
from presets_include_filter import PresetsIncludeFilter
from wled_cfg import WledCfg
from wled_presets import WledPresets

DEFAULT_DEFINITIONS_DIR = "../../../etc"
DEFAULT_WLED_DIR = "."
DEFAULT_COLORS_FILE = "colors.yaml"
DEFAULT_PALETTES_FILE = "palettes.yaml"
DEFAULT_EFFECTS_FILE = "effects.yaml"
DEFAULT_SEGMENTS_FILE = "segments.yaml"
DEFAULT_PRESETS_FILE = "presets.yaml"
DEFAULT_CONFIG_FILE = "cfg.yaml"


def main(name, args):
    parser = argparse.ArgumentParser(description='Convert YAML files to WLED JSON.')
    parser.add_argument("--wled_dir", type=str,
                        help="WLED data file location. Applies to presets, cfg, and segments files",
                        action="store", default=DEFAULT_WLED_DIR)
    parser.add_argument("--presets", type=str, help="One or more WLED presets file name (YAML), separated by commas.",
                        action="store", default=None)
    parser.add_argument("--segments", type=str, help="Segments definition file name (YAML).", action="store",
                        default=DEFAULT_SEGMENTS_FILE)
    parser.add_argument("--cfg", type=str, help="WLED cfg file name (YAML).", action="store",
                        default=None)
    parser.add_argument("--definitions_dir", type=str,
                        help="Definition file location. Applies to effects, palettes, and colors files",
                        action="store", default=DEFAULT_DEFINITIONS_DIR)
    parser.add_argument("--effects", type=str, help="WLED effect definition file name (YAML).", action="store",
                        default=DEFAULT_EFFECTS_FILE)
    parser.add_argument("--palettes", type=str, help="WLED palette definitions file-name (YAML).", action="store",
                        default=DEFAULT_PALETTES_FILE)
    parser.add_argument("--colors", type=str, help="HTML color-name definitions file-name (YAML).", action="store",
                        default=DEFAULT_COLORS_FILE)
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
    parser.add_argument('--deep', action='store_true')

    args = parser.parse_args()
    wled_dir = str(args.wled_dir)
    presets_file = str(args.presets) if args.presets is not None else None
    segments_file = str(args.segments)
    cfg_file = str(args.cfg) if args.cfg is not None else None
    definitions_dir = str(args.definitions_dir)
    effects_file = str(args.effects)
    palettes_file = str(args.palettes)
    colors_file = str(args.colors)
    suffix = '-' + str(args.suffix) if args.suffix is not None else ''
    include_list = str(args.include).split(',') if args.include is not None else None
    exclude_list = str(args.exclude).split(',') if args.exclude is not None else None
    deep = args.deep

    segments_path = build_path(wled_dir, segments_file)

    print("wled_dir: " + wled_dir)
    print("segments_path: {path}".format(path=segments_path))
    print("suffix: '{suffix}'".format(suffix=suffix))
    print("include_list: " + str(include_list))
    print("exclude_list: " + str(exclude_list))
    print("deep: " + str(deep))

    print()

    if include_list is not None and exclude_list is not None:
        raise ValueError("The --include and --exclude options are mutually exclusive and cannot both be provided.")

    effects_path = build_path(definitions_dir, effects_file)
    palettes_path = build_path(definitions_dir, palettes_file)
    colors_path = build_path(definitions_dir, colors_file)

    print("definitions_dir: " + definitions_dir)
    print("effects_path: {path}".format(path=effects_path))
    print("palettes_path: {path}".format(path=palettes_path))
    print("colors_path: {path}".format(path=colors_path))

    if presets_file is not None:
        presets_path = build_path(wled_dir, presets_file)
        print("presets_path: {path}".format(path=presets_path))
        wled_presets = WledPresets(colors_path, palettes_path, effects_path)
        print("Processing {file}".format(file=presets_path))
        preset_data = wled_presets.process_yaml_file(presets_path, segments_file=segments_path)

        if include_list is not None:
            include_filter = PresetsIncludeFilter(preset_data, deep)
            preset_data = include_filter.apply(include_list)
        elif exclude_list is not None:
            exclude_filter = PresetsExcludeFilter(preset_data, deep)
            preset_data = exclude_filter.apply(exclude_list)

        json_file_path = get_json_file_name(presets_path, suffix)
        if exists(json_file_path):
            rename_existing_file(json_file_path)
        print("Generating {file}".format(file=json_file_path))
        with open(json_file_path, "w", newline='\n') as out_file:
            json.dump(preset_data, out_file, indent=2)

    if cfg_file is not None:
        cfg_path = build_path(wled_dir, cfg_file)
        print()
        print("cfg_path: {path}".format(path=cfg_path))
        wled_cfg = WledCfg(presets_data=preset_data)
        print("Processing {file}".format(file=cfg_path))
        cfg_data = wled_cfg.process_yaml_file(cfg_path)
        json_file_path = get_json_file_name(cfg_path, suffix)
        if exists(json_file_path):
            rename_existing_file(json_file_path)
        print("Generating {file}".format(file=json_file_path))
        with open(json_file_path, "w", newline='\n') as out_file:
            json.dump(cfg_data, out_file, indent=2)


def build_path(directory, file):
    return "{dir}/{file}".format(dir=directory, file=file) if len(file) > 0 else None


def get_json_file_name(yaml_file_name: str, suffix: str):
    file_base_name = yaml_file_name.replace('.yaml', '', 1)
    if file_base_name.endswith(suffix):
        json_file_name = '{base_name}.json'.format(base_name=file_base_name)
    else:
        json_file_name = '{base_name}{suffix}.json'.format(base_name=file_base_name, suffix=suffix)

    return json_file_name


def rename_existing_file(file_path):
    backup_file_path = "{file_path}.backup".format(file_path=file_path)
    if exists(backup_file_path):
        print("Removing existing backup file: {file}".format(file=backup_file_path))
        os.remove(backup_file_path)

    print("Renaming existing file from {file}\n                         to {backup_file}".format(file=file_path, backup_file=backup_file_path))
    os.rename(file_path, backup_file_path)


if __name__ == '__main__':
    main(sys.argv[0], sys.argv[1:])
