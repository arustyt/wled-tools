from data_files.presets_filter import PresetsFilter


class PresetsExcludeFilter(PresetsFilter):

    def __init__(self, presets_in, deep: bool):
        super().__init__(presets_in, deep, presets_in)

    def apply_filter_item(self, preset_id: str):
        if preset_id in self.presets_out:
            del self.presets_out[preset_id]
        return self.presets_in[preset_id]

    def initialize_filter(self):
        pass

    def finalize_filter(self):
        pass
