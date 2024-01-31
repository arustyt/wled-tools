import re


def normalize_keys(dictionary: dict):
    new_dictionary = dict()
    for key in dictionary:
        new_key = normalize_name(key)
        if new_key != key:
            new_dictionary[new_key] = dictionary[key]

    dictionary.update(new_dictionary)


def normalize_name(name: str):
    return re.sub(r"[^a-zA-Z0-9_]", '', name.lower().replace(" ", "_"))


def get_dict_path(*args):
    return '.'.join(args)

