import argparse
import sys
import json

from presets_exclude_filter import PresetsExcludeFilter
from presets_include_filter import PresetsIncludeFilter
from wled_cfg import WledCfg
from wled_presets import WledPresets

DEFAULT_DEFINITIONS_DIR = "../../../etc"
DEFAULT_WLED_DIR = "."
DEFAULT_COLORS_FILE = "colors.yaml"
DEFAULT_PALLETS_FILE = "pallets.yaml"
DEFAULT_EFFECTS_FILE = "effects.yaml"
DEFAULT_SEGMENTS_FILE = "segments.yaml"
DEFAULT_PRESETS_FILE = "presets.yaml"
DEFAULT_CONFIG_FILE = "cfg.yaml"


def main(name, args):
    parser = argparse.ArgumentParser(description='Convert YAML files to WLED JSON.')
    parser.add_argument("--wled_dir", type=str,
                        help="WLED data file location. Applies to presets, cfg, and segments files",
                        action="store", default=DEFAULT_WLED_DIR)
    parser.add_argument("--presets", type=str, help="WLED presets file name (YAML).", action="store",
                        default=DEFAULT_PRESETS_FILE)
    parser.add_argument("--segments", type=str, help="Segments definition file name (YAML).", action="store",
                        default=DEFAULT_SEGMENTS_FILE)
    parser.add_argument("--cfg", type=str, help="WLED cfg file name (YAML).", action="store",
                        default=DEFAULT_CONFIG_FILE)
    parser.add_argument("--definitions_dir", type=str,
                        help="Definition file location. Applies to effects, pallets, and colors files",
                        action="store", default=DEFAULT_DEFINITIONS_DIR)
    parser.add_argument("--effects", type=str, help="WLED effect definition file name (YAML).", action="store",
                        default=DEFAULT_EFFECTS_FILE)
    parser.add_argument("--pallets", type=str, help="WLED pallet definitions file-name (YAML).", action="store",
                        default=DEFAULT_PALLETS_FILE)
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
    presets_file = str(args.presets)
    segments_file = str(args.segments)
    cfg_file = str(args.cfg)
    definitions_dir = str(args.definitions_dir)
    effects_file = str(args.effects)
    pallets_file = str(args.pallets)
    colors_file = str(args.colors)
    suffix = '-' + str(args.suffix) if args.suffix is not None else ''
    include_list = str(args.include).split(',') if args.include is not None else None
    exclude_list = str(args.exclude).split(',') if args.exclude is not None else None
    deep = args.deep

    presets_path = build_path(wled_dir, presets_file)
    segments_path = build_path(wled_dir, segments_file)
    cfg_path = build_path(wled_dir, cfg_file)

    print("wled_dir: " + wled_dir)
    print("presets_path: {path}".format(path=presets_path))
    print("segments_path: {path}".format(path=segments_path))
    print("cfg_path: {path}".format(path=cfg_path))
    print("suffix: '{suffix}'".format(suffix=suffix))
    print("include_list: " + str(include_list))
    print("exclude_list: " + str(exclude_list))
    print("deep: " + str(deep))

    print()

    if include_list is not None and exclude_list is not None:
        raise ValueError("The --include and --exclude options are mutually exclusive and cannot both be provided.")

    effects_path = build_path(definitions_dir, effects_file)
    pallets_path = build_path(definitions_dir, pallets_file)
    colors_path = build_path(definitions_dir, colors_file)

    print("definitions_dir: " + definitions_dir)
    print("effects_path: {path}".format(path=effects_path))
    print("pallets_path: {path}".format(path=pallets_path))
    print("colors_path: {path}".format(path=colors_path))

    wled_presets = WledPresets(colors_path, pallets_path, effects_path)
    preset_data = wled_presets.process_yaml_file(presets_path, segments_file=segments_path)
    json_file_path = get_json_file_name(presets_path, suffix)

    if include_list is not None:
        include_filter = PresetsIncludeFilter(preset_data, deep)
        preset_data = include_filter.apply(include_list)
    elif exclude_list is not None:
        exclude_filter = PresetsExcludeFilter(preset_data, deep)
        preset_data = exclude_filter.apply(exclude_list)

    with open(json_file_path, "w") as out_file:
        json.dump(preset_data, out_file, indent=2)

    wled_cfg = WledCfg(presets_data=preset_data)
    cfg_data = wled_cfg.process_yaml_file(cfg_path)
    json_file_path = get_json_file_name(cfg_path, suffix)
    with open(json_file_path, "w") as out_file:
        json.dump(cfg_data, out_file, indent=2)


def build_path(directory, file):
    return "{dir}/{file}".format(dir=directory, file=file) if len(file) > 0 else None


def get_json_file_name(yaml_file_name: str, suffix: str):
    json_file_name = yaml_file_name.replace('.yaml', suffix + '.json', 1)
    return json_file_name


if __name__ == '__main__':
    main(sys.argv[0], sys.argv[1:])
