import argparse
import os
import json
from os.path import exists

import requests

from effects import Effects
from palettes import Palettes
from wled_constants import EFFECTS_TAG, PALETTES_TAG

DEFAULT_DEFINITIONS_DIR = "../../../etc"
DEFAULT_PALETTES_FILE = "palettes.yaml"
DEFAULT_EFFECTS_FILE = "effects.yaml"


def main():
    parser = argparse.ArgumentParser(description='Convert YAML files to WLED JSON.')
    parser.add_argument("--host", type=str, help="Hostname to which the file(s) will be uploaded.", action="store",
                        required=True)
    parser.add_argument("--definitions_dir", type=str,
                        help="Definition file location. Applies to effects, palettes, and colors files",
                        action="store", default=DEFAULT_DEFINITIONS_DIR)
    parser.add_argument("--effects", type=str, help="WLED effect definition file name (YAML).", action="store",
                        default=DEFAULT_EFFECTS_FILE)
    parser.add_argument("--palettes", type=str, help="WLED palette definitions file-name (YAML).", action="store",
                        default=DEFAULT_PALETTES_FILE)

    args = parser.parse_args()
    host = str(args.host)
    definitions_dir = str(args.definitions_dir)
    effects_file = args.effects
    palettes_file = args.palettes

    effects_path = build_path(definitions_dir, effects_file)
    palettes_path = build_path(definitions_dir, palettes_file)

    print("host: " + host)
    print("definitions_dir: " + definitions_dir)
    print("effects_path: {path}".format(path=effects_path))
    print("palettes_path: {path}".format(path=palettes_path))

    wled_data = download_wled_data(host)

    effects = Effects(effects_path)
    effects.merge(wled_data[EFFECTS_TAG])
    if effects.is_modified():
        effects_data = effects.dump()
        print("effects: {effects}".format(effects=effects_data))

    palettes = Palettes(palettes_path)
    palettes.merge(wled_data[PALETTES_TAG])
    if palettes.is_modified():
        palettes_data = palettes.dump()
        print("palettes: {palettes}".format(palettes=palettes_data))


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


def build_path(directory, file):
    return "{dir}/{file}".format(dir=directory, file=file) if file is not None and len(file) > 0 else None


def rename_existing_file(file_path):
    backup_file_path = "{file_path}.backup".format(file_path=file_path)
    if exists(backup_file_path):
        print("Removing existing backup file: {file}".format(file=backup_file_path))
        os.remove(backup_file_path)

    print("Renaming existing file from {file}".format(file=file_path))
    print("                         to {backup_file}".format(backup_file=backup_file_path))
    os.rename(file_path, backup_file_path)


if __name__ == '__main__':
    main()
