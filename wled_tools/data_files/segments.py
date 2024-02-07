import re

import yaml

from data_files.segment import Segment
from wled_constants import SEGMENTS_KEY, DEFAULT_SEGMENT_OFFSET, DEFAULT_SEGMENT_GROUPING, DEFAULT_SEGMENT_SPACING, \
    SEGMENT_OFFSET_KEY, SEGMENT_GROUPING_KEY, SEGMENT_SPACING_KEY, WLED_NAME_KEY, SEGMENT_START_KEY, SEGMENT_STOP_KEY, \
    SEGMENT_PATTERN_KEY
from wled_utils.logger_utils import get_logger
from wled_utils.property_tools import PropertyEvaluator

SEGMENT_PATTERN_RE = re.compile(r'[^(0-9]?([(]?\d+[)]?)*')
#  SEGMENT_PARAMETER_RE = re.compile(r'([^(]+)[(]([^)]+)[)]')
SEGMENT_PARAMETER_RE = re.compile(r'([^(]+)[(](.+)[)]$')


class Segments:

    def __init__(self, env, segments_file='segments.yaml'):
        self.env = env

        with open(segments_file) as f:
            segment_data = yaml.safe_load(f)

        property_evaluator = PropertyEvaluator(segment_data, verbose=False, strings_only=False)

#        self.segments_by_name_as_tuples = {}
#        self.segments_by_name_as_dicts = {}
        self.segments_by_name = {}
        segments_list = property_evaluator.get_property(self.env, SEGMENTS_KEY)
        for segment in segments_list:
            segment_name_normalized = self.normalize_segment_name(segment[WLED_NAME_KEY])
            self.segments_by_name[segment_name_normalized] = segment.copy()

    def normalize_segment_name(self, segment_name):
        segment_name_normalized = str(segment_name).lower()
        segment_name_normalized = re.sub('[ _]', '', segment_name_normalized)
        return segment_name_normalized

    #  Returns Segment instance containing segment data
    def get_segment_by_name(self, segment_string: str) -> Segment:
        if '(' in segment_string:
            return self.get_variant_segment_by_name(segment_string)
        else:
            return self.get_simple_segment_by_name(segment_string)

    def get_variant_segment_by_name(self, segment_string: str) -> Segment:
        matches = re.match(SEGMENT_PARAMETER_RE, segment_string)
        if matches is None:
            raise ValueError("Invalid segment variant string: {var_str}".format(var_str=segment_string))
        segment_name = matches[1]
        segment_parm_str = matches[2]
        segment_base = self.get_simple_segment_by_name_as_dict(segment_name)
        segment_base.name = segment_string
        if segment_parm_str.lower().startswith(SEGMENT_PATTERN_KEY):
            return self.get_pattern_segment(segment_base, segment_parm_str)
        else:
            return self.get_parameterized_segment(segment_base, segment_parm_str)

    def get_parameterized_segment(self, segment: Segment, segment_parm_str: str) -> Segment:
        parms = segment_parm_str.strip().split(',')

        for parm in parms:
            parm_parts = parm.split('=')
            parm_name = parm_parts[0].strip().lower()
            parm_value = int(parm_parts[1].strip())
            if parm_name == SEGMENT_OFFSET_KEY:
                segment.offset = int(parm_value)
            elif parm_name == SEGMENT_START_KEY:
                segment.start = int(parm_value)
            elif parm_name == SEGMENT_STOP_KEY:
                segment.stop = int(parm_value)
            elif parm_name == SEGMENT_SPACING_KEY:
                segment.spacing = int(parm_value)
            elif parm_name == SEGMENT_GROUPING_KEY:
                segment.grouping = int(parm_value)
            else:
                raise ValueError("Invalid segment attribute: {attr}".format(attr=parm_name))

        return segment

    def get_pattern_segment(self, segment: Segment, segment_parm_str: str) -> Segment:

        parm_parts = segment_parm_str.split('=')
        parm_name = parm_parts[0].strip().lower()
        parm_value = parm_parts[1].strip()

        if parm_name != SEGMENT_PATTERN_KEY:
            raise ValueError("Invalid segment attribute: {attr}".format(attr=parm_name))

        sub_segment_lengths, cur_sub_segment, pattern_length = self.get_sub_segment_lengths(parm_value)

        segment.start = sum([x for x in sub_segment_lengths[0:cur_sub_segment]])
        segment.grouping = sub_segment_lengths[cur_sub_segment]
        segment.spacing = pattern_length - sub_segment_lengths[cur_sub_segment]

        return segment

    def get_sub_segment_lengths(self, segment_var_str):
        matches = re.findall(SEGMENT_PATTERN_RE, segment_var_str)
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
        if segment_string_normalized in self.segments_by_name:
            segment = Segment(self.segments_by_name[segment_string_normalized].copy())
        else:
            raise LookupError("Input '{name}' is not a recognized segment name".format(name=segment_string))

        return segment

    def get_simple_segment_by_name(self, segment_string):
        segment_string_normalized = self.normalize_segment_name(segment_string)
        if segment_string_normalized in self.segments_by_name:
            segment = Segment(self.segments_by_name[segment_string_normalized])
        else:
            raise LookupError("Input '{name}' is not a recognized segment name".format(name=segment_string))

        return segment


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
