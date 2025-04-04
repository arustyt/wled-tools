import re
from pprint import pprint

from data_files.wled_data_processor import WledDataProcessor
from wled_constants import DEFAULTS_TAG
from wled_utils.logger_utils import get_logger
from wled_utils.property_tools import PropertyEvaluator

PLACEHOLDER_PREFIX = '${'
PLACEHOLDER_PREFIX_RE = '[$][{]'
PLACEHOLDER_SUFFIX = '}'
PLACEHOLDER_SUFFIX_RE = '[}]'
PLACEHOLDER_CHARS_RE = '[^}]'


class WledPlaceholderReplacer(WledDataProcessor):

    def __init__(self, placeholder_data: dict, environment=None):
        super().__init__(environment)
        self.placeholder_data = placeholder_data
        placeholder_re_str = '^.*{prefix}({chars}*){suffix}.*$'.format(prefix=PLACEHOLDER_PREFIX_RE,
                                                                       chars=PLACEHOLDER_CHARS_RE,
                                                                       suffix=PLACEHOLDER_SUFFIX_RE)
        self.placeholder_re = re.compile(placeholder_re_str)
        self.property_evaluator = PropertyEvaluator(placeholder_data)

    def handle_defaults(self, defaults_dict):
        return self.handle_dict(DEFAULTS_TAG, DEFAULTS_TAG, defaults_dict)

    def handle_dict_element(self, path: str, name, data):
        return (name, self.replace_placeholders(data)),

    def handle_list_element(self, path: str, name, data):
        return [self.replace_placeholders(data)]

    def replace_placeholders(self, data):

        new_data = data

        while True:
            if not isinstance(new_data, str):
                break

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

        replacement_value = self.property_evaluator.get_property(self.environment, placeholder)

        if replacement_value is None:
            raise LookupError('Property not found: {prop}'.format(prop=placeholder))

        text_to_replace = PLACEHOLDER_PREFIX + placeholder + PLACEHOLDER_SUFFIX
        if data != text_to_replace:
            new_data = data.replace(text_to_replace, str(replacement_value))
        else:
            new_data = replacement_value

        return new_data

    def add_properties(self, properties):
        self.property_evaluator.add_properties(properties)

    def add_property(self, name: str, value):
        self.property_evaluator.add_property(name, value)


if __name__ == '__main__':
    env_data = {'it_worked': 'IT WORKED ',
                'dict':
                    {
                        'dict': 'IN A DICT (${dict.nested})',
                        'nested': 'nested'
                    },
                'list':
                    {
                        'list': 'IN A LIST (${list.again})',
                        'again': 'again'
                    },
                'easter':
                    {
                        'bg': 'Black',
                        'fg': 'White'
                    },
                'lent_bg': 'Scarlet',
                'lent_fg': 'Purple',
                }

    wled_data = {
        '1':
            {
                'n': 'Hey look, ${it_worked}${dict.dict}!!!',
                'h': 'Some other dict value.',
                'l': ['1', 'Hey look, ${it_worked}${list.list}!!!', '3']
            },
        '2':
            {
                'bg': '${${holiday}.bg}',
                'fg': '${${holiday}.fg}'
            },
        '3':
            {
                'bg': '${${holiday2}_bg}',
                'fg': '${${holiday2}_fg}'
            }

    }

    placeholder_replacer = WledPlaceholderReplacer(env_data)

    placeholder_replacer.add_property('holiday', 'easter')
    placeholder_replacer.add_property('holiday2', 'lent')

    new_wled_data = placeholder_replacer.process_wled_data(wled_data)

    pprint(new_wled_data)
