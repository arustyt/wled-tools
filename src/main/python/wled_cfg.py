import sys
import json

from presets import Presets
from wled_yaml import WledYaml

DEFAULT_PRESET_PATH = 'def.ps'

class WledCfg(WledYaml):

    def __init__(self, presets_yaml_file='presets.yaml'):
        super().__init__()
        self.presets = Presets(presets_yaml_file)

    def process_dict_element(self, path: str, name, data):
        if path == DEFAULT_PRESET_PATH:
            return self.process_default_preset_name(path, name, data)
        else:
            return (name, data),

    def process_default_preset_name(self, path, name, data):
        preset_data = self.presets.get_preset_by_name(data)
        return (name, preset_data['id']),


if __name__ == '__main__':
    wled_cfg = WledCfg()
    json_data = wled_cfg.process_yaml_file(sys.argv[1])
    json_string = json.dumps(json_data, indent=2)

    print(json_string)
