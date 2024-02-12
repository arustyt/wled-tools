import json
import os
from os.path import exists

import yaml

from data_files.presets_exclude_filter import PresetsExcludeFilter
from data_files.presets_include_filter import PresetsIncludeFilter
from data_files.wled_file_processor import WledFileProcessor
from data_files.wled_presets import WledPresets
from wled_utils.logger_utils import get_logger
from wled_utils.yaml_multi_file_loader import load_yaml_files


class PresetsFileProcessor(WledFileProcessor):

    def __init__(self, presets_paths, segments_path, environment, palettes_path, effects_path, colors_path,
                 include_list, exclude_list, deep, output_dir, placeholder_replacer, suffix, test_mode, quiet_mode,
                 merge_playlists: bool):
        super().__init__(output_dir, placeholder_replacer, suffix, test_mode, quiet_mode)
        self.presets_paths = presets_paths
        self.segments_path = segments_path
        self.environment = environment
        self.palettes_path = palettes_path
        self.effects_path = effects_path
        self.colors_path = colors_path
        self.include_list = include_list
        self.exclude_list = exclude_list
        self.deep = deep
        self.merge_playlists = merge_playlists
        self.presets_data = None

    def process(self):
        if self.presets_paths is not None:
            if not self.quiet_mode:
                get_logger().info("PROCESSING PRESETS ...")
            wled_presets = WledPresets(self.environment, self.colors_path, self.palettes_path, self.effects_path)
            if not self.quiet_mode:
                get_logger().info("  Processing {file}".format(file=self.presets_paths))

            raw_presets_data = load_yaml_files(self.presets_paths)

            if self.placeholder_replacer is not None:
                prepped_presets_data = self.placeholder_replacer.process_wled_data(raw_presets_data)
            else:
                prepped_presets_data = raw_presets_data

            self.presets_data = wled_presets.process_wled_data(prepped_presets_data, segments_file=self.segments_path,
                                                               merge_playlists=self.merge_playlists)

            if len(self.presets_paths) > 1:
                yaml_file_path = self.get_output_file_name(self.presets_paths[0],
                                                           "{suffix}{env}-merged".
                                                           format(suffix=self.suffix,
                                                                  env="-" + self.environment
                                                                  if self.environment is not None else ""),
                                                           'yaml')
                if not self.test_mode:
                    if not self.quiet_mode:
                        get_logger().info("  Saving merged YAML to {file}".format(file=yaml_file_path))
                    dir_name = os.path.dirname(yaml_file_path)
                    os.makedirs(dir_name, mode=0o777, exist_ok=True)
                    with open(yaml_file_path, "w", newline='\n') as out_file:
                        yaml.dump(self.presets_data, out_file, indent=2)
                else:
                    if not self.quiet_mode:
                        get_logger().info("  Would have saved merged YAML to {file}".format(file=yaml_file_path))

            if self.include_list is not None:
                include_filter = PresetsIncludeFilter(self.presets_data, self.deep)
                self.presets_data = include_filter.apply(self.include_list)
            elif self.exclude_list is not None:
                exclude_filter = PresetsExcludeFilter(self.presets_data, self.deep)
                self.presets_data = exclude_filter.apply(self.exclude_list)

            self.json_file_path = self.get_output_file_name(self.presets_paths[0],
                                                            "{suffix}{env}".format(suffix=self.suffix,
                                                                                   env="-" + self.environment
                                                                                   if self.environment is not None else ""))
            if not self.test_mode:
                if exists(self.json_file_path):
                    self.rename_existing_file(self.json_file_path)
                if not self.quiet_mode:
                    get_logger().info("  Generating {file}".format(file=self.json_file_path))
                with open(self.json_file_path, "w", newline='\n') as out_file:
                    json.dump(self.presets_data, out_file, indent=2)
                    self.json_file_path = self.json_file_path
            else:
                if not self.quiet_mode:
                    get_logger().info("  Would have generated {file}".format(file=self.json_file_path))

    def get_processed_data(self):
        return self.presets_data
