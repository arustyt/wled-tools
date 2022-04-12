import sys
import json
import yaml

from colors import Colors


def main(name, args):
    with open(args[0]) as f:
        preset_data = yaml.safe_load(f)

    print('INPUT: ' + str(preset_data))

    for key in preset_data.keys():
        preset = preset_data[key]
        if isinstance(preset, dict):
            process_dict(key, preset)
        elif isinstance(preset, list):
            process_list(key, preset)
        else:
            process_element(key, preset, preset_data)

    preset_data = json.dumps(preset_data)

    print('OUTPUT: ' + str(preset_data))



def process_dict(name, data: dict):
    for key in data.keys():
        item = data[key]
        if isinstance(item, dict):
            process_dict(key, item)
        elif isinstance(item, list):
            process_list(key, item)
        else:
            process_element(key, item, data)


def process_list(name, data: list):
    if name == 'col':
        process_colors(data)
    for item in data:
        if isinstance(item, dict):
            process_dict(name, item)
        elif isinstance(item, list):
            process_list(name, item)


def process_element(name, data, container):
    pass


def process_colors(color_list):
    colors = Colors()
    for i in range(len(color_list)):
        value = color_list[i]
        if not isinstance(value, list):
            value_is_placeholder, placeholder = is_placeholder(str(value))
            if value_is_placeholder:
                r, g, b = colors.html_color_to_rgb(placeholder)
                color_list[i] = list((r, g, b))


def is_placeholder(value: str):
    return isinstance(value, str), value


if __name__ == '__main__':
    main(sys.argv[0], sys.argv[1:])
