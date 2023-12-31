# File Name Conventions

## Default Definition File Names
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