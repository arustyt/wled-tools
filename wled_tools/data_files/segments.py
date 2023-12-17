import re

import yaml

from wled_utils.logger_utils import get_logger


class Segments:

    def __init__(self, segment_names_file='segments.yaml'):
        with open(segment_names_file) as f:
            segment_data = yaml.safe_load(f)

        self.segments_by_name = {}
        for segment in segment_data['segments']:
            segment_name_normalized = self.normalize_segment_name(segment['n'])
            self.segments_by_name[segment_name_normalized] = (('n', segment['n']), ('start', segment['start']),
                                                              ('stop', segment['stop']))

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

