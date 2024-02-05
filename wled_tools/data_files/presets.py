import re

from wled_constants import DEFAULTS
from wled_utils.logger_utils import get_logger

PRESETS_DATA_ARG = 'presets_data'
KWDICT_ARG = 'kwdict'


class Presets:

    def __init__(self, env, **kwargs):

        self.env = env

        if KWDICT_ARG in kwargs:
            kwargs = kwargs[KWDICT_ARG]

        presets_data = kwargs[PRESETS_DATA_ARG] if PRESETS_DATA_ARG in kwargs else None

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
    def get_preset_by_name(self, preset_string: str):
        preset_string_normalized = self.normalize_preset_name(preset_string)
        if preset_string_normalized in self.presets_by_name:
            preset_data = self.presets_by_name[preset_string_normalized]
        else:
            err_msg = 'Input "{name}" is not a recognized preset name or id'.format(name=preset_string)
            raise ValueError(err_msg)

        return dict(preset_data)


if __name__ == '__main__':
    presets = Presets('presets-new.yaml')
    test_preset_string = 'Fireworksrainbow'
    properties = presets.get_preset_by_name(test_preset_string)
    get_logger().info(test_preset_string, flush=True)
    get_logger().info(properties, flush=True)

    test_preset_string = '17'
    properties = presets.get_preset_by_name(test_preset_string)
    get_logger().info(test_preset_string, flush=True)
    get_logger().info(properties, flush=True)

    test_preset_string = 'TriChaseXmas'
    properties = presets.get_preset_by_name(test_preset_string)
    get_logger().info(test_preset_string, flush=True)
    get_logger().info(properties, flush=True)

    test_preset_string = 'Valentines'
    properties = presets.get_preset_by_name(test_preset_string)
    get_logger().info(test_preset_string, flush=True)
    get_logger().info(properties, flush=True)

    test_preset_string = 'chicken'
    properties = presets.get_preset_by_name(test_preset_string)
    get_logger().info(test_preset_string, flush=True)
    get_logger().info(properties, flush=True)