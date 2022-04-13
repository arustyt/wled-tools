import sys
import json
import yaml

from colors import Colors
from segments import Segments


class WledPresets:

    def __init__(self):
        self.colors = Colors()
        self.segments = Segments()

    def process_yaml_file(self, yaml_file_name):
        with open(yaml_file_name) as in_file:
            preset_data = yaml.safe_load(in_file)

        new_preset_data = {}

        for key in preset_data.keys():
            preset = preset_data[key]
            if isinstance(preset, dict):
                new_preset_data[key] = self.process_dict(key, key, preset)
            elif isinstance(preset, list):
                new_preset_data[key] = self.process_list(key, key, preset)
            else:
                replacements = self.process_dict_element(key, key, preset)
                if len(replacements) >= 1:
                    for replacement in replacements:
                        new_preset_data[replacement[0]] = replacement[1]

        return new_preset_data

    def process_dict(self, path: str, name, data: dict):
        new_data = {}
        for key in data.keys():
            item = data[key]
            new_path = '{name}.{key}'.format(name=path, key=key)
            if isinstance(item, dict):
                new_data[key] = self.process_dict(new_path, key, item)
            elif isinstance(item, list):
                new_data[key] = self.process_list(new_path, key, item)
            else:
                replacements = self.process_dict_element(new_path, key, item)
                if len(replacements) >= 1:
                    for replacement in replacements:
                        new_data[replacement[0]] = replacement[1]

        return new_data

    def process_list(self, path: str, name, data: list):
        if name == 'col':
            return self.process_colors(path, 'col', data)

        new_data = []

        index = 0
        for item in data:
            new_path = '{name}[{index}]'.format(name=path, index=index)
            index += 1
            if isinstance(item, dict):
                new_data.append(self.process_dict(new_path, None, item))
            elif isinstance(item, list):
                new_data.append(self.process_list(new_path, None, item))
            else:
                new_data.extend(self.process_list_element(new_path, None, item))

        return new_data

    def process_dict_element(self, path: str, name, data):
        if name == 'seg_name' and 'seg' in path:
            return self.process_segment_name(path, name, data)
        return (name, data),

    def process_segment_name(self, path, name, data):
        return self.segments.get_segment_by_name(data)

    def process_list_element(self, path: str, name, data):
        return [data]

    def process_colors(self, path: str, name, color_list: list):
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
    json_data = wled_presets.process_yaml_file(sys.argv[1])
    json_string = json.dumps(json_data, indent=2)

    print(json_string)
