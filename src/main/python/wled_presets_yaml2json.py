import sys
import json
from wled_presets import WledPresets


def main(name, args):
    yaml_file_name = args[0]
    wled_presets = WledPresets()
    json_data = wled_presets.process_yaml_file(sys.argv[1])
    json_file_name = get_json_file_name(yaml_file_name)
    with open(json_file_name, "w") as out_file:
        json.dump(json_data, out_file, indent=2)


def get_json_file_name(yaml_file_name: str):
    json_file_name = yaml_file_name.replace('.yaml', '.json', 1)
    return json_file_name


if __name__ == '__main__':
    main(sys.argv[0], sys.argv[1:])
