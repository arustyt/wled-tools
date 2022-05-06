import sys
import json

from colors import Colors
from effects import Effects
from pallets import Pallets
from presets import Presets
from segments import Segments
from wled_yaml import WledYaml

ID_TAG = 'id'
SEGMENTS_FILE_TAG = 'segments_file'

COLOR_TAG = 'col'
EFFECT_TAG = 'fx'
EFFECT_NAME_TAG = 'fx_name'
PALLET_TAG = 'pal'
PALLET_NAME_TAG = 'pal_name'
SEGMENT_NAME_TAG = 'seg_name'
SEGMENT_TAG = 'seg'
DEFAULTS = 'defaults'
PRESET_DEFAULTS = 'preset'
SEGMENT_DEFAULTS = 'segment'


class WledPresets(WledYaml):

    def __init__(self, color_names_file='colors.yaml', pallet_names_file='pallets.yaml',
                 effect_names_file='effects.yaml'):
        super().__init__()
        self.colors = Colors(color_names_file)
        self.pallets = Pallets(pallet_names_file)
        self.effects = Effects(effect_names_file)
        self.segments = None
        self.presets = None
        self.global_preset_defaults = {}
        self.global_segment_defaults = {}
        self.preset_segment_defaults = {}
        self.current_preset_defaults = {}
        self.current_segment_defaults = {}

    def process_other_args(self, presets_file_path, other_args):
        self.presets = Presets(presets_file_path)
        if SEGMENTS_FILE_TAG in other_args:
            self.segments = Segments(other_args[SEGMENTS_FILE_TAG])
        else:
            raise AttributeError("Missing keyword argument, '{name}'".format(name=SEGMENTS_FILE_TAG))

    def init_dict(self, path: str, name, data: dict):
        if len(data) > 0:
            if self.in_preset_segment(path):
                new_data = self.current_segment_defaults.copy()
            elif self.in_normal_preset(data):
                new_data = self.current_preset_defaults.copy()
            else:
                new_data = {}
        else:
            new_data = {}
        return new_data

    def finalize_dict(self, path: str, name, data: dict, new_data: dict):
        if self.in_preset_segment(path):
            self.current_segment_defaults = new_data.copy()

    # preset segment is one that contains a 'seg' element in the path.
    def in_preset_segment(self, path):
        return SEGMENT_TAG in path

    # normal preset is one that is not a playlist or macro.  Current test is if it contains a 'seg' element.
    def in_normal_preset(self, data):
        return SEGMENT_TAG in data

    def handle_list(self, path: str, name, data: list, new_data: list):
        if name == COLOR_TAG:
            return True, self.process_colors(path, COLOR_TAG, data)
        else:
            return False, new_data

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
        data_str = str(data)
        if '*' in data_str:
            parts = data_str.split('*', 1)
            value = parts[0].strip()
            count = int(parts[1].strip())
            result = [int(value) if value.isnumeric() else value] * count
        elif "playlist.ps" in path:
            result = [self.presets.get_preset_by_name(str(data))[ID_TAG]]
        else:
            result = [data]

        return result

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

    def load_defaults(self, path, preset_id, preset):
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
