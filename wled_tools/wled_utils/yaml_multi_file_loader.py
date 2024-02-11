import yaml


def load_yaml_files(yaml_file_list, merge_lists=True):
    yaml_data = {}

    for yaml_file in yaml_file_list:
        yaml_data = add_yaml_file(yaml_file, yaml_data, merge_lists)

    return yaml_data


def load_yaml_file(yaml_file):
    yaml_data = {}
    yaml_data = add_yaml_file(yaml_file, yaml_data)
    return yaml_data


def add_yaml_file(yaml_file, yaml_data, merge_lists=True):
    with open(yaml_file) as in_file:
        new_yaml_data: dict = yaml.safe_load(in_file)
        for key in new_yaml_data.keys():
            if key not in yaml_data:
                yaml_data[key] = new_yaml_data[key]
            elif merge_lists and isinstance(yaml_data[key], list):
                yaml_data[key].extend(new_yaml_data[key])
            else:
                raise ValueError('Duplicate keys in yaml file: file = {file}, key = {key}'.format(file=yaml_file, key=key))

    return yaml_data
