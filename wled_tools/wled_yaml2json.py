import argparse
import os
import sys

from data_files.cfg_file_processor import CfgFileProcessor
from data_files.presets_file_processor import PresetsFileProcessor
from data_files.wled_placeholder_replacer import WledPlaceholderReplacer
from wled_configuration import WledConfiguration
from wled_constants import DEFAULT_WLED_DIR, DEFAULT_ENVIRONMENT, DEFAULT_SEGMENTS_FILE_BASE, \
    DEFAULT_PROPERTIES_FILE_NAME, \
    DEFAULT_OUTPUT_DIR, DEFAULT_DEFINITIONS_DIR, DEFAULT_EFFECTS_FILE_NAME, DEFAULT_PALETTES_FILE_NAME, \
    DEFAULT_COLORS_FILE_NAME, \
    DEFAULT_PROPERTIES_FILE_BASE, DEFAULT_PRESETS_FILE_BASE, DEFAULT_CFG_FILE_BASE, DEFAULT_DATA_DIR, \
    DEFAULT_EFFECTS_FILE_BASE, DEFAULT_PALETTES_FILE_BASE, DEFAULT_COLORS_FILE_BASE
from wled_utils.logger_utils import get_logger, init_logger
from wled_utils.path_utils import find_path, find_path_list

from wled_utils.yaml_multi_file_loader import load_yaml_file

FILE_NAME_OPTIONS = ("   env     file     file\n"
                     "  option   option   option ends\n"
                     "  present  present  with .yaml\n"
                     "  =======  =======  ===========\n"
                     "     Y        Y         N        <file option value>-<env option value>.yaml\n"
                     "     N        Y         N        <file option value>.yaml\n"
                     "     *        Y         Y        <file option value>\n"
                     "     Y        N         N        <default file base>-<env option value>.yaml\n"
                     "     N        N         N        <default file base>.yaml\n")


def main(name, args):
    parser = argparse.ArgumentParser(
        description="Convert YAML files to WLED JSON.  The names of files located in --wled_dir \n"
                    "(--properties, --segments, --presets, and --cfg) follow these rules to\n"
                    "determine the file name.\n" +
                    FILE_NAME_OPTIONS,
        # formatter_class=argparse.RawTextHelpFormatter
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--data_dir", type=str,
                        help="Directory from which wled_dir and definitions_dir are relative.  If not specified, "
                             "'" + DEFAULT_DATA_DIR + "' is used.",
                        action="store", default=DEFAULT_WLED_DIR)
    parser.add_argument("--wled_dir", type=str,
                        help="WLED data file location. Applies to presets, cfg, and segments files. If not specified, "
                             "'" + DEFAULT_WLED_DIR + "' is used.",
                        action="store", default=DEFAULT_WLED_DIR)
    parser.add_argument("--env", type=str, help="The name of the environment for this execution. The "
                                                "environment name is used to construct file names for properties, "
                                                "presets, segments, and cfg files per the rules above in the "
                                                "description.",
                        action="store", default=DEFAULT_ENVIRONMENT)
    parser.add_argument("--properties", type=str, help="A file (YAML) defining properties for placeholder replacement "
                                                       "within config and preset files.  The file name is relative to "
                                                       "the --wled_dir directory. The properties file name will be "
                                                       "determined as described above where the default file base is "
                                                       "'properties'.",
                        action="store", default=DEFAULT_PROPERTIES_FILE_NAME)
    parser.add_argument("--define", "-D", type=str, help="Defines property to be added to the properties "
                                                         "loaded via --properties. Format is <prop_name>=<prop_value>. "
                                                         "Multiple properties can be defined by including multiple "
                                                         "occurrences of the -D option.",
                        action="append")
    parser.add_argument("--presets", type=str, help="A comma-separated list of WLED preset file names (YAML). The "
                                                    "file names are relative to the --wled_dir directory. Note that "
                                                    "preset IDs must be unique across all preset files. The "
                                                    "presets file name will be determined as described above where "
                                                    "the default file base is 'presets'.",
                        action="store", default=None)
    parser.add_argument("--segments", type=str, help="Segments definition file name (YAML) relative to the --wled_dir "
                                                     "directory. The segments file name will be determined as "
                                                     "described above where the default file base is 'segments'.",
                        action="store", default=DEFAULT_SEGMENTS_FILE_BASE)
    parser.add_argument("--cfg", type=str, help="WLED cfg file name (YAML) relative to the --wled_dir directory. The "
                                                "cfg file name will be determined as described above where the "
                                                "default file base is 'cfg'.",
                        action="store", default=None)
    parser.add_argument("--output_dir", type=str,
                        help="Directory where generated files output. If not "
                             "specified, '" + DEFAULT_OUTPUT_DIR + "' is used.",
                        action="store", default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--definitions_dir", type=str,
                        help="Definition file location. Applies to effects, palettes, and colors files. If not "
                             "specified, '" + DEFAULT_DEFINITIONS_DIR + "' is used.",
                        action="store", default=DEFAULT_DEFINITIONS_DIR)
    parser.add_argument("--effects", type=str, help="WLED effect definition file name (YAML) relative to the "
                                                    "--definitions_dir directory. If not specified, '" +
                                                    DEFAULT_EFFECTS_FILE_NAME + "' is used.",
                        action="store", default=DEFAULT_EFFECTS_FILE_NAME)
    parser.add_argument("--palettes", type=str, help="WLED palette definitions file-name (YAML) relative to the "
                                                     "--definitions_dir directory. If not specified, '" +
                                                     DEFAULT_PALETTES_FILE_NAME + "' is used.",
                        action="store", default=DEFAULT_PALETTES_FILE_NAME)
    parser.add_argument("--colors", type=str, help="HTML color-name definitions file-name (YAML) relative to the "
                                                   "--definitions_dir directory. If not specified, '" +
                                                   DEFAULT_COLORS_FILE_NAME + "' is used.",
                        action="store", default=DEFAULT_COLORS_FILE_NAME)
    parser.add_argument("--suffix", type=str, help=("Suffix to be appended to the output file names, preceded by a "
                                                    "'-',  before the '.json' extension."),
                        action="store", default=None)
    parser.add_argument("--include", type=str, help=("A comma-separated list of preset/playlist IDs/names to INCLUDE "
                                                     "in the output presets file. When this option is provided the "
                                                     "script will start with an empty set of presets and include only "
                                                     "those in the list. If a playlist is provided in the list "
                                                     " the playlist itself will be included. If the --deep option is "
                                                     "present presets referenced in the playlist will also be "
                                                     "included. The --include and --exclude "
                                                     "options are mutually exclusive.  Providing both will result in "
                                                     "an error and script termination."), action="store",
                        default=None)
    parser.add_argument("--exclude", type=str, help=("A comma-separated list of preset/playlist IDs/names to EXCLUDE "
                                                     "from the output presets file. When this option is provided the "
                                                     "script will start with all presets in the --presets file "
                                                     "exclude those in the list. If a playlist is provided in the "
                                                     "list the playlist itself will be excluded. If the --deep option "
                                                     "is present presets referenced in the playlist will also be"
                                                     "excluded. The --include and --exclude options are mutually "
                                                     "exclusive.  Providing both will result in an error and script "
                                                     "termination."), action="store",
                        default=None)
    parser.add_argument('--deep', help=("If the --deep option is present, presets referenced in playlists will "
                                        "be included/excluded depending on the presence of the --include or --exclude "
                                        "options.  If neither the --include or --exclude options are present the "
                                        "--deep option will be ignored."), action='store_true')

    parser.add_argument('--test', help="Processing will be performed, but no files will be saved.",
                        action='store_true')
    parser.add_argument('--quiet', help="Suppresses all non-error output.",
                        action='store_true')

    args = parser.parse_args()
    data_dir = str(args.data_dir)
    wled_rel_dir = str(args.wled_dir)
    environment = str(args.env) if args.env is not None else None
    properties_option = str(args.properties) if args.properties is not None else None
    property_definitions = args.define
    presets_option = str(args.presets) if args.presets is not None else None
    segments_option = str(args.segments) if args.segments is not None else None
    cfg_option = str(args.cfg) if args.cfg is not None else None
    definitions_rel_dir = str(args.definitions_dir)
    output_dir = str(args.output_dir)
    effects_file = str(args.effects)
    palettes_file = str(args.palettes)
    colors_file = str(args.colors)
    suffix = "-{suffix}".format(suffix=args.suffix) if args.suffix is not None else ''
    include_list = str(args.include).split(',') if args.include is not None else None
    exclude_list = str(args.exclude).split(',') if args.exclude is not None else None
    deep = args.deep
    test_mode = args.test
    quiet_mode = args.quiet

    init_logger()

    if not quiet_mode:
        get_logger().info("OPTION VALUES ...")
        get_logger().info("  data_dir: " + data_dir)
        get_logger().info("  wled_dir: " + wled_rel_dir)
        get_logger().info("  definitions_dir: " + definitions_rel_dir)
        get_logger().info("  output_dir: " + output_dir)
        get_logger().info("  environment: " + str(environment))
        get_logger().info("  property_definitions: " + str(property_definitions))
        get_logger().info("  suffix: '{suffix}'".format(suffix=suffix))
        get_logger().info("  include_list: " + str(include_list))
        get_logger().info("  exclude_list: " + str(exclude_list))
        get_logger().info("  deep: " + str(deep))
        get_logger().info("  test: " + str(test_mode))

    wled_yaml2json(data_dir=data_dir,
                   wled_rel_dir=wled_rel_dir,
                   environment=environment,
                   properties=properties_option,
                   property_definitions=property_definitions,
                   presets=presets_option,
                   segments=segments_option,
                   cfg=cfg_option,
                   output_dir=output_dir,
                   definitions_rel_dir=definitions_rel_dir,
                   effects=effects_file,
                   palettes=palettes_file,
                   colors=colors_file,
                   suffix=suffix,
                   include_list=include_list,
                   exclude_list=exclude_list,
                   deep=deep,
                   test_mode=test_mode,
                   quiet_mode=quiet_mode)


def wled_yaml2json(*,
                   data_dir=DEFAULT_DATA_DIR,
                   wled_rel_dir=DEFAULT_WLED_DIR,
                   definitions_rel_dir=DEFAULT_DEFINITIONS_DIR,
                   environment=DEFAULT_ENVIRONMENT,
                   properties=None,
                   property_definitions=None,
                   presets=None,
                   cfg=None,
                   output_dir=DEFAULT_OUTPUT_DIR,
                   segments=None,
                   effects=DEFAULT_EFFECTS_FILE_NAME,
                   palettes=DEFAULT_PALETTES_FILE_NAME,
                   colors=DEFAULT_COLORS_FILE_NAME,
                   suffix=None,
                   include_list=None,
                   exclude_list=None,
                   deep=False,
                   test_mode=False,
                   quiet_mode=False):
    if include_list is not None and exclude_list is not None:
        raise ValueError("The --include and --exclude options are mutually exclusive and cannot both be provided.")

    if cfg is not None and presets is None:
        raise ValueError("Cannot process config file without presets file.")

    os.makedirs(output_dir, exist_ok=True)

    configuration = WledConfiguration(data_dir, wled_rel_dir, definitions_rel_dir, environment, properties, segments,
                                      effects, palettes, colors)

    wled_dir = configuration.wled_dir
    effects_path = configuration.effects_path
    palettes_path = configuration.palettes_path
    colors_path = configuration.colors_path
    segments_path = configuration.segments_path
    properties_path = configuration.properties_path

    presets_paths = find_path_list(wled_dir, environment, presets,
                                   DEFAULT_PRESETS_FILE_BASE) if presets is not None else None
    cfg_paths = find_path_list(wled_dir, environment, cfg, DEFAULT_CFG_FILE_BASE) if cfg is not None else None

    if not quiet_mode:
        get_logger().info("INPUT FILE PATHS ...")
        get_logger().info("  effects_path: {path}".format(path=effects_path))
        get_logger().info("  palettes_path: {path}".format(path=palettes_path))
        get_logger().info("  colors_path: {path}".format(path=colors_path))
        get_logger().info("  segments_path: {path}".format(path=segments_path))
        get_logger().info("  properties_path: {path}".format(path=properties_path))
        get_logger().info("  presets_paths: {path}".format(path=presets_paths))
        get_logger().info("  cfg_paths: {path}".format(path=cfg_paths))

        get_logger().info("LOADING PROPERTIES ...")
        get_logger().info("  From: {file}".format(file=properties_path))
    placeholder_replacer = load_placeholder_replacer(properties_path, environment, property_definitions)

    presets_processor = PresetsFileProcessor(presets_paths, segments_path, environment, palettes_path, effects_path,
                                             colors_path, include_list, exclude_list, deep, output_dir,
                                             placeholder_replacer, suffix, test_mode, quiet_mode)
    presets_processor.process()
    presets_data = presets_processor.get_processed_data()
    presets_json_path = presets_processor.get_json_file_path()

    cfg_processor = CfgFileProcessor(cfg_paths, presets_data, output_dir, placeholder_replacer, suffix, test_mode,
                                     quiet_mode)
    cfg_processor.process()
    cfg_json_path = cfg_processor.get_json_file_path()

    return presets_json_path, cfg_json_path


def load_placeholder_replacer(properties_path: str, environment: str, property_definitions: list):
    if properties_path is not None:
        properties_data = load_yaml_file(properties_path)
        placeholder_replacer = WledPlaceholderReplacer(properties_data, environment)
        if property_definitions is not None and len(property_definitions) > 0:
            properties = []
            for property_definition in property_definitions:
                properties.append(tuple(property_definition.split('=')))
            placeholder_replacer.add_properties(properties)
    else:
        placeholder_replacer = None

    return placeholder_replacer


if __name__ == '__main__':
    main(sys.argv[0], sys.argv[1:])
