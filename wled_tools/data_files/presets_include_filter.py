from presets_filter import PresetsFilter


class PresetsIncludeFilter(PresetsFilter):

    def __init__(self, presets_in, deep: bool):
        super().__init__(presets_in, deep, {})

    def apply_filter_item(self, preset_id: str):
        if preset_id not in self.presets_out:
            self.presets_out[preset_id] = self.presets_in[preset_id]
        return self.presets_in[preset_id]

    def initialize_filter(self):
        self.presets_out['0'] = self.presets_in['0']

    def finalize_filter(self):
        pass
