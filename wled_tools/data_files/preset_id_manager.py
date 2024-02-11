from wled_constants import DEFAULTS_TAG, PRESETS_TAG, ID_TAG


class PresetIdManager:

    def __init__(self, wled_data: dict):
        self.preset_ids = set()
        self.max_preset_id = 0
        for key in wled_data.keys():
            if key == DEFAULTS_TAG:
                continue
            if key == PRESETS_TAG:
                self.process_presets_tag(wled_data[PRESETS_TAG])
            else:
                self.process_preset(key, wled_data[key])

    def process_presets_tag(self, presets):
        for preset in presets:
            if ID_TAG in preset:
                preset_id = int(preset[ID_TAG])
                self.add_preset(preset_id)

    def add_preset(self, preset_id):
        if preset_id in self.preset_ids:
            raise ValueError("Duplicate preset ID: {pid}".format(pid=preset_id))

        self.preset_ids.add(preset_id)
        if preset_id > self.max_preset_id:
            self.max_preset_id = preset_id

    def process_preset(self, preset_id, preset):
        self.add_preset(int(preset_id))

    def get_next_preset_id(self):
        self.max_preset_id += 1
        preset_id = self.max_preset_id
        self.preset_ids.add(preset_id)
        return preset_id

