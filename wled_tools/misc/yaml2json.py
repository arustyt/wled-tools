import json
import sys

import yaml

with open(sys.argv[1]) as f:
    preset_data = json.dumps(yaml.safe_load(f))

print(str(preset_data))
