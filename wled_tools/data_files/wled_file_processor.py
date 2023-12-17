import os
from abc import abstractmethod
from os.path import exists

from wled_utils.logger_utils import get_logger


class WledFileProcessor:

    def __init__(self, output_dir, placeholder_replacer, suffix, test_mode, quiet_mode):
        self.placeholder_replacer = placeholder_replacer
        self.suffix = suffix
        self.test_mode = test_mode
        self.quiet_mode = quiet_mode
        self.output_dir = output_dir
        self.json_file_path = None

    @abstractmethod
    def process(self):
        pass

    @abstractmethod
    def get_processed_data(self):
        return None

    def get_output_file_name(self, yaml_file_name: str, suffix: str, extension: str = "json"):
        path_sep = os.sep
        dir_name = os.path.dirname(yaml_file_name)
        file_name = os.path.basename(yaml_file_name)
        file_base_name = file_name.split('.', 1)[0]
        if file_base_name.endswith(suffix):
            output_file_name = '{dir}{sep}{out_dir}{sep}{base_name}.{extension}'.format(dir=dir_name, sep=path_sep,
                                                                                        out_dir=self.output_dir,
                                                                                        base_name=file_base_name,
                                                                                        extension=extension)
        else:
            output_file_name = '{dir}{sep}{out_dir}{sep}{base_name}{suffix}.{extension}'.format(dir=dir_name,
                                                                                                sep=path_sep,
                                                                                                out_dir=self.output_dir,
                                                                                                base_name=file_base_name,
                                                                                                suffix=suffix,
                                                                                                extension=extension)

        return output_file_name

    def rename_existing_file(self, file_path):
        backup_file_path = "{file_path}.backup".format(file_path=file_path)
        if exists(backup_file_path):
            if not self.quiet_mode:
                get_logger().info("  Removing existing backup file: {file}".format(file=backup_file_path))
            os.remove(backup_file_path)

        if not self.quiet_mode:
            get_logger().info("  Renaming existing file from {file}\n                           to {backup_file}".
                  format(file=file_path, backup_file=backup_file_path))
        os.rename(file_path, backup_file_path)

    def get_json_file_path(self):
        return self.json_file_path
