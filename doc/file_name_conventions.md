# File Name Conventions

This document covers file naming conventions applied in this software.
While it is not required to follow these conventions doing so will reduce 
the number options that need to be supplied to many of the scripts.
Furthermore, the automation scripts in this package are based on these
conventions and may require modification to function if they are not followed.

File conventions covered in this document are:
- [Definition File Names](#definition_file_names)
- [WLED Presets File Names](#preset_file_names)
- [WLED Config File Names](#config_file_names)

## Definition File Names {#definition_file_names}

### Default Definition File Names
The major scripts in this repository implement these default file base-names and these expected locations:

| Purpose              | File Option Flag | Default File Base-name | Location                 |
|----------------------|------------------|------------------------|--------------------------|
| Effect Definitions   | --effects        | effects                | data_dir/definitions_dir |
| Palette Definitions  | --palettes       | palettes               | data_dir/definitions_dir |
| Color Definitions    | --colors         | colors                 | data_dir/definitions_dir |
| Segment Definitions  | --segments       | segments               | data_dir/wled_dir        |
| Property Definitions | --properties     | properties             | data_dir/wled_dir        |

For definition files, one or two filename candidates will be checked for existence. 
The table below shows what file names will be considered based on values provided 
to the script/function call.

If the value provided with a file option (e.g. --effects, --palettes, etc.) ends with '.yaml.'
it will be interpreted as a complete file name and will be used as-is. In other cases, if an
environment is specified (--env) the file name including the environment will be considered
first, followed by the option file name itself.  This table shows combinations of options and 
the resulting file name(s) that will be considered.  In cases where there is a Primary and 
Secondary file name the Primary file name will be tried first and if it exists it will be used. 
If the Primary file name does not exist the Secondary file name will be tried. If neither file 
exists, a ValueError will be raised.

| Env Option Present | File Option Present | File Option Ends<br/>With .yaml |       Primary File Name       |  Secondary File Name  |
|:------------------:|:-------------------:|:-------------------------------:|:-----------------------------:|:---------------------:|
|         *          |          Y          |                Y                |        \<file_option\>        |          N/A          |
|         N          |          Y          |                N                |     \<file_option\>.yaml      |          N/A          |
|         Y          |          Y          |                N                | \<file_option\>-\<env\>.yaml  | \<file_option\>.yaml  |
|         N          |          N          |                                 |     <default_base\>.yaml      |          N/A          |
|         Y          |          N          |                                 | \<default_base\>-\<env\>.yaml | \<default_base\>.yaml |

This convention provides a way to maintain separate files for each environment, if desired. 
Typically, environment specific files should not be required for effects, palettes, or colors. 
However, they may be appropriate for segments and properties files. Alternatively, segments and
properties files can be divided into sections for each environment.  This will be covered in the
individual sections for each file.   

## WLED Presets File Names {#preset_file_names}
The preset file naming convention is mainly important when using the automation scripts, 
- **wled_4_ha.py** and 
- **wled_4_appdaemon.py** 

This convention is quite straight forward and consists of the prefix "presets-" followed by 
a description of the holiday or purpose of the preset file and finally by the .yaml extension.
```commandline
    presets-<purpose_or_holiday>.yaml
```
A couple of examples are:
- presets-newyears.yaml
- presets-twinkle.yaml

The <purpose_or_holiday> should match the ***presets*** value for the associated holiday
in /etc/holiday_presets.yaml. The examples above match values for new_years_day and 
normal_day, respectively.

## WLED Config File Names {#config_file_names}
When I started this project I naively assumed that config files would generally be
paired with a corresponding presets file.  However, since that beginning I have come 
to realize that configurations do not have to change with each set of presets, 
in fact they are really quite static.  I settled on a preset convention where my 
configurations don't change unless I add LEDS to my setup. I now have two configurations,
one for each environment:
- **cfg-lab_300.yaml** -  which is my WLED development environment, and
- **cfg-roof.yaml** -  which is my WLED production environment, i.e. exterior LEDs.
 
