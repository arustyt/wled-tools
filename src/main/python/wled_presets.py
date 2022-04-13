import sys
import json
import yaml

from colors import Colors
from segments import Segments


class WledPresets:

    def __init__(self):
        self.colors = Colors()
        self.segments = Segments()

    def process_yaml(self, yaml_file_name):
        with open(yaml_file_name) as in_file:
            preset_data = yaml.safe_load(in_file)

        new_preset_data = {}

        for key in preset_data.keys():
            preset = preset_data[key]
            if isinstance(preset, dict):
                new_preset_data[key] = self.process_dict(key, preset)
            elif isinstance(preset, list):
                new_preset_data[key] = self.process_list(key, preset)
            else:
                new_preset_data[key] = self.process_element(key, preset)

        return new_preset_data

    def process_dict(self, name: str, data: dict):
        new_data = {}
        for key in data.keys():
            item = data[key]
            new_name = '{name}.{key}'.format(name=name, key=key)
            if isinstance(item, dict):
                new_data[key] = self.process_dict(new_name, item)
            elif isinstance(item, list):
                new_data[key] = self.process_list(new_name, item)
            else:
                new_data[key] = self.process_element(new_name, item)

        return new_data

    def process_list(self, name: str, data: list):
        if name.endswith('.col'):
            return self.process_colors(name, data)

        new_data = []

        index = 0
        for item in data:
            new_name = '{name}[{index}]'.format(name=name, index=index)
            index += 1
            if isinstance(item, dict):
                new_data.append(self.process_dict(new_name, item))
            elif isinstance(item, list):
                new_data.append(self.process_list(new_name, item))
            else:
                new_data.append(self.process_element(new_name, item))

        return new_data

    def process_element(self, name: str, data):
        return data

    def process_colors(self, name: str, color_list: list):
        new_color_list = []
        for index in range(len(color_list)):
            value = color_list[index]
            if not isinstance(value, list):
                value_is_placeholder, placeholder = self.is_placeholder(str(value))
                if value_is_placeholder:
                    r, g, b = self.colors.html_color_to_rgb(placeholder)
                    new_color_list.append(list((r, g, b)))

        return new_color_list

    def is_placeholder(self, value: str):
        return isinstance(value, str), value


if __name__ == '__main__':
    wled_presets = WledPresets()
    json_data = wled_presets.process_yaml(sys.argv[1])
    json_string = json.dumps(json_data, indent=2)

    print(json_string)
