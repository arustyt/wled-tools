from wled_constants import DEFAULT_EFFECTS_FILE_BASE, DEFAULT_PALETTES_FILE_BASE, DEFAULT_COLORS_FILE_BASE, \
    DEFAULT_SEGMENTS_FILE_BASE, DEFAULT_PROPERTIES_FILE_BASE, DEFAULT_EFFECTS_FILE_NAME, DEFAULT_PALETTES_FILE_NAME, \
    DEFAULT_COLORS_FILE_NAME
from wled_utils.path_utils import find_path


class WledConfiguration:

    def __init__(self, data_dir, wled_rel_dir, definitions_rel_dir, environment, properties, segments,
                 effects=DEFAULT_EFFECTS_FILE_NAME, palettes=DEFAULT_PALETTES_FILE_NAME,
                 colors=DEFAULT_COLORS_FILE_NAME):
        self.data_dir = data_dir
        self.wled_rel_dir = wled_rel_dir
        self.definitions_rel_dir = definitions_rel_dir
        self.wled_dir = "{base}/{rel_dir}".format(base=data_dir, rel_dir=wled_rel_dir)
        self.definitions_dir = "{base}/{rel_dir}".format(base=data_dir, rel_dir=definitions_rel_dir)
        self.environment = environment
        self.properties_file = properties
        self.properties_path = find_path(self.wled_dir, environment, properties, DEFAULT_PROPERTIES_FILE_BASE)
        self.segments_file = segments
        self.segments_path = find_path(self.wled_dir, environment, segments, DEFAULT_SEGMENTS_FILE_BASE)
        self.effects_file = effects
        self.effects_path = find_path(self.definitions_dir, environment, effects, DEFAULT_EFFECTS_FILE_BASE)
        self.palettes_file = palettes
        self.palettes_path = find_path(self.definitions_dir, environment, palettes, DEFAULT_PALETTES_FILE_BASE)
        self.colors_file = colors
        self.colors_path = find_path(self.definitions_dir, environment, colors, DEFAULT_COLORS_FILE_BASE)
