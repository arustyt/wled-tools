import sys
import json
from abc import abstractmethod

import yaml

from yaml_multi_file_loader import load_yaml_files

DEFAULTS = 'defaults'


class WledYaml:

    def __init__(self):
        self.yaml_data = None

    @abstractmethod
    def process_yaml_file(self, yaml_file_names, **other_args):
        self.process_other_args(yaml_file_names, other_args)
        new_wled_data = {}

        self.yaml_data = load_yaml_files(yaml_file_names)

        self.load_global_defaults()

        for key in self.yaml_data.keys():
            if key == DEFAULTS:
                continue
            wled_element = self.yaml_data[key]
            self.load_defaults(key, key, wled_element)
            if isinstance(wled_element, dict):
                new_wled_data[key] = self.process_dict(key, key, wled_element)
            elif isinstance(wled_element, list):
                new_wled_data[key] = self.process_list(key, key, wled_element)
            else:
                replacements = self.process_dict_element(key, key, wled_element)
                if len(replacements) >= 1:
                    for replacement in replacements:
                        new_wled_data[replacement[0]] = replacement[1]

        new_wled_data = self.finalize_wled_data(new_wled_data)

        return new_wled_data

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
    def load_global_defaults(self):
        pass

    def load_defaults(self, path, name, defaults):
        pass

    @abstractmethod
    def process_other_args(self, yaml_file_name, other_args):
        pass

    @abstractmethod
    def finalize_wled_data(self, wled_data):
        return wled_data
