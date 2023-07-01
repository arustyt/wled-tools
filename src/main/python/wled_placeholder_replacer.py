import re

from wled_data_processor import WledDataProcessor

PLACEHOLDER_PREFIX = '${'
PLACEHOLDER_PREFIX_RE = '[$][{]'
PLACEHOLDER_SUFFIX = '}'
PLACEHOLDER_SUFFIX_RE = '[}]'
PLACEHOLDER_CHARS_RE = '[^}]'


class WledPlaceholderReplacer(WledDataProcessor):

    def __init__(self, placeholder_data: dict):
        super().__init__()
        self.placeholder_data = placeholder_data
        placeholder_re_str = '^.*{prefix}({chars}*){suffix}.*$'.format(prefix=PLACEHOLDER_PREFIX_RE,
                                                                       chars=PLACEHOLDER_CHARS_RE,
                                                                       suffix=PLACEHOLDER_SUFFIX_RE)
        self.placeholder_re = re.compile(placeholder_re_str)

    def process_dict_element(self, path: str, name, data):
        return (name, self.replace_placeholders(data)),

    def process_list_element(self, path: str, name, data):
        return [self.replace_placeholders(data)]

    def replace_placeholders(self, data):
        new_data = data
        while True:
            matches = re.match(self.placeholder_re, new_data)
            if matches is not None:
                new_data = self.replace_placeholder(new_data, matches.groups())
            else:
                break

        return new_data

    def replace_placeholder(self, data: str, placeholders):
        placeholder = placeholders[0]

        if placeholder is None or len(placeholder) == 0:
            raise ValueError("Empty placeholder encountered.")

        if placeholder in self.placeholder_data:
            text_to_replace = PLACEHOLDER_PREFIX + placeholder + PLACEHOLDER_SUFFIX
            new_data = data.replace(text_to_replace, self.placeholder_data[placeholder])
        else:
            raise ValueError("Placeholder not defined: {placeholder}".format(placeholder=placeholder))

        return new_data


if __name__ == '__main__':
    env_data = {'it_worked': 'IT WORKED ',
                'dict': 'IN A DICT (${nested})',
                'list': 'IN A LIST (${again})',
                'again': 'again',
                'nested': 'nested'
                }

    wled_data = {'1': {'n': 'Hey look, ${it_worked}${dict}!!!', 'h': 'Some other dict value.',
                       'l': ['1', 'Hey look, ${it_worked}${list}!!!', '3']}}

    wled_presets = WledPlaceholderReplacer(env_data)

    new_wled_data = wled_presets.process_wled_data(wled_data)

    print(new_wled_data)