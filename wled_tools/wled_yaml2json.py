import argparse
import os
import sys
from pathlib import Path

from data_files.cfg_file_processor import CfgFileProcessor
from data_files.presets_file_processor import PresetsFileProcessor
from data_files.wled_placeholder_replacer import WledPlaceholderReplacer
from wled_constants import DEFAULT_WLED_DIR, DEFAULT_ENVIRONMENT, DEFAULT_SEGMENTS_FILE_BASE, DEFAULT_PROPERTIES_FILE, \
    DEFAULT_OUTPUT_DIR, DEFAULT_DEFINITIONS_DIR, DEFAULT_EFFECTS_FILE, DEFAULT_PALETTES_FILE, DEFAULT_COLORS_FILE, \
    DEFAULT_PROPERTIES_FILE_BASE, DEFAULT_PRESETS_FILE_BASE, DEFAULT_CFG_FILE_BASE, YAML_EXTENSION, DEFAULT_DATA_DIR
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
    parser.add_argument("--env", type=str, help="The name of the environment for this execution.  Currently recognized "
                                                "environments are: {environments}. The environment name is used to "
                                                "construct file names for properties, presets, segments, and cfg "
                                                "files per the rules above in the description.",
                        action="store", default=DEFAULT_ENVIRONMENT)
    parser.add_argument("--properties", type=str, help="A file (YAML) defining properties for placeholder replacement "
                                                       "within config and preset files.  The file name is relative to "
                                                       "the --wled_dir directory. The properties file name will be "
                                                       "determined as described above where the default file base is "
                                                       "'properties'.",
                        action="store", default=DEFAULT_PROPERTIES_FILE)

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
                                                    DEFAULT_EFFECTS_FILE + "' is used.",
                        action="store", default=DEFAULT_EFFECTS_FILE)
    parser.add_argument("--palettes", type=str, help="WLED palette definitions file-name (YAML) relative to the "
                                                     "--definitions_dir directory. If not specified, '" +
                                                     DEFAULT_PALETTES_FILE + "' is used.",
                        action="store", default=DEFAULT_PALETTES_FILE)
    parser.add_argument("--colors", type=str, help="HTML color-name definitions file-name (YAML) relative to the "
                                                   "--definitions_dir directory. If not specified, '" +
                                                   DEFAULT_COLORS_FILE + "' is used.",
                        action="store", default=DEFAULT_COLORS_FILE)
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
    wled_dir = "{base}/{rel_dir}".format(base=data_dir, rel_dir=str(args.wled_dir))
    environment = str(args.env) if args.env is not None else None
    properties_option = str(args.properties) if args.properties is not None else None
    presets_option = str(args.presets) if args.presets is not None else None
    segments_option = str(args.segments) if args.segments is not None else None
    cfg_option = str(args.cfg) if args.cfg is not None else None
    definitions_dir = "{base}/{rel_dir}".format(base=data_dir, rel_dir=str(args.definitions_dir))
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

    if not quiet_mode:
        print("\nOPTION VALUES ...")
        print("  wled_dir: " + wled_dir)
        print("  definitions_dir: " + definitions_dir)
        print("  output_dir: " + output_dir)
        print("  environment: " + str(environment))
        print("  suffix: '{suffix}'".format(suffix=suffix))
        print("  include_list: " + str(include_list))
        print("  exclude_list: " + str(exclude_list))
        print("  deep: " + str(deep))
        print("  test: " + str(test_mode))

    wled_yaml2json(wled_dir=wled_dir,
                   environment=environment,
                   properties=properties_option,
                   presets=presets_option,
                   segments=segments_option,
                   cfg=cfg_option,
                   output_dir=output_dir,
                   definitions_dir=definitions_dir,
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
                   wled_dir=DEFAULT_WLED_DIR,
                   definitions_dir=DEFAULT_DEFINITIONS_DIR,
                   environment=DEFAULT_ENVIRONMENT,
                   properties=None,
                   presets=None,
                   cfg=None,
                   output_dir=DEFAULT_OUTPUT_DIR,
                   segments=DEFAULT_SEGMENTS_FILE_BASE,
                   effects=DEFAULT_EFFECTS_FILE,
                   palettes=DEFAULT_PALETTES_FILE,
                   colors=DEFAULT_COLORS_FILE,
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

    effects_path = build_path(definitions_dir, environment, effects, DEFAULT_EFFECTS_FILE)

    palettes_path = build_path(definitions_dir, environment, palettes, DEFAULT_PALETTES_FILE)
    colors_path = build_path(definitions_dir, environment, colors, DEFAULT_COLORS_FILE)

    segments_path = build_path(wled_dir, environment, segments, DEFAULT_SEGMENTS_FILE_BASE)
    properties_path = build_path(wled_dir, environment, properties, DEFAULT_PROPERTIES_FILE_BASE)
    presets_paths = build_path_list(wled_dir, environment, presets,
                                    DEFAULT_PRESETS_FILE_BASE) if presets is not None else None
    cfg_paths = build_path_list(wled_dir, environment, cfg, DEFAULT_CFG_FILE_BASE) if cfg is not None else None

    if not quiet_mode:
        print("\nINPUT FILE PATHS ...")
        print("  effects_path: {path}".format(path=effects_path))
        print("  palettes_path: {path}".format(path=palettes_path))
        print("  colors_path: {path}".format(path=colors_path))
        print("  segments_path: {path}".format(path=segments_path))
        print("  properties_path: {path}".format(path=properties_path))
        print("  presets_paths: {path}".format(path=presets_paths))
        print("  cfg_paths: {path}".format(path=cfg_paths))

        print("\nLOADING PROPERTIES ...")
        print("  From: {file}".format(file=properties_path))
    placeholder_replacer = load_placeholder_replacer(properties_path, environment)

    presets_processor = PresetsFileProcessor(presets_paths, segments_path, environment, palettes_path, effects_path,
                                             colors_path, include_list, exclude_list, deep, output_dir,
                                             placeholder_replacer, suffix, test_mode, quiet_mode)
    presets_processor.process()
    presets_data = presets_processor.get_processed_data()
    presets_json_path = presets_processor.get_json_file_path()

    cfg_processor = CfgFileProcessor(cfg_paths, presets_data, output_dir, placeholder_replacer, suffix, test_mode, quiet_mode)
    cfg_processor.process()
    cfg_json_path = cfg_processor.get_json_file_path()

    return presets_json_path, cfg_json_path


def load_placeholder_replacer(properties_path: str, environment: str):
    if properties_path is not None:
        properties_data = load_yaml_file(properties_path)
        placeholder_replacer = WledPlaceholderReplacer(properties_data, environment)
    else:
        placeholder_replacer = None

    return placeholder_replacer


def build_path_list(directory: str, environment: str, files_str: str, file_base: str):
    paths = []
    if files_str is not None and len(files_str) > 0:
        for file_nickname in files_str.split(','):
            path = build_path(directory, environment, file_nickname, file_base)
            if path is not None:
                paths.append(path)

    return paths


def build_path(directory: str, environment: str, file_nickname: str, file_base: str):
    candidates = get_file_name_candidates(environment, file_nickname, file_base)

    if len(candidates) == 0:
        raise ValueError("No candidates found for '{base}' file.".format(base=file_base))

    for candidate in candidates:
        file_path = "{dir}/{file}".format(dir=directory, file=candidate) if len(candidate) > 0 else None
        if file_path is not None:
            path = Path(file_path)
            if path.is_file():
                return file_path

    raise ValueError("None of the candidate files exist: '{candidates}'.".format(candidates=str(candidates)))


def get_file_name_candidates(environment: str, file_nickname: str, file_base: str):
    candidates = []
    if file_nickname is not None and file_nickname.endswith(YAML_EXTENSION):
        candidates.append(file_nickname)
        if not file_nickname.startswith(file_base):
            candidates.append("{base}-{file}".format(base=file_base, file=file_nickname))
    else:
        if file_nickname is not None and not file_nickname.startswith(file_base):
            add_nickname_candidates(candidates, "{base}-{nickname}".format(base=file_base, nickname=file_nickname),
                                    environment)

        add_nickname_candidates(candidates, file_nickname, environment)
        add_nickname_candidates(candidates, file_base, environment)

    return candidates


def add_nickname_candidates(candidates, file_nickname, environment):
    if file_nickname is not None:
        if environment is not None:
            candidates.append("{nickname}-{env}.yaml".format(nickname=file_nickname, env=environment))

        candidates.append("{nickname}.yaml".format(nickname=file_nickname))


if __name__ == '__main__':
    main(sys.argv[0], sys.argv[1:])
