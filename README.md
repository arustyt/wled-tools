# wled-tools - A toolset to manage WLED configurations

## Overview

This project was created to enable the automation of WLED controllers presets
and configuration. The end goal was to have presets defined for various 
holidays throughout the year and for the automation to determine the 
appropriate holiday (based on the current date) and then configura a WLED controller
with the corresponding presets. The initial plan was to use Home Assistant 
for automation but, in the end, automation was implemented via AppDaemon.

Sub-goals were to be able to:
 - Keep the preset/configuration data separate from code,
 - Reference WLED palettes and effects by name,
 - Specify palette colors by name or in HTML format, e.g. RRGGBB,
 - Reuse segment definitions across presets and refer to them by name, 
 - Define playlists by referencing preset names,
 - Support property definition and replacement to allow a single presets 
   file to be used in multiple environments, e.g. development vs. production,
 - Enable combining multiple sets of preset definitions into a coherent set
   of presets for a WLED controller.

This project uses YAML as the configuration language. YAML was chosen because
it is compatible with JSON but is more compact, syntactically simpler and more human-readable. 

### Primary tools:
- **[wled_tools/wled_yaml2json.py](doc/wled_yaml2json.md)** - converts YAML files into 
WLED JSON presets and configuration files.  The functionality is exposed as a callable
Python function.
- **[wled_tools/wled_upload.py](doc/wled_upload.md)** - uploads a JSON presets and
configuration files to a WLED controller. The functionality is exposed as a callable
Python function.

### Secondary tools:
- **[wled_tools/wled_holiday.py](doc/wled_holiday.md)** - determines the "holiday" based on a date. The 
functionality is exposed as a callable Python class method.
- **[wled_tools/wled_update_definitions.py](doc/wled_update_definitions.md)** - updates palette and effects 
definition files from a running WLED controller.

### Integration tools:
- **[wled_tools/wled_4_ha.py](doc/wled_4_ha.md)** - initially intended to be *the* automation integration
tool, it uses wled_holiday.py, wled_yaml2json.py, and wled_upload.py to
build and upload date-appropriate presets to a WLED controller.
- **[wled_tools/wled_4_appdaemon.py](doc/wled_4_appdaemon.md)** - is an AppDaemon wrapper for wled_4_ha.py

### Miscellaneous tools:
- **[wled_tools/wled_jsondiff.py](doc/wled_jsondiff.md)** - outputs the differences between two JSON files.
Have switched to using [JSON Diff](https://jsondiff.org/) for a more useful comparison.
- **[wled_tools/misc/json2yaml.py](doc/json2yaml.md)** - converts a JSON format file to YAML. This is useful 
for converting an existing JSON presets file into YAML for modification and use with 
the tools above.
- **[wled_tools/misc/yaml2json.py](doc/yaml2json.md)** - dumps the contents of a YAML file as a Python
dict.

## Environment and Dependencies

### Python
Wled-tools was developed under Python 3.7 but has been run on up to 3.12 thus far.
- Python 3.7+

### Python packages
See [wled_tools/requirements.txt](wled_tools/requirements.txt) for most up-to-date list. Higher versions
of these packages may function correctly but have not been tested.
- PyYAML==6.0.1
- python-dateutil==2.8.2
- requests==2.31.0
- urllib3==1.26.12
- hassapi~=0.2.0
- GitPython == 3.1.40

### Related Repositories
Wled-config is a sibling repository that contains working examples of the data files used by wled-tools.

## Additional Details
Additional details can be found [here](doc/README.md).

## License
This software is provided under the [MIT License](LICENSE).
