import sys


def strip_property_level(key: str):
    idx = key.find(".")

    if idx != -1:
        new_key = key[idx+1:]
    else:
        new_key = None

    return new_key


def get_property(dict_data: dict, *key_parts: str, ):
    replacement_value = None
    key = '.'.join(key_parts)
    not_found = True
    while not_found:
        try:
            replacement_value = drill_down_key(key, dict_data)
            not_found = False
        except ValueError:
            key = strip_property_level(key)
            if key is None:
                raise ValueError("Property/sub-property not found, {key}".format(key=key))

    return replacement_value


def drill_down_key(key: str, dict_data: dict):

    key_levels = key.split('.')
    current_level = dict_data
    for key_level in key_levels:
        if key_level in current_level:
            current_level = current_level[key_level]
        else:
            raise ValueError("Placeholder not defined: {placeholder}".format(placeholder=key))

    if isinstance(current_level, dict):
        raise ValueError("Placeholder resolves to a dict: {placeholder}".format(placeholder=key))
    if isinstance(current_level, list):
        raise ValueError("Placeholder resolves to a list: {placeholder}".format(placeholder=key))

    return current_level


def main(prog_name, args):
    test_data = {"a": {"b": {"c": "something"}}, "b": {"c": "something else"}, "d": "another thing"}

    print("value: " + str(get_property(test_data, "a.b.c")))
    print("value: " + str(get_property(test_data, "a.b.c.d")))
    print("value: " + str(get_property(test_data, "b.c")))
    print("value: " + str(get_property(test_data, "a", "b", "c.d")))


if __name__ == '__main__':
    main(sys.argv[0], sys.argv[1:])