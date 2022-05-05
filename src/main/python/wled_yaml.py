import sys
import json
from abc import abstractmethod

import yaml


DEFAULTS = 'defaults'


class WledYaml:

    def __init__(self):
        pass

    @abstractmethod
    def process_yaml_file(self, yaml_file_name, **other_args):
        self.process_other_args(other_args)
        yaml_data = self.load_yaml_file(yaml_file_name)

        new_preset_data = {}

        self.load_global_defaults(yaml_data)

        for key in yaml_data.keys():
            if key == DEFAULTS:
                continue
            preset = yaml_data[key]
            self.load_defaults(key, key, preset)
            if isinstance(preset, dict):
                new_preset_data[key] = self.process_dict(key, key, preset)
            elif isinstance(preset, list):
                new_preset_data[key] = self.process_list(key, key, preset)
            else:
                replacements = self.process_dict_element(key, key, preset)
                if len(replacements) >= 1:
                    for replacement in replacements:
                        new_preset_data[replacement[0]] = replacement[1]

        return new_preset_data

    def load_yaml_file(self, yaml_file_name):
        with open(yaml_file_name) as in_file:
            yaml_data = yaml.safe_load(in_file)
        return yaml_data

    def process_dict(self, path: str, name, data: dict):
        new_data = self.init_dict(path, name, data)

        handled, new_data = self.handle_dict(path, name, data, new_data)

        if not handled:
            self.process_dict_keys(path, data, new_data)

        self.finalize_dict(path, name, data, new_data)
        return new_data

    def process_dict_keys(self, path, data, new_data):
        for key in data.keys():
            if key == DEFAULTS:
                continue
            item = data[key]
            new_path = '{name}.{key}'.format(name=path, key=key)
            if isinstance(item, dict):
                new_data[key] = self.process_dict(new_path, key, item)
            elif isinstance(item, list):
                new_data[key] = self.process_list(new_path, key, item)
            else:
                replacements = self.process_dict_element(new_path, key, item)
                if len(replacements) >= 1:
                    for replacement in replacements:
                        new_data[replacement[0]] = replacement[1]

    @abstractmethod
    def init_dict(self, path: str, name, data: dict):
        return {}

    @abstractmethod
    def handle_dict(self, path: str, name, data: dict, new_data: dict):
        return False, new_data

    @abstractmethod
    def finalize_dict(self, path: str, name, data: dict, new_data: dict):
        pass

    def process_list(self, path: str, name, data: list):
        new_data = self.init_list(path, name, data)

        handled, new_data = self.handle_list(path, name, data, new_data)

        if not handled:
            self.process_list_elements(path, data, new_data)

        self.finalize_list(path, name, data, new_data)

        return new_data

    def process_list_elements(self, path, data, new_data):
        index = 0
        for item in data:
            new_path = '{name}[{index}]'.format(name=path, index=index)
            index += 1
            if isinstance(item, dict):
                new_data.append(self.process_dict(new_path, None, item))
            elif isinstance(item, list):
                new_data.append(self.process_list(new_path, None, item))
            else:
                new_data.extend(self.process_list_element(new_path, None, item))

    @abstractmethod
    def init_list(self, path: str, name, data: list):
        return []

    @abstractmethod
    def handle_list(self, path: str, name, data: list, new_data: list):
        return False, new_data

    @abstractmethod
    def finalize_list(self, path: str, name, data: list, new_data: list):
        pass

    @abstractmethod
    def process_dict_element(self, path: str, name, data):
        return (name, data),

    @abstractmethod
    def process_list_element(self, path: str, name, data):
        return [data]

    @abstractmethod
    def load_global_defaults(self, yaml_data: {}):
        pass

    def load_defaults(self, path, name, defaults):
        pass

    @abstractmethod
    def process_other_args(self, other_args):
        pass
