# `wled_yaml2json.py`
## Program
```
usage: wled_yaml2json.py [-h] [--data_dir DATA_DIR] [--wled_dir WLED_DIR]
                         [--env ENV] [--properties PROPERTIES]
                         [--define DEFINE] [--presets PRESETS]
                         [--segments SEGMENTS] [--cfg CFG]
                         [--output_dir OUTPUT_DIR]
                         [--definitions_dir DEFINITIONS_DIR]
                         [--effects EFFECTS] [--palettes PALETTES]
                         [--colors COLORS] [--suffix SUFFIX]
                         [--include INCLUDE] [--exclude EXCLUDE] [--deep]
                         [--test] [--quiet] [--merge_playlists]
```
Converts YAML preset and config files to WLED JSON format.

The names of files located in --wled_dir 
(--properties, --segments, --presets, and --cfg) follow these rules to
determine the file name.

```   
   env     File     File
  option   option   option ends
  present  present  with .yaml   File name
  =======  =======  ===========  ===========================================
     Y        Y         N        <file option value>-<env option value>.yaml
     N        Y         N        <file option value>.yaml
     *        Y         Y        <file option value>
     Y        N         N        <default file base>-<env option value>.yaml
     N        N         N        <default file base>.yaml
```
options:

```  -h, --help            show this help message and exit
  --data_dir DATA_DIR   Directory from which wled_dir and definitions_dir are
                        relative. If not specified, '.' is used.
  --wled_dir WLED_DIR   WLED data file location. Applies to presets, cfg, and
                        segments files. If not specified, 'presets' is used.
  --env ENV             The name of the environment for this execution. The
                        environment name is used to construct file names for
                        properties, presets, segments, and cfg files per the
                        rules above in the description.
  --properties PROPERTIES
                        A file (YAML) defining properties for placeholder
                        replacement within config and preset files. The file
                        name is relative to the --wled_dir directory. The
                        properties file name will be determined as described
                        above where the default file base is 'properties'.
  --define DEFINE, -D DEFINE
                        Defines property to be added to the properties loaded
                        via --properties. Format is <prop_name>=<prop_value>.
                        Multiple properties can be defined by including
                        multiple occurrences of the -D option.
  --presets PRESETS     A comma-separated list of WLED preset file names
                        (YAML). The file names are relative to the --wled_dir
                        directory. Note that preset IDs must be unique across
                        all preset files. The presets file name will be
                        determined as described above where the default file
                        base is 'presets'.
  --segments SEGMENTS   Segments definition file name (YAML) relative to the
                        --wled_dir directory. The segments file name will be
                        determined as described above where the default file
                        base is 'segments'.
  --cfg CFG             WLED cfg file name (YAML) relative to the --wled_dir
                        directory. The cfg file name will be determined as
                        described above where the default file base is 'cfg'.
  --output_dir OUTPUT_DIR
                        Directory where generated files output. If not
                        specified, 'generated' is used.
  --definitions_dir DEFINITIONS_DIR
                        Definition file location. Applies to effects,
                        palettes, and colors files. If not specified, 'etc' is
                        used.
  --effects EFFECTS     WLED effect definition file name (YAML) relative to
                        the --definitions_dir directory. If not specified,
                        'effects.yaml' is used.
  --palettes PALETTES   WLED palette definitions file-name (YAML) relative to
                        the --definitions_dir directory. If not specified,
                        'palettes.yaml' is used.
  --colors COLORS       HTML color-name definitions file-name (YAML) relative
                        to the --definitions_dir directory. If not specified,
                        'colors.yaml' is used.
  --suffix SUFFIX       Suffix to be appended to the output file names,
                        preceded by a '-', before the '.json' extension.
  --include INCLUDE     A comma-separated list of preset/playlist IDs/names to
                        INCLUDE in the output presets file. When this option
                        is provided the script will start with an empty set of
                        presets and include only those in the list. If a
                        playlist is provided in the list the playlist itself
                        will be included. If the --deep option is present
                        presets referenced in the playlist will also be
                        included. The --include and --exclude options are
                        mutually exclusive. Providing both will result in an
                        error and script termination.
  --exclude EXCLUDE     A comma-separated list of preset/playlist IDs/names to
                        EXCLUDE from the output presets file. When this option
                        is provided the script will start with all presets in
                        the --presets file exclude those in the list. If a
                        playlist is provided in the list the playlist itself
                        will be excluded. If the --deep option is present
                        presets referenced in the playlist will also
                        beexcluded. The --include and --exclude options are
                        mutually exclusive. Providing both will result in an
                        error and script termination.
  --deep                If the --deep option is present, presets referenced in
                        playlists will be included/excluded depending on the
                        presence of the --include or --exclude options. If
                        neither the --include or --exclude options are present
                        the --deep option will be ignored.
  --test                Processing will be performed, but no files will be
                        saved.
  --quiet               Suppresses all non-error output.
  --merge_playlists     Causes like-named playlists to be merged.
```
## Function

This functionality is also exposed as a callable function.
Parameter definitions follow the associated
options of the program.

wled_yaml2json.wled_yaml2json(*,
                   data_dir='.',
                   wled_rel_dir='presets',
                   definitions_rel_dir='etc',
                   environment=None,
                   properties=None,
                   property_definitions=None,
                   presets=None,
                   cfg=None,
                   output_dir='generated',
                   segments=None,
                   effects='effects.yaml',
                   palettes='palettes.yaml',
                   colors='colors.yaml',
                   suffix=None,
                   include_list=None,
                   exclude_list=None,
                   deep=False,
                   test_mode=False,
                   quiet_mode=False,
                   merge_playlists=False)
