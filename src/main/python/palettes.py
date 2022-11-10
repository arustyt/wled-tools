import re

import yaml

from wled_constants import NAME_TAG, PALETTES_TAG, ID_TAG, DESCRIPTION_TAG, ALIASES_TAG


class Palettes:

    def __init__(self, palette_names_file='palettes.yaml'):
        with open(palette_names_file) as f:
            palette_data = yaml.safe_load(f)

        self.palettes_by_name = {}
        for palette in palette_data[PALETTES_TAG]:
            palette_name_normalized = self.normalize_palette_name(palette[NAME_TAG])
            palette_details = {NAME_TAG: palette[NAME_TAG], ID_TAG: palette[ID_TAG],
                              DESCRIPTION_TAG: palette[DESCRIPTION_TAG]}

            if ALIASES_TAG in palette:
                palette_details[ALIASES_TAG] = palette[ALIASES_TAG]
                for alias in palette[ALIASES_TAG]:
                    alias_name_normalized = self.normalize_palette_name(alias)
                    self.palettes_by_name[alias_name_normalized] = palette_details

            self.palettes_by_name[palette_name_normalized] = palette_details

    def normalize_palette_name(self, palette_name):
        palette_name_normalized = str(palette_name).lower()
        palette_name_normalized = re.sub('[ _]', '', palette_name_normalized)
        return palette_name_normalized

    #  Returns tuple containing palette data: (name, id, desc)
    def get_palette_by_name(self, palette_string):
        palette_data = None
        palette_string_normalized = self.normalize_palette_name(palette_string)
        if palette_string_normalized in self.palettes_by_name:
            palette_data = self.palettes_by_name[palette_string_normalized]
        else:
            raise ValueError("Input '{name}' is not a recognized palette name".format(name=palette_string))

        return palette_data


if __name__ == '__main__':
    palettes = Palettes('../../../etc/palettes.yaml')
    test_palette_string = 'default'
    properties = palettes.get_palette_by_name(test_palette_string)
    print(test_palette_string, flush=True)
    print(properties, flush=True)

    test_palette_string = 'Color 1'
    properties = palettes.get_palette_by_name(test_palette_string)
    print(test_palette_string, flush=True)
    print(properties, flush=True)

    test_palette_string = 'hult_64'
    properties = palettes.get_palette_by_name(test_palette_string)
    print(test_palette_string, flush=True)
    print(properties, flush=True)

    test_palette_string = 'Hult 65'
    try:
        properties = palettes.get_palette_by_name(test_palette_string)
        print("Test Failed: Expected ValueError.", flush=True)
    except ValueError:
        print(test_palette_string, flush=True)
        print("Caused ValueError, as expected.", flush=True)
