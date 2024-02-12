from data_files.playlists import Playlists
from data_files.preset_id_manager import PresetIdManager
from data_files.presets import Presets
from wled_constants import DEFAULTS_TAG, PRESETS_TAG, ID_TAG, PLAYLIST_TAG


class PresetDataNormalizer:

    def __init__(self, preset_data: dict, merge_duplicate_playlists=False):
        self.original_preset_data = preset_data
        self.normalized_preset_data = {}
        self.preset_id_manager = PresetIdManager(preset_data)
        self.playlists = Playlists(merge_duplicate_playlists)
        self.presets = None

    def normalize(self):
        for key in self.original_preset_data.keys():
            if key == DEFAULTS_TAG:
                self.normalized_preset_data[DEFAULTS_TAG] = self.original_preset_data[DEFAULTS_TAG]
            elif key == PRESETS_TAG:
                self.process_presets_tag(self.original_preset_data[PRESETS_TAG])
            else:
                self.process_preset(key, self.original_preset_data[key])

        self.presets = Presets(presets_data=self.normalized_preset_data)

        return self.normalized_preset_data

    def get_normalized_data(self):
        return self.normalized_preset_data

    def process_presets_tag(self, presets: list):
        for preset_data in presets:
            if ID_TAG in preset_data:
                preset_id = str(preset_data[ID_TAG])
                preset_data.pop(ID_TAG)
            else:
                preset_id = None

            self.include_preset_data(preset_id, preset_data)

    def process_preset(self, preset_id: str, preset_data: dict):
        self.include_preset_data(preset_id, preset_data)

    def include_preset_data(self, preset_id: str, preset_data: dict):
        if self.is_playlist_preset(preset_data):
            is_new_preset = self.playlists.add(preset_data)
            if is_new_preset:
                self.add_preset(preset_id, preset_data)
        else:
            self.add_preset(preset_id, preset_data)

    def add_preset(self, preset_id, preset_data):
        if preset_id is None:
            preset_id = self.preset_id_manager.get_next_preset_id()
        self.normalized_preset_data[preset_id] = preset_data

    def is_playlist_preset(self, preset):
        return PLAYLIST_TAG in preset

