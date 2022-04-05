import sys
import json
import yaml

with open(sys.argv[1]) as f:
    print(json.dumps(yaml.safe_load(f)))

# print(json.dumps(yaml.load(open(sys.argv[1]))))
