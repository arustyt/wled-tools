import json
from os.path import exists

from data_files.wled_cfg import WledCfg
from data_files.wled_file_processor import WledFileProcessor
from wled_utils.logger_utils import get_logger
from wled_utils.yaml_multi_file_loader import load_yaml_files


class CfgFileProcessor(WledFileProcessor):

    def __init__(self, cfg_paths, presets_data, output_dir, placeholder_replacer, suffix, test_mode, quiet_mode):
        super().__init__(output_dir, placeholder_replacer, suffix, test_mode, quiet_mode)
        self.cfg_paths = cfg_paths
        self.presets_data = presets_data
        self.cfg_data = None

    def process(self):
        if self.cfg_paths is not None:
            if not self.quiet_mode:
                get_logger().info("\nPROCESSING CFG ...")
            wled_cfg = WledCfg(presets_data=self.presets_data)
            if not self.quiet_mode:
                get_logger().info("  Processing {file}".format(file=self.cfg_paths))

            raw_cfg_data = load_yaml_files(self.cfg_paths)

            if self.placeholder_replacer is not None:
                prepped_cfg_data = self.placeholder_replacer.process_wled_data(raw_cfg_data)
            else:
                prepped_cfg_data = raw_cfg_data

            self.cfg_data = wled_cfg.process_wled_data(prepped_cfg_data)
            json_file_path = self.get_output_file_name(self.cfg_paths[0], self.suffix)
            if not self.test_mode:
                if exists(json_file_path):
                    self.rename_existing_file(json_file_path)
                if not self.quiet_mode:
                    get_logger().info("  Generating {file}".format(file=json_file_path))
                with open(json_file_path, "w", newline='\n') as out_file:
                    json.dump(self.cfg_data, out_file, indent=2)
                    self.json_file_path = json_file_path
            else:
                if not self.quiet_mode:
                    get_logger().info("  Would have generated {file}".format(file=json_file_path))

    def get_processed_data(self):
        return self.cfg_data

