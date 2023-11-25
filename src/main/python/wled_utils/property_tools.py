import sys
from wled_utils.trace_tools import Tracer


class PropertyEvaluator:
    
    def __init__(self, dict_data: dict, verbose=False):
        self.dict_data = dict_data
        self.verbose = verbose
        self.tracer = Tracer(verbose)

    def get_property(self, *key_parts: str, ):
        property_value, property_name = self.get_property_tuple(*key_parts)

        return property_value

    def get_property_tuple(self, *key_parts: str, ):
        parts_count = len(key_parts)
        var_parts = list(key_parts[0:parts_count - 1])
        fixed_parts = list(key_parts[parts_count - 1].split('.'))
    
        if self.verbose:
            print("\nEvaluating variable: '{var}', fixed: '{fixed}'".format(var=".".join(var_parts), fixed=".".join(fixed_parts)))
    
        property_value, property_name = self.evaluate_with_all_var_parts(var_parts, fixed_parts)
    
        if property_value is None:
            property_value, property_name = self.evaluate_eliminating_var_parts(var_parts, fixed_parts)

        if property_value is None:
            property_value, property_name = self.evaluate_fixed_parts(fixed_parts)

        return property_value, property_name

    def evaluate_with_all_var_parts(self, var_parts: list, fixed_parts: list):
        if self.verbose:
            self.tracer.entering("evaluate_without_elimination")
        try:
            property_value, property_name = self.evaluate_by_order(0, var_parts, fixed_parts)
        except ValueError:
            property_value = None
            property_name = None
    
        if self.verbose:
            self.tracer.exiting()
        return property_value, property_name

    def evaluate_eliminating_var_parts(self, var_parts: list, fixed_parts: list):
        if self.verbose:
            self.tracer.entering("evaluate_with_elimination")
        property_value = None
        property_name = None
        for i in range(0, len(var_parts)):
            short_list = list(var_parts)
            short_list.pop(i)
            try:
                property_value, property_name = self.evaluate_by_order(0, short_list, fixed_parts)
                if property_value is not None:
                    break
            except ValueError:
                continue
    
        if self.verbose:
            self.tracer.exiting()
    
        return property_value, property_name

    def evaluate_fixed_parts(self, fixed_parts: list):
        if self.verbose:
            self.tracer.entering("evaluate_fixed_parts")

        key_levels = list(fixed_parts)
        candidate_property = None
        current_level = self.dict_data
        for key_level in key_levels:
            candidate_property = "{candidate}.{level}".format(candidate=candidate_property,
                                                              level=key_level) if candidate_property is not None else key_level
            if self.verbose:
                print("{indent}   Trying {property} ... ".format(indent=self.tracer.get_indent(),
                                                                 property=candidate_property), end="")
            if key_level in current_level:
                current_level = current_level[key_level]
                if self.verbose:
                    print("FOUND")
            else:
                if self.verbose:
                    print("NOT FOUND")

        if self.verbose:
            self.tracer.exiting()

        if isinstance(current_level, dict):
            raise ValueError("Property resolves to a dict: {placeholder}".format(placeholder='.'.join(key_levels)))
        if isinstance(current_level, list):
            raise ValueError("Property resolves to a list: {placeholder}".format(placeholder='.'.join(key_levels)))

        return current_level, candidate_property

    def reorder_list(self, start_idx, list_data):
        start_value = list_data[start_idx]
        for i in range(start_idx, 0, -1):
            list_data[i] = list_data[i - 1]
    
        list_data[0] = start_value

    def evaluate_by_order(self, start_idx: int, var_parts: list, fixed_parts: list):
        if self.verbose:
            self.tracer.entering("evaluate_by_order")
    
        local_var_parts = list(var_parts)
        if start_idx != 0:
            self.reorder_list(start_idx, local_var_parts)
        key_levels = list(local_var_parts)
        key_levels.extend(fixed_parts)
        candidate_property = None
        current_level = self.dict_data
        for key_level in key_levels:
            if key_level is None:
                continue
            candidate_property = "{candidate}.{level}".format(candidate=candidate_property, level=key_level) if candidate_property is not None else key_level
            if self.verbose:
                print("{indent}   Trying {property} ... ".format(indent=self.tracer.get_indent(), property=candidate_property), end="")
            if key_level in current_level:
                current_level = current_level[key_level]
                if self.verbose:
                    print("FOUND")
            else:
                if start_idx + 1 < len(var_parts):
                    if self.verbose:
                        print("NOT FOUND")
                    try:
                        property_value, property_name = self.evaluate_by_order(start_idx + 1, var_parts, fixed_parts)
                        current_level = property_value
                        candidate_property = property_name
                    except ValueError:
                        current_level = None
                        candidate_property = None
                        break
                else:
                    if self.verbose:
                        print("NOT FOUND")
                        self.tracer.exiting()
                    raise ValueError("Property not defined: '{property}'".format(property='.'.join(key_levels)))
    
        if self.verbose:
            self.tracer.exiting()
    
        if isinstance(current_level, dict):
            raise ValueError("Property resolves to a dict: '{placeholder}'".format(placeholder='.'.join(key_levels)))
        if isinstance(current_level, list):
            raise ValueError("Property resolves to a list: '{placeholder}'".format(placeholder='.'.join(key_levels)))
    
        return current_level, candidate_property
    

def print_result(property_tuple):
    property_value = property_tuple[0]
    property_name = property_tuple[1]
    if property_value is not None:
        print('Property found - "{name}": "{value}"'.format(name=property_name, value=property_value))
    else:
        print('Property not found.')


def main(prog_name, args):
    test_data = {"a": {"b": {"c": "something"}},
                 "b": {"c": {"e": "something else", "d": "another thing"}},
                 "c": {"d": "last resort"}, "f": {"g": "lonesome thing"}}

    property_evaluator = PropertyEvaluator(test_data, True)

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
