from wled_constants import WLED_NAME_KEY, SEGMENT_START_KEY, SEGMENT_OFFSET_KEY, DEFAULT_SEGMENT_OFFSET, \
    SEGMENT_GROUPING_KEY, DEFAULT_SEGMENT_GROUPING, SEGMENT_SPACING_KEY, DEFAULT_SEGMENT_SPACING, SEGMENT_STOP_KEY


class Segment:
    def __init__(self, segment):
        self.name = segment[WLED_NAME_KEY]
        self.name_key = WLED_NAME_KEY
        self.start = int(segment[SEGMENT_START_KEY])
        self.start_key = SEGMENT_START_KEY
        self.stop = int(segment[SEGMENT_STOP_KEY])
        self.stop_key = SEGMENT_STOP_KEY
        self.offset = int(segment[SEGMENT_OFFSET_KEY]) if SEGMENT_OFFSET_KEY in segment else DEFAULT_SEGMENT_OFFSET
        self.offset_key = SEGMENT_OFFSET_KEY
        self.grouping = int(
            segment[SEGMENT_GROUPING_KEY]) if SEGMENT_GROUPING_KEY in segment else DEFAULT_SEGMENT_GROUPING
        self.grouping_key = SEGMENT_GROUPING_KEY
        self.spacing = int(segment[SEGMENT_SPACING_KEY]) if SEGMENT_SPACING_KEY in segment else DEFAULT_SEGMENT_SPACING
        self.spacing_key = SEGMENT_SPACING_KEY




