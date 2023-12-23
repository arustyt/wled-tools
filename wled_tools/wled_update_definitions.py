import argparse
import json
import os
from os.path import exists

import requests
import yaml

from definition_files.effects import Effects
from definition_files.palettes import Palettes
from wled_constants import EFFECTS_TAG, PALETTES_TAG
from wled_utils.logger_utils import get_logger, init_logger
from wled_utils.path_utils import build_path

DEFAULT_DEFINITIONS_DIR = "../../../etc"
DEFAULT_PALETTES_FILE = "palettes.yaml"
DEFAULT_EFFECTS_FILE = "effects.yaml"


def main():
    parser = argparse.ArgumentParser(description='Updates effects and palettes definition files by downloading effects '
                                                 'and pallets from running WLED instance.')
    parser.add_argument("--host", type=str, help="Hostname of WLED instance from which the effects and pallets will "
                                                 "be downloaded.",
                        action="store", required=True)
    parser.add_argument("--definitions_dir", type=str,
                        help="Definition file location. Applies to effects and palettes files",
                        action="store", default=DEFAULT_DEFINITIONS_DIR)
    parser.add_argument("--effects", type=str, help="Name of file to which WLED effect definitions will be written "
                                                    "(YAML).", action="store",
                        default=DEFAULT_EFFECTS_FILE)
    parser.add_argument("--palettes", type=str, help="Name of file to which WLED palette definitions will be written "
                                                     "(YAML).", action="store",
                        default=DEFAULT_PALETTES_FILE)
    parser.add_argument('--auto_create', help="Automatically create new effects/palettes.", action='store_true')
    parser.add_argument("--auto_delete", type=str, help="Comma separated list of names of new effects/palettes to be "
                                                        "automatically deleted (if existing) or not created (if "
                                                        "new).", action="store", default=None)

    args = parser.parse_args()
    host = str(args.host)
    definitions_dir = str(args.definitions_dir)
    effects_file = args.effects
    palettes_file = args.palettes
    auto_create = args.auto_create
    auto_delete = args.auto_delete

    effects_path = build_path(definitions_dir, effects_file)
    palettes_path = build_path(definitions_dir, palettes_file)

    auto_delete_list = []
    if auto_delete is not None:
        for item in auto_delete.split(','):
            item = str(item).strip()
            if len(item) > 0:
                auto_delete_list.append(item)

    init_logger()

    get_logger().info("host: " + host)
    get_logger().info("definitions_dir: " + definitions_dir)
    get_logger().info("effects_path: {path}".format(path=effects_path))
    get_logger().info("palettes_path: {path}".format(path=palettes_path))

    wled_data = download_wled_data(host)

    get_logger().info("=====================================")
    get_logger().info("Processing effects: {path}".format(path=effects_path))
    get_logger().info("-------------------------------------")
    effects = Effects(effects_path)
    effects.merge(wled_data[EFFECTS_TAG], auto_create, auto_delete_list)
    if effects.is_modified():
        effects_data = effects.dump()
        backup_existing_file(effects_path)
        with open(effects_path, "w", newline='\n') as out_file:
            out_file.write(yaml.dump(effects_data, sort_keys=False, default_flow_style=False, width=1000))
    else:
        get_logger().info("No changes")

    get_logger().info("=====================================")

    get_logger().info("=====================================")
    get_logger().info("Processing palettes: {path}".format(path=palettes_path))
    get_logger().info("-------------------------------------")
    palettes = Palettes(palettes_path)
    palettes.merge(wled_data[PALETTES_TAG], auto_create, auto_delete_list)
    if palettes.is_modified():
        palettes_data = palettes.dump()
        backup_existing_file(palettes_path)
        with open(palettes_path, "w", newline='\n') as out_file:
            out_file.write(yaml.dump(palettes_data, sort_keys=False, default_flow_style=False, width=1000))
    else:
        get_logger().info("No changes")

    get_logger().info("=====================================")


#        get_logger().info("palettes: {palettes}".format(palettes=palettes_data))


def download_wled_data(host):
    url = "http://{host}/json".format(host=host)
    result = requests.get(url)
    wled_data = json.loads(result.content)

    return wled_data


def process_effects(effects, device_effects):
    modified = False
    i = 0
    for effect_name in device_effects[EFFECTS_TAG]:
        modified |= effects.modify(i, effect_name)
        i += 1

    return modified


def process_palettes(palettes, device_palettes):
    modified = False
    i = 0
    for palette_name in device_palettes[PALETTES_TAG]:
        modified |= palettes.modify(i, palette_name)
        i += 1

    return modified


def backup_existing_file(file_path):
    backup_file_path = "{file_path}.backup".format(file_path=file_path)
    if exists(backup_file_path):
        get_logger().info("Removing existing backup file: {file}".format(file=backup_file_path))
        os.remove(backup_file_path)

    get_logger().info("Renaming existing file from {file}".format(file=file_path))
    get_logger().info("                         to {backup_file}".format(backup_file=backup_file_path))
    os.rename(file_path, backup_file_path)


if __name__ == '__main__':
    main()
