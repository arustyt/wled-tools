import os
from abc import abstractmethod
from os.path import exists


class WledFileProcessor:

    def __init__(self, placeholder_replacer, suffix, test_mode):
        self.placeholder_replacer = placeholder_replacer
        self.suffix = suffix
        self.test_mode = test_mode

    @abstractmethod
    def process(self):
        pass

    @abstractmethod
    def get_processed_data(self):
        return None

    def get_output_file_name(self, yaml_file_name: str, suffix: str, extension: str = "json"):
        file_base_name = yaml_file_name.replace('.yaml', '', 1)
        if file_base_name.endswith(suffix):
            json_file_name = '{base_name}.{extension}'.format(base_name=file_base_name, extension=extension)
        else:
            json_file_name = '{base_name}{suffix}.{extension}'.format(base_name=file_base_name, suffix=suffix,
                                                                      extension=extension)

        return json_file_name

    def rename_existing_file(self, file_path):
        backup_file_path = "{file_path}.backup".format(file_path=file_path)
        if exists(backup_file_path):
            print("  Removing existing backup file: {file}".format(file=backup_file_path))
            os.remove(backup_file_path)

        print("  Renaming existing file from {file}\n                           to {backup_file}".
              format(file=file_path, backup_file=backup_file_path))
        os.rename(file_path, backup_file_path)



