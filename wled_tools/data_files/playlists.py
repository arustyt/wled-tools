from wled_constants import (PRESET_NAME_TAG, PLAYLIST_TAG, PLAYLIST_PRESETS_TAG, PLAYLIST_DURATION_TAG,
                            PLAYLIST_TRANSITION_TAG)


class Playlists:

    def __init__(self, merge_duplicates):
        self.merge_duplicates = merge_duplicates
        self.playlist_presets = {}

    def add(self, playlist_preset):
        if PLAYLIST_TAG not in playlist_preset:
            raise ValueError("Preset is not a playlist: {ps}".format(ps=playlist_preset))

        if PRESET_NAME_TAG in playlist_preset:
            name = playlist_preset[PRESET_NAME_TAG]
            if name not in self.playlist_presets:
                is_new_preset = self.add_playlist_preset(name, playlist_preset)
            else:
                if self.merge_duplicates:
                    is_new_preset = self.merge_playlist_preset(name, playlist_preset)
                else:
                    raise ValueError("Duplicate playlist name: {name}".format(name=name))
        else:
            raise ValueError("Playlist is unnamed: {pl}".format(pl=playlist_preset))

        return is_new_preset

    def add_playlist_preset(self, name, playlist_preset):
        self.playlist_presets[name] = playlist_preset
        return True

    def merge_playlist_preset(self, name, playlist_preset):
        self.merge_playlist(self.playlist_presets[name][PLAYLIST_TAG], playlist_preset[PLAYLIST_TAG])
        return False

    def merge_playlist(self, existing_playlist, new_playlist):
        self.merge_lists(existing_playlist, new_playlist)
        self.add_new_items(existing_playlist, new_playlist)

    def add_new_items(self, existing_playlist, new_playlist):
        for key in new_playlist:
            if key not in existing_playlist:
                existing_playlist[key] = new_playlist[key]

    def merge_lists(self, existing_playlist, new_playlist):
        for key in existing_playlist:
            if key == PLAYLIST_DURATION_TAG:
                existing_playlist[PLAYLIST_DURATION_TAG].extend(new_playlist[PLAYLIST_DURATION_TAG])
            elif key == PLAYLIST_PRESETS_TAG:
                existing_playlist[PLAYLIST_PRESETS_TAG].extend(new_playlist[PLAYLIST_PRESETS_TAG])
            elif key == PLAYLIST_TRANSITION_TAG:
                existing_playlist[PLAYLIST_TRANSITION_TAG].extend(new_playlist[PLAYLIST_TRANSITION_TAG])
