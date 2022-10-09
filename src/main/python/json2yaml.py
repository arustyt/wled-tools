import sys
import json
import yaml


def get_yaml_file_name(json_file_name: str):
    yaml_file_name = json_file_name.replace('.json', '.yaml', 1)
    return yaml_file_name


json_file = sys.argv[1]
json_data = json.load(open(json_file))
#  print(yaml.dump(json_data, default_flow_style=False))

yaml_file = get_yaml_file_name(json_file)
with open(yaml_file, "w", newline='\n') as out_file:
    out_file.write(yaml.dump(json_data, default_flow_style=False))


