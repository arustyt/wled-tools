from wled_constants import DEFAULTS_TAG, PRESETS_TAG, ID_TAG


class SegmentIdManager:

    def __init__(self, seg_data: list):
        self.segment_ids = set()
        self.next_segment_id = 0
        for segment in seg_data:
            if ID_TAG in segment:
                segment_id = int(segment[ID_TAG])
                self.add_segment_id(segment_id)

    def add_segment_id(self, segment_id):
        if segment_id in self.segment_ids:
            raise ValueError("Duplicate segment ID: {pid}".format(pid=segment_id))

        self.segment_ids.add(segment_id)

    def get_next_segment_id(self):
        while True:
            segment_id = self.next_segment_id
            self.next_segment_id += 1
            if segment_id not in self.segment_ids:
                self.segment_ids.add(segment_id)
                break

        return segment_id
