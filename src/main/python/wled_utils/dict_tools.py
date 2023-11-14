def strip_property_level(key: str):
    idx = key.find(".")

    if idx != -1:
        new_key = key[idx]
    else:
        new_key = None

    return new_key


def get_env_property(env: str, key: str, dict_data: dict):
    return get_property("{env}.{key}".format(env=env, key=key), dict_data)

    
def get_property(key: str, dict_data: dict):
    replacement_value = None
    new_key = key
    while not_found:
        try:
            replacement_value = drill_down_key(new_key, dict_data)
            not_found = False
        except ValueError:
            new_key = strip_property_level(key)
            if new_key is None:
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
