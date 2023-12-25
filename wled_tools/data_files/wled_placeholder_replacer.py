import re

from data_files.wled_data_processor import WledDataProcessor
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

    def process_dict_element(self, path: str, name, data):
        return (name, self.replace_placeholders(data)),

    def process_list_element(self, path: str, name, data):
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

        text_to_replace = PLACEHOLDER_PREFIX + placeholder + PLACEHOLDER_SUFFIX
        if data != text_to_replace:
            new_data = data.replace(text_to_replace, str(replacement_value))
        else:
            new_data = replacement_value

        return new_data


if __name__ == '__main__':
    env_data = {'it_worked': 'IT WORKED ',
                'dict': {
                    'dict': 'IN A DICT (${dict.nested})',
                    'nested': 'nested'
                },
                'list': {
                    'list': 'IN A LIST (${list.again})',
                    'again': 'again'}
                }

    wled_data = {'1': {'n': 'Hey look, ${it_worked}${dict.dict}!!!', 'h': 'Some other dict value.',
                       'l': ['1', 'Hey look, ${it_worked}${list.list}!!!', '3']}}

    wled_presets = WledPlaceholderReplacer(env_data)

    new_wled_data = wled_presets.process_wled_data(wled_data)

    get_logger().info(new_wled_data)
