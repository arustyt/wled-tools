import sys
import json

from wled_yaml import WledYaml


class WledCfg(WledYaml):

    def __init__(self):
        super().__init__()


if __name__ == '__main__':
    wled_cfg = WledCfg()
    json_data = wled_cfg.process_yaml_file(sys.argv[1])
    json_string = json.dumps(json_data, indent=2)

    print(json_string)
