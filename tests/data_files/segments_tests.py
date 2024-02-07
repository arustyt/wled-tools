import re
import unittest

from data_files.segment import Segment
from data_files.segments import Segments
from wled_constants import (WLED_NAME_KEY, SEGMENT_START_KEY, SEGMENT_STOP_KEY, SEGMENT_OFFSET_KEY,
                            SEGMENT_GROUPING_KEY, SEGMENT_SPACING_KEY)

ATTR_NAMES = (WLED_NAME_KEY, SEGMENT_START_KEY, SEGMENT_STOP_KEY, SEGMENT_OFFSET_KEY, SEGMENT_GROUPING_KEY,
              SEGMENT_SPACING_KEY)


class SegmentsTests(unittest.TestCase):
    def setUp(self):
        self.segments = Segments('segments.yaml')

    def tearDown(self):
        pass

    # get_file_name_candidates tests ================================================================================

    def test_get_segment_by_name_simple(self):
        segment_name = 'Whole Roof'
        actual_segment = self.segments.get_segment_by_name(segment_name)
        self.assertIsNotNone(actual_segment, "Segment not found.")
        self.assertIsInstance(actual_segment, Segment, "Result is not a Segment")
        self.validate_segment(actual_segment, segment_name, 0, 300, 0, 1, 0)

    def test_get_segment_by_name_2_121(self):
        segment_name = 'Whole Roof(pat=(2)/1/2/1)'
        actual_segment = self.segments.get_segment_by_name(segment_name)
        self.assertIsNotNone(actual_segment, "Segment not found.")
        self.assertIsInstance(actual_segment, Segment, "Result is not a Segment")
        self.validate_segment(actual_segment, segment_name, 0, 300, 0, 2, 4)

    def test_get_segment_by_name_2_1_21(self):
        segment_name = 'Whole Roof(pat=2/(1)/2/1)'
        actual_segment = self.segments.get_segment_by_name(segment_name)
        self.assertIsNotNone(actual_segment, "Segment not found.")
        self.assertIsInstance(actual_segment, Segment, "Result is not a Segment")
        expected_segment = ((WLED_NAME_KEY, segment_name),
                            (SEGMENT_START_KEY, 2),
                            (SEGMENT_STOP_KEY, 300),
                            (SEGMENT_OFFSET_KEY, 0),
                            (SEGMENT_GROUPING_KEY, 1),
                            (SEGMENT_SPACING_KEY, 5))
        self.validate_segment(actual_segment, segment_name, 2, 300, 0, 1, 5)

    def test_get_segment_by_name_21_2_1(self):
        segment_name = 'Whole Roof(pat=2/1/(2)/1)'
        actual_segment = self.segments.get_segment_by_name(segment_name)
        self.assertIsNotNone(actual_segment, "Segment not found.")
        self.assertIsInstance(actual_segment, Segment, "Result is not a Segment")
        self.validate_segment(actual_segment, segment_name, 3, 300, 0, 2, 4)

    def test_get_segment_by_name_212_1_(self):
        segment_name = 'Whole Roof(pat=2/1/2/(1))'
        actual_segment = self.segments.get_segment_by_name(segment_name)
        self.assertIsNotNone(actual_segment, "Segment not found.")
        self.assertIsInstance(actual_segment, Segment, "Result is not a Segment")
        self.validate_segment(actual_segment, segment_name, 5, 300, 0, 1, 5)

    def test_get_segment_by_name_start_3_grp_2_spc_4(self):
        segment_name = 'Whole Roof(start=3, grp=2, spc=4)'
        actual_segment = self.segments.get_segment_by_name(segment_name)
        self.assertIsNotNone(actual_segment, "Segment not found.")
        self.assertIsInstance(actual_segment, Segment, "Result is not a Segment")
        self.validate_segment(actual_segment, segment_name, 3, 300, 0, 2, 4)

    def test_get_segment_by_name_start_3_grp_2_spc_4_spaced(self):
        segment_name = 'Whole Roof( START = 3 , GrP = 2 , sPc = 4 )'
        actual_segment = self.segments.get_segment_by_name(segment_name)
        self.assertIsNotNone(actual_segment, "Segment not found.")
        self.assertIsInstance(actual_segment, Segment, "Result is not a Segment")
        self.validate_segment(actual_segment, segment_name, 3, 300, 0, 2, 4)

    def validate_segment(self, segment: Segment, name, start, stop, offset, grouping, spacing):
        self.assertEqual(name, segment.name, "Segment name is incorrect.")
        self.assertEqual(start, segment.start, "Segment start is incorrect.")
        self.assertEqual(stop, segment.stop, "Segment stop is incorrect.")
        self.assertEqual(offset, segment.offset, "Segment offset is incorrect.")
        self.assertEqual(grouping, segment.grouping, "Segment grouping is incorrect.")
        self.assertEqual(spacing, segment.spacing, "Segment spacing is incorrect.")

    def validate_segment_attr(self, expected_attr, actual_attr):
        self.assertEqual(expected_attr[0], actual_attr[0], "Name in N/V pair is incorrect.")
        self.assertEqual(expected_attr[1], actual_attr[1], "Value in N/V pair is incorrect.")

    def test_parse_segment_var_string(self):
        expected_counts = [4, 3, 2, 1]
        expected_current = 2
        expected_pattern_length = 10
        actual_sub_segment_lengths, actual_cur_sub_segment, actual_pattern_length = \
            self.segments.get_sub_segment_lengths('4;3,(2)/1')

        self.assertEqual(expected_counts, actual_sub_segment_lengths, "Counts are incorrect.")
        self.assertEqual(expected_current, actual_cur_sub_segment, "Current index is incorrect.")
        self.assertEqual(expected_pattern_length, actual_pattern_length, "Pattern length is incorrect.")


