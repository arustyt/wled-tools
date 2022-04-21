import sys
import json
import yaml

from colors import Colors
from effects import Effects
from pallets import Pallets
from segments import Segments

# PRESET_DEFAULTABLES =  "bri,mainseg,on"
# SEGEMENT_DEFAULTABLES =
EFFECT_TAG = 'fx'
EFFECT_NAME_TAG = 'fx_name'
PALLET_TAG = 'pal'
PALLET_NAME_TAG = 'pal_name'
SEGMENT_NAME_TAG = 'seg_name'
SEGMENT_TAG = 'seg'
DEFAULTS = 'defaults'
PRESET_DEFAULTS = 'preset'
SEGMENT_DEFAULTS = 'segment'


class WledPresets:

    def __init__(self):
        self.colors = Colors()
        self.segments = Segments()
        self.pallets = Pallets()
        self.effects = Effects()
        self.global_preset_defaults = {}
        self.global_segment_defaults = {}
        self.preset_segment_defaults = {}
        self.current_preset_defaults = {}
        self.current_segment_defaults = {}

    def process_yaml_file(self, yaml_file_name):
        with open(yaml_file_name) as in_file:
            preset_data = yaml.safe_load(in_file)

        new_preset_data = {}

        self.load_global_defaults(preset_data)

        for key in preset_data.keys():
            if key == DEFAULTS:
                continue
            preset = preset_data[key]
            self.load_preset_defaults(key, preset)
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
        if len(data) > 0:
            if self.in_preset_segment(path):
                new_data = self.current_segment_defaults.copy()
            elif self.in_normal_preset(data):
                new_data = self.current_preset_defaults.copy()
            else:
                new_data = {}
        else:
            new_data = {}

        for key in data.keys():
            if key == DEFAULTS:
                continue
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

    # preset segment is one that contains a 'seg' element in the path.
    def in_preset_segment(self, path):
        return SEGMENT_TAG in path

    # normal preset is one that is not a playlist of macro.  Current test is if it contains a 'seg' element.
    def in_normal_preset(self, data):
        return SEGMENT_TAG in data

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
        if SEGMENT_TAG in path:
            if name == SEGMENT_NAME_TAG:
                return self.process_segment_name(path, name, data)
            elif name == PALLET_NAME_TAG:
                pallet = self.process_pallet_name(path, name, data)
                return (PALLET_TAG, pallet[1][1]),
            elif name == EFFECT_NAME_TAG:
                effect = self.process_effect_name(path, name, data)
                return (EFFECT_TAG, effect[1][1]),
        return (name, data),

    def process_segment_name(self, path, name, data):
        return self.segments.get_segment_by_name(data)

    def process_pallet_name(self, path, name, data):
        return self.pallets.get_pallet_by_name(data)

    def process_effect_name(self, path, name, data):
        return self.effects.get_effect_by_name(data)

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

    def load_global_defaults(self, preset_data):
        if DEFAULTS in preset_data:
            defaults = preset_data[DEFAULTS]
            if PRESET_DEFAULTS in defaults:
                self.load_global_preset_defaults(defaults[PRESET_DEFAULTS])
            if SEGMENT_DEFAULTS in defaults:
                self.load_global_segment_defaults(defaults[SEGMENT_DEFAULTS])

    def load_preset_defaults(self, preset_id, preset):
        if DEFAULTS in preset:
            defaults = preset[DEFAULTS]
            if SEGMENT_DEFAULTS in defaults:
                self.load_preset_segment_defaults(preset_id, defaults[SEGMENT_DEFAULTS])
        self.load_current_defaults()

    def load_current_defaults(self):
        self.current_preset_defaults = self.global_preset_defaults
        self.current_segment_defaults = {**self.global_segment_defaults, **self.preset_segment_defaults}

    def load_global_preset_defaults(self, global_preset_defaults):
        self.global_preset_defaults = self.process_dict(self.get_new_path(DEFAULTS, PRESET_DEFAULTS), PRESET_DEFAULTS, global_preset_defaults)

    def get_new_path(self, path, name):
        return '{path}.{name}'.format(path=path, name=name)

    def load_global_segment_defaults(self, global_segment_defaults):
        self.global_segment_defaults = self.process_dict(self.get_new_path(DEFAULTS, SEGMENT_DEFAULTS), SEGMENT_DEFAULTS, global_segment_defaults)

    def load_preset_segment_defaults(self, preset_id, preset_segment_defaults):
        new_path = '{preset_id}.{path}.{name}'.format(preset_id=preset_id, path=DEFAULTS, name=SEGMENT_DEFAULTS)
        self.preset_segment_defaults = self.process_dict(new_path, SEGMENT_DEFAULTS, preset_segment_defaults)


if __name__ == '__main__':
    wled_presets = WledPresets()
    json_data = wled_presets.process_yaml_file(sys.argv[1])
    json_string = json.dumps(json_data, indent=2)

    print(json_string)
