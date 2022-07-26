import argparse
import sys
import json

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

    args = parser.parse_args()
    wled_dir = str(args.wled_dir)
    presets_file = str(args.presets)
    segments_file = str(args.segments)
    cfg_file = str(args.cfg)
    definitions_dir = str(args.definitions_dir)
    effects_file = str(args.effects)
    pallets_file = str(args.pallets)
    colors_file = str(args.colors)

    presets_path = build_path(wled_dir, presets_file)
    segments_path = build_path(wled_dir, segments_file)
    cfg_path = build_path(wled_dir, cfg_file)

    print("wled_dir: " + wled_dir)
    print("presets_path: {path}".format(path=presets_path))
    print("segments_path: {path}".format(path=segments_path))
    print("cfg_path: {path}".format(path=cfg_path))
    print()

    effects_path = build_path(definitions_dir, effects_file)
    pallets_path = build_path(definitions_dir, pallets_file)
    colors_path = build_path(definitions_dir, colors_file)

    print("definitions_dir: " + definitions_dir)
    print("effects_path: {path}".format(path=effects_path))
    print("pallets_path: {path}".format(path=pallets_path))
    print("colors_path: {path}".format(path=colors_path))

    wled_presets = WledPresets(colors_path, pallets_path, effects_path)
    json_data = wled_presets.process_yaml_file(presets_path, segments_file=segments_path)
    json_file_path = get_json_file_name(presets_path)
    with open(json_file_path, "w") as out_file:
        json.dump(json_data, out_file, indent=2)

    wled_cfg = WledCfg(presets_path)
    json_data = wled_cfg.process_yaml_file(cfg_path)
    json_file_path = get_json_file_name(cfg_path)
    with open(json_file_path, "w") as out_file:
        json.dump(json_data, out_file, indent=2)


def build_path(directory, file):
    return "{dir}/{file}".format(dir=directory, file=file) if len(file) > 0 else None


def get_json_file_name(yaml_file_name: str):
    json_file_name = yaml_file_name.replace('.yaml', '.json', 1)
    return json_file_name


if __name__ == '__main__':
    main(sys.argv[0], sys.argv[1:])
