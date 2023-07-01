from decision_maker import DecisionMaker
from wled_constants import EFFECTS_TAG
from wled_definitions import WledDefinitions


class Effects(WledDefinitions):

    def __init__(self, definitions_file='effects.yaml', decision_maker: DecisionMaker = DecisionMaker()):
        super().__init__(definitions_file, EFFECTS_TAG, decision_maker)


if __name__ == '__main__':
    effects = Effects('../../../etc/effects.yaml')
    test_effect_string = 'Wipe Random'
    properties = effects.get_by_name(test_effect_string)
    print(test_effect_string, flush=True)
    print(properties, flush=True)

    test_effect_string = 'solid'
    properties = effects.get_by_name(test_effect_string)
    print(test_effect_string, flush=True)
    print(properties, flush=True)

    test_effect_string = 'theater_rainbow'
    properties = effects.get_by_name(test_effect_string)
    print(test_effect_string, flush=True)
    print(properties, flush=True)

    test_effect_string = 'Tri Chase'
    properties = effects.get_by_name(test_effect_string)
    print(test_effect_string, flush=True)
    print(properties, flush=True)

    test_effect_string = 'Chase 3'
    properties = effects.get_by_name(test_effect_string)
    print(test_effect_string, flush=True)
    print(properties, flush=True)

    test_effect_string = 'walking'
    try:
        properties = effects.get_by_name(test_effect_string)
        print("Test Failed: Expected ValueError.", flush=True)
    except ValueError:
        print(test_effect_string, flush=True)
        print("Caused ValueError, as expected.", flush=True)
