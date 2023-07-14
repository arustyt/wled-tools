import json
from os.path import exists

import yaml

from presets_exclude_filter import PresetsExcludeFilter
from presets_include_filter import PresetsIncludeFilter
from wled_file_processor import WledFileProcessor
from wled_presets import WledPresets
from yaml_multi_file_loader import load_yaml_files


class PresetsFileProcessor(WledFileProcessor):

    def __init__(self, presets_paths, segments_path, environment, palettes_path, effects_path, colors_path,
                 include_list, exclude_list, deep, placeholder_replacer, suffix, test_mode):
        super().__init__(placeholder_replacer, suffix, test_mode)
        self.presets_paths = presets_paths
        self.segments_path = segments_path
        self.environment = environment
        self.palettes_path = palettes_path
        self.effects_path = effects_path
        self.colors_path = colors_path
        self.include_list = include_list
        self.exclude_list = exclude_list
        self.deep = deep
        self.presets_data = None

    def process(self):
        if self.presets_paths is not None:
            print("\nPROCESSING PRESETS ...")
            wled_presets = WledPresets(self.colors_path, self.palettes_path, self.effects_path)
            print("  Processing {file}".format(file=self.presets_paths))

            raw_presets_data = load_yaml_files(self.presets_paths)

            if self.placeholder_replacer is not None:
                prepped_presets_data = self.placeholder_replacer.process_wled_data(raw_presets_data)
            else:
                prepped_presets_data = raw_presets_data

            self.presets_data = wled_presets.process_wled_data(prepped_presets_data, segments_file=self.segments_path)

            if len(self.presets_paths) > 1:
                yaml_file_path = self.get_output_file_name(self.presets_paths[0],
                                                           "{suffix}{env}-merged".
                                                           format(suffix=self.suffix,
                                                                  env="-" + self.environment
                                                                  if self.environment is not None else ""),
                                                           'yaml')
                if not self.test_mode:
                    print("  Saving merged YAML to {file}".format(file=yaml_file_path))
                    with open(yaml_file_path, "w", newline='\n') as out_file:
                        yaml.dump(self.presets_data, out_file, indent=2)
                else:
                    print("  Would have saved merged YAML to {file}".format(file=yaml_file_path))

            if self.include_list is not None:
                include_filter = PresetsIncludeFilter(self.presets_data, self.deep)
                self.presets_data = include_filter.apply(self.include_list)
            elif self.exclude_list is not None:
                exclude_filter = PresetsExcludeFilter(self.presets_data, self.deep)
                self.presets_data = exclude_filter.apply(self.exclude_list)

            json_file_path = self.get_output_file_name(self.presets_paths[0],
                                                       "{suffix}{env}".format(suffix=self.suffix,
                                                                              env="-" + self.environment
                                                                              if self.environment is not None else ""))
            if not self.test_mode:
                if exists(json_file_path):
                    self.rename_existing_file(json_file_path)
                print("  Generating {file}".format(file=json_file_path))
                with open(json_file_path, "w", newline='\n') as out_file:
                    json.dump(self.presets_data, out_file, indent=2)
            else:
                print("  Would have generated {file}".format(file=json_file_path))

    def get_processed_data(self):
        return self.presets_data
