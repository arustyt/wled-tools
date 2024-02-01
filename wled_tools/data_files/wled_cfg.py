import json
import sys

from data_files.presets import Presets
from data_files.wled_data_processor import WledDataProcessor

DEFAULT_PRESET_PATH = 'def.ps'


class WledCfg(WledDataProcessor):

    def __init__(self, **kwargs):
        super().__init__()

        self.presets = Presets(kwdict=kwargs)

    def handle_dict_element(self, path: str, name, data):
        if path == DEFAULT_PRESET_PATH:
            return self.process_default_preset_name(path, name, data)
        else:
            return (name, data),

    def process_default_preset_name(self, path, name, data):
        preset_data = self.presets.get_preset_by_name(data)
        return (name, preset_data['id']),


if __name__ == '__main__':
    wled_cfg = WledCfg()
    json_data = wled_cfg.process_wled_data(sys.argv[1])
    json_string = json.dumps(json_data, indent=2)

    print(json_string)
