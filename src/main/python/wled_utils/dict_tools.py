

def drill_down_env_key(env: str, key: str, dict_data: dict):
    if env is not None and env in dict_data:
        try:  # Try with environment as prefix
            replacement_value = drill_down_key("{env}.{placeholder}".format(env=env, placeholder=key), dict_data)
        except ValueError:  # Else ignore environment
            replacement_value = drill_down_key(key, dict_data)
    else:
        replacement_value = drill_down_key(key, dict_data)

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
