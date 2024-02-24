import unittest

from data_files.segment_id_manager import SegmentIdManager

NO_ID = -1


class SegmentIdManagerTests(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_get_next_segment_id_3_ordered_2_missing(self):
        ids = [0, 1, 2, NO_ID, NO_ID]
        segments, segment_id_mgr = self.get_test_segment_id_manager(ids)

        expected_ids = [0, 1, 2, 3, 4]
        self.validate_segment_ids(expected_ids, ids, segments, segment_id_mgr)

    def test_get_next_segment_id_3_unordered_2_missing(self):
        ids = [2, 0, 1, NO_ID, NO_ID]
        segments, segment_id_mgr = self.get_test_segment_id_manager(ids)

        expected_ids = [2, 0, 1, 3, 4]
        self.validate_segment_ids(expected_ids, ids, segments, segment_id_mgr)

    def test_get_next_segment_id_2_missing_3_unordered(self):
        ids = [NO_ID, NO_ID, 2, 0, 1]
        segments, segment_id_mgr = self.get_test_segment_id_manager(ids)

        expected_ids = [3, 4, 2, 0, 1]
        self.validate_segment_ids(expected_ids, ids, segments, segment_id_mgr)

    def test_get_next_segment_id_2_missing_3_nonsequential(self):
        ids = [NO_ID, NO_ID, 1, 3, 4]
        segments, segment_id_mgr = self.get_test_segment_id_manager(ids)

        expected_ids = [0, 2, 1, 3, 4]
        self.validate_segment_ids(expected_ids, ids, segments, segment_id_mgr)

    def test_get_next_segment_id_3_missing_2_nonsequential(self):
        ids = [NO_ID, NO_ID, 1, 3, NO_ID]
        segments, segment_id_mgr = self.get_test_segment_id_manager(ids)

        expected_ids = [0, 2, 1, 3, 4]
        self.validate_segment_ids(expected_ids, ids, segments, segment_id_mgr)

    def test_get_next_segment_id_all_missing(self):
        ids = [NO_ID, NO_ID, NO_ID, NO_ID, NO_ID]
        segments, segment_id_mgr = self.get_test_segment_id_manager(ids)

        expected_ids = [0, 1, 2, 3, 4]
        self.validate_segment_ids(expected_ids, ids, segments, segment_id_mgr)

    def test_get_next_segment_id_all_hard_coded(self):
        ids = [0, 1, 2, 3, 4]
        segments, segment_id_mgr = self.get_test_segment_id_manager(ids)

        expected_ids = [0, 1, 2, 3, 4]
        self.validate_segment_ids(expected_ids, ids, segments, segment_id_mgr)

    def test_get_next_segment_id_all_hard_coded_nonzero_start(self):
        ids = [1, 2, 3, 4]
        segments, segment_id_mgr = self.get_test_segment_id_manager(ids)

        expected_ids = [1, 2, 3, 4]
        self.validate_segment_ids(expected_ids, ids, segments, segment_id_mgr)

    def get_test_segment_id_manager(self, ids):
        segments = self.get_test_segments(ids)
        segment_id_mgr = SegmentIdManager(segments)
        return segments, segment_id_mgr

    def get_test_segments(self, ids: list):
        segments = []
        for segment_id in ids:
            segment = {}
            if segment_id != NO_ID:
                segment['n'] = "Segment {id}".format(id=segment_id)
                segment['id'] = segment_id
            else:
                segment['n'] = "Segment no-id"
            segments.append(segment)

        return segments

    def validate_segment_ids(self, expected_ids: list, ids: list, segments, segment_id_mgr):
        self.assertEqual(len(expected_ids), len(ids), "Id lists different lengths")
        self.assertEqual(len(expected_ids), len(segments), "Segment list length incorrect.")
        for i in range(0, len(expected_ids)):
            segment_id = ids[i]
            expected_id = expected_ids[i]
            if segment_id < 0:
                self.assertEqual(expected_id, segment_id_mgr.get_next_segment_id(), "Generated segment id incorrect.")
            else:
                self.assertEqual(expected_id, segments[i]['id'], "Hard-coded segment id incorrect.")




