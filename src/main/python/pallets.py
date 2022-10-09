import re

import yaml


class Pallets:

    def __init__(self, pallet_names_file='pallets.yaml'):
        with open(pallet_names_file) as f:
            pallet_data = yaml.safe_load(f)

        self.pallets_by_name = {}
        for pallet in pallet_data['pallets']:
            pallet_name_normalized = self.normalize_pallet_name(pallet['name'])
            self.pallets_by_name[pallet_name_normalized] = (('name', pallet['name']), ('id', pallet['id']),
                                                            ('desc', pallet['desc']))

    def normalize_pallet_name(self, pallet_name):
        pallet_name_normalized = str(pallet_name).lower()
        pallet_name_normalized = re.sub('[ _]', '', pallet_name_normalized)
        return pallet_name_normalized

    #  Returns tuple containing pallet data: (name, id, desc)
    def get_pallet_by_name(self, pallet_string):
        pallet_data = None
        pallet_string_normalized = self.normalize_pallet_name(pallet_string)
        if pallet_string_normalized in self.pallets_by_name:
            pallet_data = self.pallets_by_name[pallet_string_normalized]
        else:
            raise ValueError("Input '{name}' is not a recognized pallet name".format(name=pallet_string))

        return pallet_data


if __name__ == '__main__':
    pallets = Pallets()
    test_pallet_string = 'default'
    properties = pallets.get_pallet_by_name(test_pallet_string)
    print(test_pallet_string, flush=True)
    print(properties, flush=True)

    test_pallet_string = 'Color 1'
    properties = pallets.get_pallet_by_name(test_pallet_string)
    print(test_pallet_string, flush=True)
    print(properties, flush=True)

    test_pallet_string = 'hult_64'
    properties = pallets.get_pallet_by_name(test_pallet_string)
    print(test_pallet_string, flush=True)
    print(properties, flush=True)

    test_pallet_string = 'Hult 65'
    properties = pallets.get_pallet_by_name(test_pallet_string)
    print(test_pallet_string, flush=True)
    print(properties, flush=True)
