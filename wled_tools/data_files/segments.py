import re

import yaml

from wled_constants import SEGMENTS_KEY, DEFAULT_SEGMENT_OFFSET, DEFAULT_SEGMENT_GROUPING, DEFAULT_SEGMENT_SPACING, \
    SEGMENT_OFFSET_KEY, SEGMENT_GROUPING_KEY, SEGMENT_SPACING_KEY, WLED_NAME_KEY, SEGMENT_START_KEY, SEGMENT_STOP_KEY
from wled_utils.logger_utils import get_logger
from wled_utils.property_tools import PropertyEvaluator

SEGMENT_NAME_VAR_RE = re.compile(r'[^(0-9]?([(]?\d+[)]?)*')


class Segments:

    def __init__(self, env, segments_file='segments.yaml'):
        self.env = env

        with open(segments_file) as f:
            segment_data = yaml.safe_load(f)

        property_evaluator = PropertyEvaluator(segment_data, verbose=False, strings_only=False)

        self.segments_by_name_as_tuples = {}
        self.segments_by_name_as_dicts = {}
        segments_list = property_evaluator.get_property(self.env, SEGMENTS_KEY)
        for segment in segments_list:
            segment_name_normalized = self.normalize_segment_name(segment[WLED_NAME_KEY])
            self.segments_by_name_as_dicts[segment_name_normalized] = segment.copy()
            self.segments_by_name_as_tuples[segment_name_normalized] = ((WLED_NAME_KEY, segment[WLED_NAME_KEY]),
                                                                        (SEGMENT_START_KEY, segment[SEGMENT_START_KEY]),
                                                                        (SEGMENT_STOP_KEY, segment[SEGMENT_STOP_KEY]),
                                                                        (SEGMENT_OFFSET_KEY,
                                                                        segment[SEGMENT_OFFSET_KEY]
                                                                        if SEGMENT_OFFSET_KEY in segment
                                                                        else DEFAULT_SEGMENT_OFFSET),
                                                                        (SEGMENT_GROUPING_KEY,
                                                                        segment[SEGMENT_GROUPING_KEY]
                                                                        if SEGMENT_GROUPING_KEY in segment
                                                                        else DEFAULT_SEGMENT_GROUPING),
                                                                        (SEGMENT_SPACING_KEY,
                                                                        segment[SEGMENT_SPACING_KEY]
                                                                        if SEGMENT_SPACING_KEY in segment
                                                                        else DEFAULT_SEGMENT_SPACING)
                                                                        )

    def normalize_segment_name(self, segment_name):
        segment_name_normalized = str(segment_name).lower()
        segment_name_normalized = re.sub('[ _]', '', segment_name_normalized)
        return segment_name_normalized

    #  Returns tuple containing segment data: (n, start, stop, of, grp, spc)
    def get_segment_by_name(self, segment_string):
        if '+' in segment_string:
            return self.get_generated_segment_by_name(segment_string)
        else:
            return self.get_simple_segment_by_name(segment_string)

    def get_generated_segment_by_name(self, segment_string):
        segment_parts = segment_string.split('+')
        segment_name = segment_parts[0].strip()
        segment_var = segment_parts[1].strip()
        segment_base = self.get_simple_segment_by_name_as_dict(segment_name)

        start = segment_base[SEGMENT_START_KEY]
        stop = segment_base[SEGMENT_STOP_KEY]
        offset = segment_base[SEGMENT_OFFSET_KEY]
        grouping = segment_base[SEGMENT_GROUPING_KEY]
        spacing = segment_base[SEGMENT_SPACING_KEY]

        sub_segment_lengths, cur_sub_segment, pattern_length = self.get_sub_segment_lengths(segment_var)

        name = segment_string
        start = sum([x for x in sub_segment_lengths[0:cur_sub_segment]])
        grouping = sub_segment_lengths[cur_sub_segment]
        spacing = pattern_length - sub_segment_lengths[cur_sub_segment]

        segment = ((WLED_NAME_KEY, name),
                   (SEGMENT_START_KEY, start),
                   (SEGMENT_STOP_KEY, stop),
                   (SEGMENT_OFFSET_KEY, offset),
                   (SEGMENT_GROUPING_KEY, grouping),
                   (SEGMENT_SPACING_KEY, spacing))

        return segment

    def get_sub_segment_lengths(self, segment_var_str):
        matches = re.findall(SEGMENT_NAME_VAR_RE, segment_var_str)
        if matches is None:
            raise ValueError("Invalid segment variant string: {var_str}".format(var_str=segment_var_str))

        sub_segment_lengths = []
        cur_sub_segment = None
        pattern_length = 0
        for idx in range(0, len(matches)):
            match = matches[idx]
            if match is None or len(match) == 0:
                continue
            if '(' in match:
                if cur_sub_segment is not None:
                    raise ValueError("Multiple current segments indicated: {var_str}".format(var_str=segment_var_str))
                cur_sub_segment = idx

            sub_segment_length = int(match.strip('()'))
            sub_segment_lengths.append(sub_segment_length)
            pattern_length += sub_segment_length

        return sub_segment_lengths, cur_sub_segment, pattern_length

    def get_simple_segment_by_name_as_dict(self, segment_string):
        segment_string_normalized = self.normalize_segment_name(segment_string)
        if segment_string_normalized in self.segments_by_name_as_dicts:
            segment_data = self.segments_by_name_as_dicts[segment_string_normalized]
        else:
            raise ValueError("Input '{name}' is not a recognized segment name".format(name=segment_string))

        return segment_data

    def get_simple_segment_by_name(self, segment_string):
        segment_string_normalized = self.normalize_segment_name(segment_string)
        if segment_string_normalized in self.segments_by_name_as_tuples:
            segment_data = self.segments_by_name_as_tuples[segment_string_normalized]
        else:
            raise ValueError("Input '{name}' is not a recognized segment name".format(name=segment_string))

        return segment_data


if __name__ == '__main__':
    segments = Segments()
    test_segment_string = 'garage'
    properties = segments.get_segment_by_name(test_segment_string)
    get_logger().info(test_segment_string, flush=True)
    get_logger().info(properties, flush=True)

    test_segment_string = 'First Floor'
    properties = segments.get_segment_by_name(test_segment_string)
    get_logger().info(test_segment_string, flush=True)
    get_logger().info(properties, flush=True)

    test_segment_string = 'second_floor'
    properties = segments.get_segment_by_name(test_segment_string)
    get_logger().info(test_segment_string, flush=True)
    get_logger().info(properties, flush=True)

    test_segment_string = 'Third Floor'
    properties = segments.get_segment_by_name(test_segment_string)
    get_logger().info(test_segment_string, flush=True)
    get_logger().info(properties, flush=True)
