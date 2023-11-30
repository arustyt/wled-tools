from abc import abstractmethod

from presets import Presets

PLAYLIST_TAG = 'playlist'
PLAYLIST_PRESETS_TAG = 'ps'


class PresetsFilter:

    def __init__(self, presets_in: dict, deep: bool, presets_out: dict):
        self.presets_in = presets_in
        self.deep = deep
        self.presets_out = presets_out.copy()
        self.presets = Presets(presets_data=presets_in)

    def apply(self, filter_list: list):
        self.initialize_filter()

        for filter_item in filter_list:
            preset_identifiers = self.presets.get_preset_by_name(filter_item)
            self.process_filter_item(str(preset_identifiers['id']))

        self.finalize_filter()

        self.adjust_presets()

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
    def initialize_filter(self):
        pass

    @abstractmethod
    def finalize_filter(self):
        pass

    def is_playlist(self, preset):
        return PLAYLIST_TAG in preset and PLAYLIST_PRESETS_TAG in preset[PLAYLIST_TAG]

    def get_playlist_presets(self, preset):
        return preset[PLAYLIST_TAG][PLAYLIST_PRESETS_TAG]

    def adjust_presets(self):
        preset_map = self.renumber_presets()
        self.update_all_playlist_presets(preset_map)

    def renumber_presets(self):
        preset_ids = []
        preset_map = {}
        next_id = 0
        for key in self.presets_out.keys():
            preset_ids.append(int(key))
        preset_ids.sort()
        for preset_id in preset_ids:
            next_id_str = str(next_id)
            preset_id_str = str(preset_id)
            if preset_id != next_id:
                self.presets_out[next_id_str] = self.presets_out[preset_id_str]
                del self.presets_out[preset_id_str]

            preset_map[preset_id_str] = next_id_str
            next_id += 1

        return preset_map

    def update_all_playlist_presets(self, preset_map):
        for preset_id_str, preset in self.presets_out.items():
            if self.is_playlist(preset):
                self.update_playlist_presets(preset, preset_map)

    def update_playlist_presets(self, preset, preset_map):
        playlist_presets: list = self.get_playlist_presets(preset)

        for idx in range(0, len(playlist_presets)):
            playlist_preset = playlist_presets[idx]
            try:
                int(playlist_preset)
                playlist_presets[idx] = preset_map[str(playlist_preset)]
            except:
                pass
