import sys
from itertools import combinations, permutations

from wled_utils.logger_utils import get_logger
from wled_utils.trace_tools import Tracer


class PropertyEvaluator:

    def __init__(self, dict_data: dict, *, verbose=False, strings_only=True):
        self.dict_data = dict_data
        self.verbose = verbose
        self.tracer = Tracer(verbose)
        self.strings_only = strings_only

    def add_property(self, name: str, value):
        name_parts = name.split('.')
        num_parts = len(name_parts)
        part_num = 0
        curr_dict = self.dict_data
        while part_num < num_parts-1:
            new_dict = dict()
            curr_dict[name_parts[part_num]] = new_dict
            curr_dict = new_dict
            part_num += 1

        curr_dict[name_parts[num_parts-1]] = value

    def add_properties(self, properties):
        for prop in properties:
            self.add_property(prop[0], prop[1])

    def get_property(self, *key_parts: str, ):
        property_value, property_name = self.get_property_tuple(*key_parts)

        return property_value

    def get_property_tuple(self, *key_parts: str, ):
        parts_count = len(key_parts)
        if parts_count > 1:
            var_parts = list(key_parts[0:parts_count - 1])
            var_parts = self.remove_empty_values(var_parts)
        else:
            var_parts = []

        last_arg: str = key_parts[parts_count - 1].strip()
        if last_arg.startswith('['):
            closing_bracket = last_arg.find(']')
            if closing_bracket == -1:
                raise ValueError("Missing closing bracket: {value}".format(value=last_arg))
            opt_parts = last_arg[1:closing_bracket]
            var_parts.extend(list(opt_parts.strip('.').split('.')))
            fixed_parts = list(last_arg[closing_bracket+1:].strip('.').split('.'))
        else:
            fixed_parts = list(key_parts[parts_count - 1].strip('.').split('.'))

        if self.verbose:
            get_logger().info("Evaluating property: '{var}', fixed: '{fixed}'".format(var=".".join(var_parts),
                                                                                      fixed=".".join(fixed_parts)))
        property_value = None
        property_name = None
        for candidate in self.candidates(var_parts):
            property_value = self.evaluate_property(candidate, fixed_parts)
            if property_value is not None:
                property_name = self.get_property_name(candidate, fixed_parts)
                if self.strings_only:
                    if isinstance(property_value, dict):
                        raise ValueError(
                            "Property resolves to a dict: {placeholder}".format(placeholder='.'.join(property_name)))
                    if isinstance(property_value, list):
                        raise ValueError(
                            "Property resolves to a list: {placeholder}".format(placeholder='.'.join(property_name)))
                break

        return property_value, property_name

    def remove_empty_values(self, var_parts):
        new_var_parts = []
        for part in var_parts:
            if part is not None and len(part) > 0:
                new_var_parts.append(part)
        return new_var_parts

    def candidates(self, names):
        for i in reversed(range(0, len(names) + 1)):
            for combo in combinations(names, i):
                for perm in permutations(combo):
                    yield perm

    def evaluate_property(self, candidate, fixed_parts):
        property_name_parts = self.get_property_name_as_list(candidate, fixed_parts)
        property_value = self.dict_data
        for name in property_name_parts:
            if name in property_value:
                property_value = property_value[name]
            else:
                property_value = None
                break

        return property_value

    def get_property_name(self, candidate, fixed_parts):
        full_name = self.get_property_name_as_list(candidate, fixed_parts)
        return '.'.join(full_name)

    def get_property_name_as_list(self, candidate, fixed_parts):
        full_name = list(candidate)
        full_name.extend(fixed_parts)
        return full_name


def main(prog_name, args):
    test_data = {"a": {"b": {"c": "something"}},
                 "b": {"c": {"e": "something else", "d": "another thing"}},
                 "c": {"d": "last resort"}, "f": {"g": "lonesome thing"}}

    property_evaluator = PropertyEvaluator(test_data, verbose=True)

    print_result(property_evaluator.get_property_tuple("a", "b", "c.d"))
    print_result(property_evaluator.get_property_tuple("a", "c.d"))
    print_result(property_evaluator.get_property_tuple("a.b.c"))
    print_result(property_evaluator.get_property_tuple("b.c.d"))
    try:
        print_result(property_evaluator.get_property_tuple("b.c"))
    except ValueError as ve:
        print(str(ve))
    print_result(property_evaluator.get_property_tuple("b", "c", "f.g"))


if __name__ == '__main__':
    main(sys.argv[0], sys.argv[1:])
