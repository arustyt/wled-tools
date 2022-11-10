import re

import yaml

from wled_constants import NAME_TAG, PALETTES_TAG, ID_TAG, DESCRIPTION_TAG, ALIASES_TAG
from wled_definitions import WledDefinitions


class Palettes(WledDefinitions):

    def __init__(self, definitions_file='palettes.yaml'):
        super().__init__(definitions_file, PALETTES_TAG)


if __name__ == '__main__':
    palettes = Palettes('../../../etc/palettes.yaml')
    test_palette_string = 'default'
    properties = palettes.get_by_name(test_palette_string)
    print(test_palette_string, flush=True)
    print(properties, flush=True)

    test_palette_string = 'Color 1'
    properties = palettes.get_by_name(test_palette_string)
    print(test_palette_string, flush=True)
    print(properties, flush=True)

    test_palette_string = 'hult_64'
    properties = palettes.get_by_name(test_palette_string)
    print(test_palette_string, flush=True)
    print(properties, flush=True)

    test_palette_string = 'Hult 65'
    try:
        properties = palettes.get_by_name(test_palette_string)
        print("Test Failed: Expected ValueError.", flush=True)
    except ValueError:
        print(test_palette_string, flush=True)
        print("Caused ValueError, as expected.", flush=True)

    test_palette_id = 27
    properties = palettes.get_by_id(test_palette_id)
    print(test_palette_id, flush=True)
    print(properties, flush=True)
