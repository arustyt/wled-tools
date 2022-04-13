import sys
import json
import yaml

from colors import Colors


def main(name, args):
    yaml_file_name = args[0]

    with open(yaml_file_name) as in_file:
        preset_data = yaml.safe_load(in_file)

    new_preset_data = {}

    for key in preset_data.keys():
        preset = preset_data[key]
        if isinstance(preset, dict):
            new_preset_data[key] = process_dict(key, preset)
        elif isinstance(preset, list):
            new_preset_data[key] = process_list(key, preset)
        else:
            new_preset_data[key] = process_element(key, preset)

    json_file_name = get_json_file_name(yaml_file_name)
    with open(json_file_name, "w") as out_file:
        json.dump(new_preset_data, out_file, indent=2)


def get_json_file_name(yaml_file_name: str):
    json_file_name = yaml_file_name.replace('.yaml', '.json', 1)
    return json_file_name


def process_dict(name: str, data: dict):
    new_data = {}
    for key in data.keys():
        item = data[key]
        new_name = '{name}.{key}'.format(name=name, key=key)
        if isinstance(item, dict):
            new_data[key] = process_dict(new_name, item)
        elif isinstance(item, list):
            new_data[key] = process_list(new_name, item)
        else:
            new_data[key] = process_element(new_name, item)

    return new_data


def process_list(name: str, data: list):
    if name.endswith('.col'):
        return process_colors(name, data)

    new_data = []

    index = 0
    for item in data:
        new_name = '{name}[{index}]'.format(name=name, index=index)
        index += 1
        if isinstance(item, dict):
            new_data.append(process_dict(new_name, item))
        elif isinstance(item, list):
            new_data.append(process_list(new_name, item))
        else:
            new_data.append(process_element(new_name, item))

    return new_data


def process_element(name: str, data):
    return data


def process_colors(name: str, color_list: list):
    new_color_list = []
    colors = Colors()
    for index in range(len(color_list)):
        value = color_list[index]
        if not isinstance(value, list):
            value_is_placeholder, placeholder = is_placeholder(str(value))
            if value_is_placeholder:
                r, g, b = colors.html_color_to_rgb(placeholder)
                new_color_list.append(list((r, g, b)))

    return new_color_list


def is_placeholder(value: str):
    return isinstance(value, str), value


if __name__ == '__main__':
    main(sys.argv[0], sys.argv[1:])
