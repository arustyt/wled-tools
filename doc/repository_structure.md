## wled-tools Repository Structure
### wled-tools
- **wled-tools**
  - **/wled_tools** - most top level scripts and supporting packages
    - **/appdaemon_tools** - AppDaemon support modules
    - **/config** - configuration modules
    - **/data_files** - modules to handle WLED presets and configuration files
    as well the files defining properties and LED segments.
    - **/definition_files** - modules to handle files for WLED palettes and effects,
    as well as named colors.
    - **/wled_utils** - various utility modules
    - **/misc** - less commonly used top level scripts
    - **/wled_utils** - various utility modules
  - **/data** - config file for wled_4_ha.py and wled_4_appdaemon.py
    - **/etc** - test palettes, effects, colors and holidays files
    - **/presets** - test presets, config and segments definition files
      - **/generated** - default directory where output files
  - **/doc** - documentation files

### wled-config
> NOTE: I have not made my wled-config repository public, but the structure is defined below.
> This is the default structure expected by the `wled-tools` code.
- wled-config - wled_4_ha job configuration files.
  - **/etc** - palettes, effects, colors and holidays definition files
  - **/presets** - presets, config, properties and segments definition files
    - **/generated** - default directory where output files are written
