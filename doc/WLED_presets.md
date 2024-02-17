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
```yaml
    fx: 89
```
in the generated WLED presets JSON file.

### Palettes {#palettes}
Palettes can be specified in one of two ways. First is using the standard WLED **pal** key and specifying an effect by id.

This package introduces the ability to specify a palette by name. This is done by using the **pal_name** key with a 
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
```yaml
    pal: 44
```
in the generated WLED presets JSON file.

### Colors {#colors}
Palettes can be specified in multiple ways. First is using the standard WLED **col** key and specifying a list of lists.
In YAML, specifying red, green, blue would look like this:
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
This package introduces alternative methods to specify colors. First you can use hex codes without the leading # sign. 
Using this notation, the above color list would look like this in YAML:

```yaml
    col:
    - 'FF0000'
    - '00FF00'
    - '0000FF'
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
As with effects and palettes, The color names are case-insensitive and can have embedded spaces and/or underscores.
### Segment settings
   - seg.n/seg.seg_name
### Preset Identifier {#id}
- id
7. \* expansion

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
