import sys
import json
from abc import abstractmethod

import yaml

from presets_filter import PresetsFilter


class PresetsIncludeFilter(PresetsFilter):

    def __init__(self, presets_in, deep: bool):
        super().__init__(presets_in, deep, {})

    def apply_filter_item(self, preset_id: str):
        self.presets_out[preset_id] = self.presets_in[preset_id]
        return self.presets_in[preset_id]

    def init_filter(self):
        self.presets_out['0'] = self.presets_in['0']
