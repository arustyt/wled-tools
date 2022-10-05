import re

import yaml


class Effects:

    def __init__(self, effect_names_file='effects.yaml'):
        with open(effect_names_file) as f:
            effect_data = yaml.safe_load(f)

        self.effects_by_name = {}
        for effect in effect_data['effects']:
            effect_name_normalized = self.normalize_effect_name(effect['name'])
            self.effects_by_name[effect_name_normalized] = (('name', effect['name']), ('id', effect['id']),
                                                            ('desc', effect['desc']))

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
    effects = Effects()
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

    test_effect_string = 'walking'
    properties = effects.get_effect_by_name(test_effect_string)
    print(test_effect_string, flush=True)
    print(properties, flush=True)
