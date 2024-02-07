import re
import unittest

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
        segment = self.segments.get_segment_by_name(segment_name)
        self.assertTrue(isinstance(segment, tuple))
        expected_segment = ((WLED_NAME_KEY, segment_name),
                            (SEGMENT_START_KEY, 0),
                            (SEGMENT_STOP_KEY, 300),
                            (SEGMENT_OFFSET_KEY, 0),
                            (SEGMENT_GROUPING_KEY, 1),
                            (SEGMENT_SPACING_KEY, 0))
        self.validate_segment(expected_segment, segment)

    def test_get_segment_by_name_2_121(self):
        segment_name = 'Whole Roof + (2)/1/2/1'
        segment = self.segments.get_segment_by_name(segment_name)
        self.assertIsNotNone(segment, "Segment not found.")
        self.assertIsInstance(segment, tuple, "Segment is not a tuple")
        expected_segment = ((WLED_NAME_KEY, segment_name),
                            (SEGMENT_START_KEY, 0),
                            (SEGMENT_STOP_KEY, 300),
                            (SEGMENT_OFFSET_KEY, 0),
                            (SEGMENT_GROUPING_KEY, 2),
                            (SEGMENT_SPACING_KEY, 4))
        self.validate_segment(expected_segment, segment)

    def test_get_segment_by_name_2_1_21(self):
        segment_name = 'Whole Roof + 2/(1)/2/1'
        segment = self.segments.get_segment_by_name(segment_name)
        self.assertIsNotNone(segment, "Segment not found.")
        self.assertIsInstance(segment, tuple, "Segment is not a tuple")
        expected_segment = ((WLED_NAME_KEY, segment_name),
                            (SEGMENT_START_KEY, 2),
                            (SEGMENT_STOP_KEY, 300),
                            (SEGMENT_OFFSET_KEY, 0),
                            (SEGMENT_GROUPING_KEY, 1),
                            (SEGMENT_SPACING_KEY, 5))
        self.validate_segment(expected_segment, segment)

    def test_get_segment_by_name_21_2_1(self):
        segment_name = 'Whole Roof + 2/1/(2)/1'
        segment = self.segments.get_segment_by_name(segment_name)
        self.assertIsNotNone(segment, "Segment not found.")
        self.assertIsInstance(segment, tuple, "Segment is not a tuple")
        expected_segment = ((WLED_NAME_KEY, segment_name),
                            (SEGMENT_START_KEY, 3),
                            (SEGMENT_STOP_KEY, 300),
                            (SEGMENT_OFFSET_KEY, 0),
                            (SEGMENT_GROUPING_KEY, 2),
                            (SEGMENT_SPACING_KEY, 4))
        self.validate_segment(expected_segment, segment)

    def test_get_segment_by_name_212_1_(self):
        segment_name = 'Whole Roof + 2/1/2/(1)'
        segment = self.segments.get_segment_by_name(segment_name)
        self.assertIsNotNone(segment, "Segment not found.")
        self.assertIsInstance(segment, tuple, "Segment is not a tuple")
        expected_segment = ((WLED_NAME_KEY, segment_name),
                            (SEGMENT_START_KEY, 5),
                            (SEGMENT_STOP_KEY, 300),
                            (SEGMENT_OFFSET_KEY, 0),
                            (SEGMENT_GROUPING_KEY, 1),
                            (SEGMENT_SPACING_KEY, 5))
        self.validate_segment(expected_segment, segment)

    def test_get_segment_by_name_start_3_grp_2_spc_4(self):
        segment_name = 'Whole Roof(start=3, grp=2, spc=4)'
        actual_segment = self.segments.get_segment_by_name(segment_name)
        self.assertIsNotNone(actual_segment, "Segment not found.")
        self.assertIsInstance(actual_segment, tuple, "Segment is not a tuple")
        expected_segment = ((WLED_NAME_KEY, segment_name),
                            (SEGMENT_START_KEY, 3),
                            (SEGMENT_STOP_KEY, 300),
                            (SEGMENT_OFFSET_KEY, 0),
                            (SEGMENT_GROUPING_KEY, 2),
                            (SEGMENT_SPACING_KEY, 4))
        self.validate_segment(expected_segment, actual_segment)

    def test_get_segment_by_name_start_3_grp_2_spc_4_spaced(self):
        segment_name = 'Whole Roof( START = 3 , GrP = 2 , sPc = 4 )'
        actual_segment = self.segments.get_segment_by_name(segment_name)
        self.assertIsNotNone(actual_segment, "Segment not found.")
        self.assertIsInstance(actual_segment, tuple, "Segment is not a tuple")
        expected_segment = ((WLED_NAME_KEY, segment_name),
                            (SEGMENT_START_KEY, 3),
                            (SEGMENT_STOP_KEY, 300),
                            (SEGMENT_OFFSET_KEY, 0),
                            (SEGMENT_GROUPING_KEY, 2),
                            (SEGMENT_SPACING_KEY, 4))
        self.validate_segment(expected_segment, actual_segment)

    def validate_segment(self, expected_segment, actual_segment):
        self.assertEqual(len(expected_segment), len(actual_segment), "Segment attr count incorrect.")
        for idx in range(0, len(expected_segment)):
            self.validate_segment_attr(expected_segment[idx], actual_segment[idx])

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


