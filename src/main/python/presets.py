import re
import yaml

from wled_yaml import DEFAULTS
from yaml_multi_file_loader import load_yaml_files

PRESETS_FILES_ARG = 'presets_files'
PRESETS_DATA_ARG = 'presets_data'
KWDICT_ARG = 'kwdict'


class Presets:

    def __init__(self, **kwargs):

        if KWDICT_ARG in kwargs:
            kwargs = kwargs[KWDICT_ARG]

        presets_data = kwargs[PRESETS_DATA_ARG] if PRESETS_DATA_ARG in kwargs else None

        if presets_data is None:
            presets_files = kwargs[PRESETS_FILES_ARG] if PRESETS_FILES_ARG in kwargs else 'presets.yaml'
            presets_data = load_yaml_files(presets_files)

        self.presets_by_name = {}
        for key in presets_data.keys():
            if key == DEFAULTS:
                continue

            preset = presets_data[key]
            if len(preset) == 0:
                continue

            preset_name_normalized = self.normalize_preset_name(preset['n'])
            entry = (('name', preset['n']), ('id', int(key)))
            self.presets_by_name[preset_name_normalized] = entry
            self.presets_by_name[key] = entry

    def normalize_preset_name(self, preset_name):
        preset_name_normalized = str(preset_name).lower()
        preset_name_normalized = re.sub('[ _]', '', preset_name_normalized)
        return preset_name_normalized

    #  Returns dict containing preset data: {'name': name, 'id': id}
    def get_preset_by_name(self, preset_string):
        preset_data = None
        preset_string_normalized = self.normalize_preset_name(preset_string)
        if preset_string_normalized in self.presets_by_name:
            preset_data = self.presets_by_name[preset_string_normalized]
        else:
            raise ValueError("Input '{name}' is not a recognized preset name or id".format(name=preset_string))

        return dict(preset_data)


if __name__ == '__main__':
    presets = Presets('presets-new.yaml')
    test_preset_string = 'Fireworksrainbow'
    properties = presets.get_preset_by_name(test_preset_string)
    print(test_preset_string, flush=True)
    print(properties, flush=True)

    test_preset_string = '17'
    properties = presets.get_preset_by_name(test_preset_string)
    print(test_preset_string, flush=True)
    print(properties, flush=True)

    test_preset_string = 'TriChaseXmas'
    properties = presets.get_preset_by_name(test_preset_string)
    print(test_preset_string, flush=True)
    print(properties, flush=True)

    test_preset_string = 'Valentines'
    properties = presets.get_preset_by_name(test_preset_string)
    print(test_preset_string, flush=True)
    print(properties, flush=True)

    test_preset_string = 'chicken'
    properties = presets.get_preset_by_name(test_preset_string)
    print(test_preset_string, flush=True)
    print(properties, flush=True)