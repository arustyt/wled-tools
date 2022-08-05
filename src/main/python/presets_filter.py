import sys
import json
from abc import abstractmethod

import yaml

from presets import Presets

PLAYLIST_TAG = 'playlist'
PLAYLIST_PRESETS_TAG = 'ps'


class PresetsFilter:

    def __init__(self, presets_in: dict, deep: bool, presets_out):
        self.presets_in = presets_in
        self.deep = deep
        self.presets_out = presets_out.copy()
        self.presets = Presets(presets_data=presets_in)

    def apply(self, filter_list: list):
        self.init_filter()

        for filter_item in filter_list:
            preset_identifiers = self.presets.get_preset_by_name(filter_item)
            self.process_filter_item(str(preset_identifiers['id']))

        self.condense_preset_ids()

        return self.presets_out

    def process_filter_item(self, preset_id: str):
        preset = self.apply_filter_item(preset_id)
        if self.deep and self.is_playlist(preset):
            for preset_id in self.get_playlist_presets(preset):
                self.process_filter_item(str(preset_id))

    @abstractmethod
    def apply_filter_item(self, preset_id: str):
        pass

    @abstractmethod
    def init_filter(self):
        pass

    def is_playlist(self, preset):
        return PLAYLIST_TAG in preset and PLAYLIST_PRESETS_TAG in preset[PLAYLIST_TAG]

    def get_playlist_presets(self, preset):
        return preset[PLAYLIST_TAG][PLAYLIST_PRESETS_TAG]

    def condense_preset_ids(self):
        pass
