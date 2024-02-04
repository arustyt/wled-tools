import re

import yaml

from wled_constants import SEGMENTS_KEY, DEFAULT_SEGMENT_OFFSET, DEFAULT_SEGMENT_GROUPING, DEFAULT_SEGMENT_SPACING, \
    SEGMENT_OFFSET_KEY, SEGMENT_GROUPING_KEY, SEGMENT_SPACING_KEY, WLED_NAME_KEY, SEGMENT_START_KEY, SEGMENT_STOP_KEY
from wled_utils.logger_utils import get_logger
from wled_utils.property_tools import PropertyEvaluator


class Segments:

    def __init__(self, env, segment_names_file='segments.yaml'):
        self.env = env

        with open(segment_names_file) as f:
            segment_data = yaml.safe_load(f)

        property_evaluator = PropertyEvaluator(segment_data, verbose=False, strings_only=False)

        self.segments_by_name = {}
        segments_list = property_evaluator.get_property(self.env, SEGMENTS_KEY)
        for segment in segments_list:
            segment_name_normalized = self.normalize_segment_name(segment[WLED_NAME_KEY])
            self.segments_by_name[segment_name_normalized] = ((WLED_NAME_KEY, segment[WLED_NAME_KEY]),
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

    #  Returns tuple containing segment data: (n, start, stop)
    def get_segment_by_name(self, segment_string):
        segment_data = None
        segment_string_normalized = self.normalize_segment_name(segment_string)
        if segment_string_normalized in self.segments_by_name:
            segment_data = self.segments_by_name[segment_string_normalized]
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
