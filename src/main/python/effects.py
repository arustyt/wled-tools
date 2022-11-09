import re
import yaml

from wled_constants import EFFECTS_TAG, NAME_TAG, ID_TAG, DESCRIPTION_TAG, ALIASES_TAG


class Effects:

    def __init__(self, effect_names_file='effects.yaml'):
        with open(effect_names_file) as f:
            effect_data = yaml.safe_load(f)

        self.effects_by_name = {}
        for effect in effect_data[EFFECTS_TAG]:
            effect_name_normalized = self.normalize_effect_name(effect[NAME_TAG])
            effect_details = {NAME_TAG: effect[NAME_TAG],
                              ID_TAG: effect[ID_TAG],
                              DESCRIPTION_TAG: effect[DESCRIPTION_TAG]}
            if ALIASES_TAG in effect:
                effect_details[ALIASES_TAG] = effect[ALIASES_TAG]
                for alias in effect[ALIASES_TAG]:
                    alias_name_normalized = self.normalize_effect_name(alias)
                    self.effects_by_name[alias_name_normalized] = effect_details

            self.effects_by_name[effect_name_normalized] = effect_details

    def normalize_effect_name(self, effect_name):
        effect_name_normalized = str(effect_name).lower()
        effect_name_normalized = re.sub('[ _]', '', effect_name_normalized)
        return effect_name_normalized

    #  Returns tuple containing effect data: (name, id, desc)
    def get_effect_by_name(self, effect_string):
        effect_data = None
        effect_string_normalized = self.normalize_effect_name(effect_string)
        if effect_string_normalized in self.effects_by_name:
            effect_data = self.effects_by_name[effect_string_normalized]
        else:
            raise ValueError("Input '{name}' is not a recognized effect name".format(name=effect_string))

        return effect_data


if __name__ == '__main__':
    effects = Effects('../../../etc/effects.yaml')
    test_effect_string = 'Wipe Random'
    properties = effects.get_effect_by_name(test_effect_string)
    print(test_effect_string, flush=True)
    print(properties, flush=True)

    test_effect_string = 'solid'
    properties = effects.get_effect_by_name(test_effect_string)
    print(test_effect_string, flush=True)
    print(properties, flush=True)

    test_effect_string = 'theater_rainbow'
    properties = effects.get_effect_by_name(test_effect_string)
    print(test_effect_string, flush=True)
    print(properties, flush=True)

    test_effect_string = 'Tri Chase'
    properties = effects.get_effect_by_name(test_effect_string)
    print(test_effect_string, flush=True)
    print(properties, flush=True)

    test_effect_string = 'Chase 3'
    properties = effects.get_effect_by_name(test_effect_string)
    print(test_effect_string, flush=True)
    print(properties, flush=True)

    test_effect_string = 'walking'
    try:
        properties = effects.get_effect_by_name(test_effect_string)
        print("Test Failed: Expected ValueError.", flush=True)
    except ValueError:
        print(test_effect_string, flush=True)
        print("Caused ValueError, as expected.", flush=True)
