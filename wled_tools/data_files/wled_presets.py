import json
import sys

from data_files.presets import Presets
from data_files.segments import Segments
from data_files.wled_data_processor import WledDataProcessor
from definition_files.colors import Colors
from definition_files.effects import Effects
from definition_files.palettes import Palettes
from wled_constants import SEGMENTS_FILE_TAG, SEGMENT_TAG, COLOR_TAG, SEGMENT_NAME_TAG, PALETTE_NAME_TAG, \
    EFFECT_NAME_TAG, PALETTE_TAG, EFFECT_TAG, ID_TAG, PRESET_KEY, STOP_TAG, DEFAULTS, PRESET_DEFAULTS, SEGMENT_DEFAULTS, \
    PLAYLIST_PRESETS_PATH_TAG, PLAYLIST_END_PATH_TAG
from wled_utils.dict_utils import get_dict_path


class WledPresets(WledDataProcessor):

    def __init__(self, environment, color_names_file='colors.yaml', palette_names_file='palettes.yaml',
                 effect_names_file='effects.yaml'):
        super().__init__(environment)
        self.colors = Colors(color_names_file)
        self.palettes = Palettes(palette_names_file)
        self.effects = Effects(effect_names_file)
        self.segments = None
        self.presets = None
        self.global_preset_defaults = {}
        self.global_segment_defaults = {}
        self.current_preset_defaults = {}
        self.current_segment_defaults = {}
        self.max_segments = 0

    def process_other_args(self, raw_preset_data, other_args):
        self.presets = Presets(self.environment, presets_data=raw_preset_data)
        if SEGMENTS_FILE_TAG in other_args:
            self.segments = Segments(self.environment, other_args[SEGMENTS_FILE_TAG])
        else:
            raise AttributeError("Missing keyword argument, '{name}'".format(name=SEGMENTS_FILE_TAG))

    def init_dict(self, path: str, name, data: dict):
        if len(data) > 0:
            if self.in_preset_segment(path):
                new_data = self.current_segment_defaults.copy()
                if SEGMENT_NAME_TAG in data:
                    segment = self.segments.get_segment_by_name(data[SEGMENT_NAME_TAG])
                    new_data.update(segment)
                if PALETTE_NAME_TAG in data:
                    palette = self.palettes.get_by_name(data[PALETTE_NAME_TAG])
                    new_data[PALETTE_TAG] = palette[ID_TAG]
                if EFFECT_NAME_TAG in data:
                    effect = self.effects.get_by_name(data[EFFECT_NAME_TAG])
                    new_data[EFFECT_TAG] = effect[ID_TAG]
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

    def process_list(self, path: str, name, data: list, new_data: list):
        if name == COLOR_TAG:
            self.process_colors(path, COLOR_TAG, data, new_data)
        else:
            super().process_list(path, name, data, new_data)

    def finalize_list(self, path: str, name, data: list, new_data: list):
        if name == 'seg':
            if len(new_data) > self.max_segments:
                self.max_segments = len(new_data)

    def handle_dict_element(self, path: str, name: str, data: str):
        if SEGMENT_TAG in path:
            if name in [SEGMENT_NAME_TAG, PALETTE_NAME_TAG, EFFECT_NAME_TAG]:
                return ()  # Name tags were applied in init_dict()
        elif PLAYLIST_END_PATH_TAG in path:
            return (name, self.presets.get_preset_by_name(str(data))[ID_TAG]),
        return (name, data),

    def handle_list_element(self, path: str, name, data):
        data_str = str(data)
        if '*' in data_str:
            parts = data_str.split('*', 1)
            value = parts[0].strip()
            count = int(parts[1].strip())
            result = [int(value) if value.isnumeric() else value] * count
        elif PLAYLIST_PRESETS_PATH_TAG in path:
            result = [self.presets.get_preset_by_name(str(data))[ID_TAG]]
        else:
            result = [data]

        return result

    def finalize_wled_data(self, preset_data: dict):
        for preset in preset_data.values():
            if PRESET_KEY in preset:
                segments: list = preset[PRESET_KEY]
                num_segments = len(segments)
                if self.max_segments > num_segments:
                    for i in range(num_segments, self.max_segments):
                        segments.append({STOP_TAG: 0})
        return preset_data

    def process_colors(self, path: str, name, color_list: list, new_color_list: list):
        for index in range(len(color_list)):
            value = color_list[index]
            if not isinstance(value, list):
                value_is_placeholder, placeholder = self.is_placeholder(str(value))
                if value_is_placeholder:
                    r, g, b = self.colors.html_color_to_rgb(placeholder)
                    new_color_list.append(list((r, g, b)))

    def is_placeholder(self, value: str):
        return isinstance(value, str), value

    def load_global_defaults(self):
        preset_data = self.raw_wled_data
        if DEFAULTS in preset_data:
            defaults = preset_data[DEFAULTS]
            if PRESET_DEFAULTS in defaults:
                self.load_global_preset_defaults(defaults[PRESET_DEFAULTS])
            if SEGMENT_DEFAULTS in defaults:
                self.load_global_segment_defaults(defaults[SEGMENT_DEFAULTS])

    def load_global_preset_defaults(self, global_preset_defaults):
        self.global_preset_defaults = self.handle_dict(get_dict_path(DEFAULTS, PRESET_DEFAULTS),
                                                       PRESET_DEFAULTS, global_preset_defaults)

    def load_global_segment_defaults(self, global_segment_defaults):
        self.global_segment_defaults = self.handle_dict(get_dict_path(DEFAULTS, SEGMENT_DEFAULTS),
                                                        SEGMENT_DEFAULTS, global_segment_defaults)

    def apply_defaults(self, path, preset_id, preset):
        self.apply_current_defaults()

    def apply_current_defaults(self):
        self.current_preset_defaults = self.global_preset_defaults
        self.current_segment_defaults = self.global_segment_defaults


if __name__ == '__main__':
    wled_presets = WledPresets()
    json_data = wled_presets.process_wled_data(sys.argv[1])
    json_string = json.dumps(json_data, indent=2)

    print(json_string)
