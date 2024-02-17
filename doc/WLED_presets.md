# WLED Presets File Specification
This section covers the WLED Presets YAML files that can be used as inputs to wled_yaml2json.py to generate presets 
JSON files for uploading to a WLED instance. If you are not familiar with YAML, have a look at 
[YAML Ain’t Markup Language (YAML™)](YAML.md).

## Properties {#properties}

Property substitution, as discussed in [Environment Definition Files Specifications](env_definition_files.md), 
can be used anywhere in the WLED Presets YAML file. Typically, property substitution would be used to set YAML values. 
Theoretically, it should also work for replacing YAML keys, although I have never had need for that and have not 
tested it.

## Defaults {#defaults}

Wled_yaml2json.py supports a non-WLED data section identified with the top level key, **defaults**. If present, 
**defaults** can contain one or both a **preset** and a **segment** key. As the name suggests, keys and values under 
these define default values for presets and segments, respectively. These defaults are applied at the beginning of 
processing each preset in the YAML file.  The default values can be overridden in a preset or segment if the 
corresponding key/value is present. If multiple **defaults** keys are present, all entries but the last one  
will be silently ignored.

Here is a sample of defaults usage:

```YAML
defaults:
  preset:
    mainseg: 0
    bri: 128
  segment:
    ix: 128
    sx: 128
```

## Preset Settings {#presets}

Most key/value pairs are copied directly to the JSON file after any required property substitution.
Exceptions to this direct-copying include effects, palettes, colors, segment settings and one non-WLED key, id.

### Effects {#effects}
Effects can be specified in one of two ways. First is using the standard WLED **fx** key and specifying an effect by id.

This package introduces the ability to specify an effect by name. This is done by using the **fx_name** key with an 
effect name from [effects.yaml](definition_files.md#effects).  The value of **fx_name** is case-insensitive and can 
have embedded spaces and/or underscores. For example,
```yaml
      fx_name: Fireworks Starburst
      fx_name: fireworks starburst
      fx_name: fireworks_starburst
      fx_name: FireworksStarburst
      fx_name: FiReWoRkS sTaRbUrSt
```
all refer to WLED effect #89 and will result in 
```json
      "fx": 89,
```
in the generated WLED presets JSON file.

### Palettes {#palettes}
Palettes can be specified in one of two ways. First is using the standard WLED **pal** key and specifying an effect by id.

This package allows you to specify a palette by name. This is done by using the **pal_name** key with a 
palette name from [palettes.yaml](definition_files.md#palettes).  The value of **pal_name** is case-insensitive and can 
have embedded spaces and/or underscores. For example,
```yaml
    pal_name: Orange & Teal
    pal_name: orange & teal
    pal_name: orange_&_teal
    pal_name: Orange&Teal
    pal_name: OrAnGe & TeAl
```
all refer to WLED palette #44 and will result in 
```json
    "pal": 44,
```
in the generated WLED presets JSON file.

### Colors {#colors}
Colors can be specified in multiple ways. First is using the standard WLED **col** key and specifying a list of 
individual RGB colors. In YAML, specifying red, green, blue would look like this:
```yaml
    col:
    - - 255
      - 0
      - 0
    - - 0
      - 255
      - 0
    - - 0
      - 0
      - 255 
```
This package supports two alternative methods to specify colors. First you can use hex codes with or without a 
leading # sign. Using this notation, the above color list would look like this in YAML:

```yaml
    col:
    - 'FF0000'
    - '00FF00'
    - '0000FF'
```
or
```yaml
    col:
    - '#FF0000'
    - '#00FF00'
    - '#0000FF'
```
The quotes are required to force interpretation as strings.

The second alternative to specifying colors is by a name in [colors.yaml](definition_files.md#colors). 
Using this notation, the above color list would look like this in YAML:

```yaml
    col:
    - Red
    - Green
    - Blue
```
As with effects and palettes, the color names are case-insensitive and can have embedded spaces and/or underscores.

In all cases above YAML allow expressing lists in the form of a comma separated list enclosed in square brackets
([item, item, ...]). Using this syntax, the above examples reduce to:

```yaml
    col:
    - [255, 0, 0]
    - [0, 255, 0]
    - [0, 0, 255] 
```
or
```yaml
    col: [[255, 0, 0], [0, 255, 0], [0, 0, 255]] 
```
or
```yaml
    col: ['FF0000', '00FF00', '0000FF']
```
or
```yaml
    col: [Red, Green, Blue]
```

As a convenience, you can use this shorthand to specify an empty list of colors when using a palette that does not use the 
primary, secondary, and tertiary colors.
```yaml
    col: []
```

### Segments and Settings {#segments}
Segments within the **seg** list can be specified in multiple ways. First is using the standard WLED key/value pairs
to specify individual keys such as **n**, **grp**, **of**, **spc**, etc. 

A more succinct and reusable mechanism is to utilize segment names to refer to segment definitions. 
This is done by using the **seg_name** key with a name from [segments.yaml](env_definition_files.md#segments).
The value of **seg_name** is case-insensitive and can have embedded spaces and/or underscores. For example,
```yaml
    seg_name: Whole Roof
    seg_name: whole roof
    seg_name: whole_roof
    seg_name: WholeRoof
    seg_name: WhOlE RoOf
```
all refer to the same segment definition in segments.yaml.

#### Segment Parameters {#parameters} 

It is possible to specify variations to a segment definition in segments.yaml with the following syntax:
```yaml
    seg_name: <segment name>(parm=value,...)
```
Zero or more spaces are allowed between the <segment name> and the open parenthesis, '(' of the parameter list.
The parentheses enclose a list of one or more comma-separated parameter=value pairs. Currently supported segment parameters are:
**start**, **stop**, **spc**, **grp**, and **of**. Setting these values via parameters will override corresponding
values in segments.yaml. Here is an example:

```yaml
    seg:
    - seg_name: Whole Roof(start=0,spc=4,grp=2)
      ...
    - seg_name: Whole Roof(start=2,spc=2,grp=1)
      ...
    - seg_name: Whole Roof(start=3,spc=4,grp=2)
```
This set of parameterized segments could be used to create a LED pattern of
>    Red - Red - White - Green - Green - White ...
#### Segment Patterns {#patterns} 

I got the idea for the following from [HandyDadTV](https://www.youtube.com/@handydadtv), 
specifically from this [video](https://www.youtube.com/watch?v=i_OtZHUFpG0).

Another supported parameterized variant uses the parm value of **pat**. This parameter allows you to specify a pattern
for the LEDs in the string/strip instead. The value is a sequence of numbers representing the pattern separated by delimiters.
The delimiter can be any single character other than a left parenthesis or a number. In addition, exactly 
one of the numbers must be enclosed in parentheses to indicate which number in the pattern belongs is associated with 
segment. Here is an example using '/' as the delimiter.

```yaml
    seg:
    - seg_name: Whole Roof(pat=(2)/1/2/1) # This segment is the 1st in the pattern and consists of 2 LEDs.
      ...
    - seg_name: Whole Roof(pat=2/(1)/2/1) # This segment is the 2nd in the pattern and consists of 1 LED.
      ...
    - seg_name: Whole Roof(pat=2/1/(2)/1) # This segment is the 3rd in the pattern and consists of 2 LEDs.
      ...
    - seg_name: Whole Roof(pat=2/1/2/(1)) # This segment is the 4th in the pattern and consists of 1 LED.
      ...
```

The numbers in the pattern are used to compute the **start**, **grp** and **spc** values for each segment. 

> NOTES:
> 1. If the numbers in the patterns for all associated segments are not identical, the results are undefined.
> 2. The **pat** parameter should not be mixed with **start**, **stop**, **spc**, **grp**, and **of**. Doing so will
>    result in an error or unexpected behavior.

###  Segments and Defaults
Values for segment keys can be defaulted and overridden at several levels. At the beginning of processing of
each preset, preset and segment defaults are set to the values in the **defaults.preset** and **defaults.segment** 
portion of the presets YAML file.

Within the first segment of a preset, if **seg_name** is present the segment values are determined and 
possibly overridden in the following order:
1. Values in **defaults.segment**.
2. Values in segments.yaml for the segment specified in **seg_name**.
3. If **seg_name** value includes parameters, those are applied next.
4. Any values explicitly specified via the preset segment keys.

For subsequent segments in the same preset, settings from the previous segment become the starting point
for this segment and are possibly overridden in the following order:
1. Values in from the previous segment.
2. Values in segments.yaml for the segment specified in **seg_name**.
3. If **seg_name** value includes parameters, those are applied next.
4. Any values explicitly specified via the preset segment keys.

As a result, after the first segment it is only necessary to specify settings that are different from the
previous segment, potentially reducing the duplicated YAML content. Here is an example showing an entire preset:
```text
01  |   - n: Valentines - Dissolve Pink White Red White
02  |     'on': true
03  |     seg:
04  |     - id: 0
05  |       seg_name: Whole Roof(pat=(2)/1/2/1)
06  |       bri: 128
07  |       cct: 127
08  |       col:
09  |       - Neon Pink
10  |       - Black
11  |       - Black
12  |       fx_name: Dissolve
13  |       ix: 80
14  |       mi: false
15  |       'on': true
16  |       pal_name: Default
17  |       rev: false
18  |       sel: true
19  |       sx: 128
20  |     - id: 1 
21  |       seg_name: Whole Roof(pat=2/(1)/2/1)
22  |       col:
23  |       - White
24  |       - Black
25  |       - Black
26  |     - id: 2 
27  |       seg_name: Whole Roof(pat=2/1/(2)/1)
28  |       col:
29  |       - Red
30  |       - Black
31  |       - Black
32  |     - id: 3 
33  |       seg_name: Whole Roof(pat=2/1/2/(1))
34  |       col:
35  |       - White
36  |       - Black
37  |       - Black
38  |     transition: 7
```
The first segment covers line numbers 4-19 (16 lines). Subsequent segments on include the **id**, **seg_name**, 
and **col** requiring 9 fewer lines and no duplication.  Note that this entire preset requires 38 lines but expands 
to 154 lines in pretty-print JSON.

### Playlist settings {#playlist}
\* expansion
### Preset Identifier {#id}
- id

And finally, wled_yaml2json.py supports two YAML file structure variations for WLED presets which will be covered in 
[YAML Structure Variations](# variations).

## Example WLED Preset YAML file
We'll discuss various parts of interest in the file in subsequent subsections.

### Example Conventions
These are the preset conventions that I have adopted and are used in this example.

```defaults``` will be discussed below.

```Preset 0``` is always present and empty. Its use causes WLED defaults to be applied the the LEDs.

```Preset 1``` turns the LEDs off.  This is the preset to apply at boot in LED Preferences.

```Preset 2``` turns the LEDs on.  I don't use this preset directly but it is included for 
               completeness.

```Preset 3``` is the preset that scheduled (~30 minutes before sunset) when the LEDs are turned on. 
               In the example below it is a playlist containing Sunrise effect in sunset mode.  
               The sunset is followed by a playlist named "Playlist Du Jour" which varies depending on
               the day of the year.

```Presets >3``` includes the "Playlist Du Jour" preset and its specified presets.

```
01 |defaults:
02 |  preset:
03 |    mainseg: 0
04 |    bri: 128
05 |    transition: 7
06 |'0': {}
07 |'1':
08 |  n: 'Off'
09 |  win: T=0
10 |'2':
11 |  n: 'On'
12 |  win: T=1
13 |'3':
14 |  n: Sunset Playlist
15 |  'on': true
16 |  playlist:
17 |    dur:
18 |    - ${sunset.sunset_duration}
19 |    - 10
20 |    end: 0
21 |    ps:
22 |    - Sunset
23 |    - Playlist Du Jour
24 |    r: false
25 |    repeat: 1
26 |    transition:
27 |    - ${sunset.sunset_transition}
28 |    - 0
29 |'20':
30 |  n: Playlist Du Jour
31 |  'on': true
32 |  playlist:
33 |    dur:
34 |    - ${playlist_duration} * 2
35 |    end: 0
36 |    ps:
37 |    - Christmas
38 |    - TwinkleFoxRainbow
39 |    r: false
40 |    repeat: ${playlist_repeat}
41 |    transition:
42 |    - 10 * 2
43 |'22':
44 |  n: Christmas
45 |  'on': true
46 |  seg:
47 |  - bri: 128
48 |    col:
49 |    - Red
50 |    - Green
51 |    - White
52 |    fx_name: Running 2
53 |    grp: 1
54 |    id: 0
55 |    ix: 128
56 |    mi: false
57 |    seg_name: First Floor
58 |    'on': true
59 |    pal_name: Default
60 |    rev: true
61 |    sel: true
62 |    spc: 0
63 |    sx: 122
64 |  - id: 1
65 |    seg_name: Second Floor
66 |    rev: false
67 |  transition: 7
68 |'27':
69 |  n: TwinkleFoxRainbow
70 |  'on': true
71 |  seg:
72 |  - bri: 128
73 |    col: []
74 |    fx_name: Twinklefox
75 |    grp: 1
76 |    id: 0
77 |    ix: 255
78 |    mi: false
79 |    seg_name: Whole Roof
80 |    'on': true
81 |    pal_name: Rainbow
82 |    rev: false
83 |    sel: true
84 |    spc: 0
85 |    sx: 125
86 |  transition: 7
```

## YAML Structure Variations (# variations)
