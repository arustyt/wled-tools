from abc import abstractmethod

from wled_constants import DEFAULTS


class WledDataProcessor:

    def __init__(self, environment: str):
        self.environment = environment
        self.raw_wled_data = None

    def process_wled_data(self, raw_wled_data, **other_args):
        self.process_other_args(raw_wled_data, other_args)
        new_wled_data = {}

        self.raw_wled_data = raw_wled_data

        self.load_global_defaults()

        for key in self.raw_wled_data.keys():
            if key == DEFAULTS:
                defaults = self.handle_defaults(self.raw_wled_data[DEFAULTS])
                if defaults is not None:
                    new_wled_data[DEFAULTS] = defaults
            else:
                wled_element = self.raw_wled_data[key]
                self.apply_defaults(key, key, wled_element)
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

    @abstractmethod
    def handle_defaults(self, defaults_dict):
        return None

    def process_dict(self, path: str, name, data: dict):
        new_data = self.init_dict(path, name, data)

        handled, new_data = self.handle_dict(path, name, data, new_data)

        if not handled:
            self.process_dict_content(path, data, new_data)

        self.finalize_dict(path, name, data, new_data)
        return new_data

    def process_dict_content(self, path, data, new_data):
        for key in data.keys():
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
            self.process_list_content(path, data, new_data)

        self.finalize_list(path, name, data, new_data)

        return new_data

    def process_list_content(self, path, data, new_data):
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

    def apply_defaults(self, path, name, defaults):
        pass

    @abstractmethod
    def process_other_args(self, raw_wled_data, other_args):
        pass

    @abstractmethod
    def finalize_wled_data(self, wled_data):
        return wled_data
