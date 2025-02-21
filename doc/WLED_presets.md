# WLED Presets File Specification
This section covers the WLED Presets YAML files that can be used as inputs to wled_yaml2json.py to generate presets 
JSON files for uploading to a WLED instance. If you are not familiar with YAML, have a look at 
[YAML Ain’t Markup Language (YAML™)](YAML.md).

## Properties {#properties}

Property substitution, as discussed in [Environment Definition Files Specifications](env_definition_files.md), 
can be used anywhere in the WLED Presets YAML file. Typically, property substitution would be used to set YAML values. 

## Defaults {#defaults}

**Wled_yaml2json.py** supports a non-WLED data section identified with the top level key, **defaults**. 
If present, 
**defaults** can contain **preset** and/or **segment** keys. As the name suggests, keys and values under 
these define default values for presets and segments, respectively. These defaults are applied at the beginning of 
processing each preset in the YAML file.  The default values can be overridden in a preset or segment if the 
corresponding key/value is present. If multiple **defaults** keys are present, all entries but the last one  
will be silently ignored.

Here is an example of defining defaults:

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
Effects can be specified in one of two ways. First is using the standard WLED **fx** key and specifying 
an effect by numeric id.

This package introduces the ability to specify an effect by name. This is done by using the **fx_name** 
key with an 
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
Similar to Effects, Palettes can be specified in one of two ways. 
First is using the standard WLED **pal** key and specifying an effect by numeric id.

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

When defining segments within a YAML preset, the following are supported: 
- **wled_yaml2json.py** - specific key/value pairs defined above such as
**pal_name** and **fx_name** as well as colors by name.
After performing appropriate substitutions (including properties) the 
resulting key/value pairs are added to the segment.
- All other key/value pairs will be copied to the segment, as is, after any 
applicable property substitutions.

#### Segment IDs
Each segment within a WLED JSON presets file must have an associated segment **id**. 
**wled_yaml2json.py** supports multiple ways to provide segment **id**s in the 
presets YAML file.

A segment **id** can be hard coded into each segment in the **seg** list.
If an **id** key is not provided for a segment, **wled_yaml2json.py** will 
auto-generate an **id** for the segment.

#### seg_name

The **seg_name** key followed by a segment name defined in [segments.yaml](env_definition_files.md#segments) 
can be used to assign associated segment parameters.
The value of **seg_name** is case-insensitive and can have embedded spaces
and/or underscores.
Single and double quotes are optional.
For example,
```yaml
    seg_name: Whole Roof
    seg_name: "Whole Roof"
    seg_name: 'Whole Roof'
    seg_name: whole roof
    seg_name: whole_roof
    seg_name: WholeRoof
    seg_name: WhOlE RoOf
```
all refer to the same segment definition in segments.yaml.

When **seg_name** is present, the associated segment values defined in **segments.yaml** 
are added to the preset.

#### Segment Name Parameterization

In addition to the segment key/value pairs in **segments.yaml**, 
the value of the **seg_name** key can be
parameterized using the following syntax:
```yaml
    seg_name: <segment name>(parm=value,...)
```
Zero or more spaces are allowed between the `<segment name>` and the open parenthesis
'(' of the parameter list.
The parentheses enclose a list of one or more comma-separated **parameter=value** pairs.
Segment parameterization supports two parameter sets:
1. A subset of standard WLED segment key/value pairs.
2. An LED pattern definition.
The following subsections discuss these two cases.

##### Segment Name (WLED name/value pairs) {#parameters} 

Currently supported segment parameters are:
**start**, **stop**, **spc**, **grp**, and **of**.
Setting these values via parameters will override corresponding
values in **segments.yaml**.
Here is an example:

```yaml
    ...
    seg:
    - seg_name: Whole Roof(start=0,spc=4,grp=2)
      fx_name: Solid
      col:
      - red
      ...
    - seg_name: Whole Roof(start=2,spc=2,grp=1)
      col:
      - white
      ...
    - seg_name: Whole Roof(start=3,spc=4,grp=2)
      col: 
      - green
    ...
```
As an example, the above set of parameterized segments could be used to create a LED pattern of
>    Red - Red - White - Green - Green - White ...

##### Segment Name - Patterns {#patterns} 

I got the idea for the following from [HandyDadTV](https://www.youtube.com/@handydadtv), 
specifically from this [video](https://www.youtube.com/watch?v=i_OtZHUFpG0).

The second parameterized variant uses a single parameter: **pat=**. 
The **pat** parameter allows you to specify a pattern for the LEDs in the segment. 
The value is a sequence of numbers representing the pattern, separated by delimiters.
The delimiter can be any single character other than a left parenthesis or a number. 
In addition, exactly one of the numbers must be enclosed in parentheses to indicate 
which number in the pattern belongs is associated with this specific segment. 
Here is an example using '/' as the delimiter that could be used to create the same 
LED pattern as above. 

```yaml
    ...
    seg:
    - seg_name: Whole Roof(pat=(2)/1/2/1) # This segment is the 1st in the pattern and consists of 2 LEDs.
      fx_name: Solid
      col:
      - red
      ...
    - seg_name: Whole Roof(pat=2/(1)/2/1) # This segment is the 2nd in the pattern and consists of 1 LED.
      col:
      - white
      ...
    - seg_name: Whole Roof(pat=2/1/(2)/1) # This segment is the 3rd in the pattern and consists of 2 LEDs.
      col:
      - green
      ...
    - seg_name: Whole Roof(pat=2/1/2/(1)) # This segment is the 4th in the pattern and consists of 1 LED.
      col:
      - white
    ...
```

The numbers in the pattern are used to compute the **start**, **grp** and **spc** values for each segment in the 
generated WLED presets JSON file. 

> NOTES:
> 1. If the numbers in the patterns for all associated segments are not identical, 
> the results are undefined.
> 2. The **pat** parameter should not be mixed with **start**, **stop**, **spc**, **grp**, and **of**. Doing so will
> result in an error or unexpected behavior.

###  Segments and Defaults
Values for segment keys can be defaulted and overridden at several levels. At the beginning of processing of
each preset, preset and segment defaults are set to the values in the **defaults.preset** and **defaults.segment** 
portion of the presets YAML file.

Within the first segment of a preset, if **seg_name** is present the segment values are determined and 
possibly overridden in the following order:
1. Values in **defaults.segment**.
2. Values in segments.yaml for the segment specified in **seg_name**.
3. If **seg_name** value includes parameters, those are applied next.
4. Any values explicitly specified via the preset segment keys are applied last.

For later segments in the same preset, settings from the previous segment become the starting point
for the next segment and are possibly overridden in the following order:
1. Values from the previous segment.
2. Values in segments.yaml for the segment specified in **seg_name**.
3. If **seg_name** value includes parameters, those are applied next.
4. Any values explicitly specified via the preset segment keys are applied last.

As a result, after the first segment, it is only necessary to specify settings that are different from the
previous segment, potentially reducing the duplicated YAML content. Here is an example showing an entire preset:
```yaml
   - n: Valentines - Dissolve Pink White Red White
     'on': true
     seg:
     - id: 0
       seg_name: Whole Roof(pat=(2)/1/2/1)
       bri: 128
       cct: 127
       col:
       - Neon Pink
       - Black
       - Black
       fx_name: Dissolve
       ix: 80
       mi: false
       'on': true
       pal_name: Default
       rev: false
       sel: true
       sx: 128
     - id: 1 
       seg_name: Whole Roof(pat=2/(1)/2/1)
       col:
       - White
       - Black
       - Black
     - id: 2 
       seg_name: Whole Roof(pat=2/1/(2)/1)
       col:
       - Red
       - Black
       - Black
     - id: 3 
       seg_name: Whole Roof(pat=2/1/2/(1))
       col:
       - White
       - Black
       - Black
     transition: 7
```
The first segment covers line numbers 4-19 (16 lines). Later segments only include the **id**, **seg_name**, 
and **col** requiring nine fewer lines and no duplication.  Note that this entire preset requires 38 lines in YAML but 
expands to 154 lines in pretty-print JSON.

### Playlist settings {#playlist}
There are two features for use in playlists, both shown in this example:

```yaml
  - n: Playlist Du Jour
    'on': true
    playlist:
      dur:
      - ${playlist_duration} * 5
      end: 'Off'
      ps:
      - Blends
      - Fireworks Starburst
      - Dissolve Red White Blue White
      - Chunchun
      - Colorwaves
      r: false
      repeat: ${playlist_repeat}
      transition:
      - 0 * 5
```

First, preset references can be made by preset names or ids.  This applies to the preset list in **ps** and to
the **end** preset.  Playlist names are case-insensitive and can have embedded spaces and/or underscores.

The second feature is shorthand for the **dur** and **transition** lists. 
Places where the list has multiple 
elements with same values can be combined into a single list element with the value, followed by an asterisk (*) and 
then the number of repetitions.  In the example above:

```yaml
      dur:
      - ${playlist_duration} * 5
      ...
      transition:
      - 0 * 5

```
produces the same result as:
```yaml
      dur:
      - ${playlist_duration}
      - ${playlist_duration}
      - ${playlist_duration}
      - ${playlist_duration}
      - ${playlist_duration}
      ...
      transition:
      - 0
      - 0
      - 0
      - 0
      - 0
```

### Presets YAML File Structure {#structure}

> #### Example Conventions
> These are the preset conventions applied in the examples below.
> 
> ```Preset 0:``` is always present and empty. Its use causes WLED defaults to be applied the LEDs.
> 
> 
> ```Preset 1:``` turns the LEDs off.  This is the preset to apply at boot in LED Preferences.
> 
> ```Preset 2:``` is the preset scheduled (at 35 minutes before sunset) when the LEDs are turned on. 
>   In these examples it is a playlist containing the Sunrise effect in sunset mode. The sunset is followed 
>   by a playlist named "Playlist Du Jour" which varies depending on
>   the day of the year.
> 
> ```Presets >3:``` includes the "Playlist Du Jour" playlist and its specified presets.

All the above information can be combined into one of two supported YAML file structure variations.

#### Presets YAML File Structure #1 - The Original Structure

The first structure most closely mimics the WLED presets JSON structure. Aside from the defaults settings the 
remainder of the file structure is basically a YAML version of the JSON file with the additional features discussed 
above. Here is an example of this structure:

```
defaults:
  preset:
    mainseg: 0
    bri: 128
    transition: 7
'0': {}
'1':
  n: 'Off'
  win: T=0
'2':
  n: Sunset Playlist
  'on': true
  playlist:
    dur:
    - ${sunset.sunset_duration}
    - 10
    end: 0
    ps:
    - Sunset
    - Playlist Du Jour
    r: false
    repeat: 1
    transition:
    - ${sunset.sunset_transition}
    - 0
'20':
  n: Playlist Du Jour
  'on': true
  playlist:
    dur:
    - ${playlist_duration} * 2
    end: 0
    ps:
    - Christmas
    - TwinkleFoxRainbow
    r: false
    repeat: ${playlist_repeat}
    transition:
    - 10 * 2
'22':
  n: Christmas
  'on': true
  seg:
  - bri: 128
    col:
    - Red
    - Green
    - White
    fx_name: Running 2
    grp: 1
    id: 0
    ix: 128
    mi: false
    seg_name: First Floor
    'on': true
    pal_name: Default
    rev: true
    sel: true
    spc: 0
    sx: 122
  - id: 1
    seg_name: Second Floor
    rev: false
  transition: 7
'27':
  n: TwinkleFoxRainbow
  'on': true
  seg:
  - bri: 128
    col: []
    fx_name: Twinklefox
    grp: 1
    id: 0
    ix: 255
    mi: false
    seg_name: Whole Roof
    'on': true
    pal_name: Rainbow
    rev: false
    sel: true
    spc: 0
    sx: 125
  transition: 7
```
The downside of this structure is that you are forced to hardcode the preset IDs. This is not ideal, especially when
you start merging multiple YAML Preset files to generate a single WLED Preset JSON file, which is a supported feature.

**wled_yaml2json.py** supports an alternate preset file structure to remove the need for hard-coding. To be sure, 
it may be desirable to hard-code some preset ids so that known values can be configured for the default boot preset 
id and when scheduling presets. 
# NEEDS WORK
> **Observation:** Initially, config file processing was designed to allow specifying presets by name,
where needed. I got as far as implementing assigning the default boot preset by name when I came to 
the conclusion that it would be better to choose a static configuration convention. 
This convention allows me to use a few hard-coded preset ids (IDs 1 and 2 in my case) and avoid the complexity of 
modifying the WLED configuration for each set of presets.
>
>As for other preset ids like playlists and the associated presets, their ids don't matter to me, so I let 
> **wled_yaml2json.py** generate them.
>
>This observation led to **Presets YAML File Structure #2**.

#### Presets YAML File Structure #2 - The Alternate Structure

The alternate file structure has two top-level keys:
```yaml
defaults:
  ...
presets:
  ...
```
The **defaults** section works the same as described above.

The **presets** section is a list of preset objects. The presets objects themselves are the same as described above 
with the addition of an optional new key, **id**.  If the **id** key is present, its associated value is 
the hard-coded preset id. If **id** is not present, **wled_yaml2json.py** will supply an unused preset 
id to the preset.

The above example in this alternate structure looks like this:
```yaml
defaults:
  preset:
    mainseg: 0
    bri: 128
    transition: 7
presets:
- id: 0
- id: 1
  n: 'Off'
  win: T=0
- id: 2
  n: Sunset Playlist
  'on': true
  playlist:
    dur:
    - ${sunset.sunset_duration}
    - 10
    end: 0
    ps:
    - Sunset
    - Playlist Du Jour
    r: false
    repeat: 1
    transition:
    - ${sunset.sunset_transition}
    - 0
- n: Playlist Du Jour
  'on': true
  playlist:
    dur:
    - ${playlist_duration} * 2
    end: 0
    ps:
    - Christmas
    - TwinkleFoxRainbow
    r: false
    repeat: ${playlist_repeat}
    transition:
    - 10 * 2
- n: Christmas
  'on': true
  seg:
  - bri: 128
    col:
    - Red
    - Green
    - White
    fx_name: Running 2
    grp: 1
    id: 0
    ix: 128
    mi: false
    seg_name: First Floor
    'on': true
    pal_name: Default
    rev: true
    sel: true
    spc: 0
    sx: 122
  - id: 1
    seg_name: Second Floor
    rev: false
  transition: 7
- n: TwinkleFoxRainbow
  'on': true
  seg:
  - bri: 128
    col: []
    fx_name: Twinklefox
    grp: 1
    id: 0
    ix: 255
    mi: false
    seg_name: Whole Roof
    'on': true
    pal_name: Rainbow
    rev: false
    sel: true
    spc: 0
    sx: 125
  transition: 7
```
In this case, preset ids 0, 1, and 2 are hard-coded.  The remainder will be assigned during processing.

#### Presets YAML File Structure #3 - The Hybrid Structure

It is also possible to combine the structures #1 and #2 into a hybrid structure. The following combines the previous 
examples, using the original structure for the hard-coded presets and the alternate structure for the presets 
without assigned ids. 

```yaml
defaults:
  preset:
    mainseg: 0
    bri: 128
    transition: 7
'0': {}
'1':
  n: 'Off'
  win: T=0
'2':
  n: Sunset Playlist
  'on': true
  playlist:
    dur:
    - ${sunset.sunset_duration}
    - 10
    end: 0
    ps:
    - Sunset
    - Playlist Du Jour
    r: false
    repeat: 1
    transition:
    - ${sunset.sunset_transition}
    - 0
presets:
- n: Playlist Du Jour
  'on': true
  playlist:
    dur:
    - ${playlist_duration} * 2
    end: 0
    ps:
    - Christmas
    - TwinkleFoxRainbow
    r: false
    repeat: ${playlist_repeat}
    transition:
    - 10 * 2
- n: Christmas
  'on': true
  seg:
  - bri: 128
    col:
    - Red
    - Green
    - White
    fx_name: Running 2
    grp: 1
    id: 0
    ix: 128
    mi: false
    seg_name: First Floor
    'on': true
    pal_name: Default
    rev: true
    sel: true
    spc: 0
    sx: 122
  - id: 1
    seg_name: Second Floor
    rev: false
  transition: 7
- n: TwinkleFoxRainbow
  'on': true
  seg:
  - bri: 128
    col: []
    fx_name: Twinklefox
    grp: 1
    id: 0
    ix: 255
    mi: false
    seg_name: Whole Roof
    'on': true
    pal_name: Rainbow
    rev: false
    sel: true
    spc: 0
    sx: 125
  transition: 7
```
While supporting a mix of formats #1 and #2 in a single file may not seem necessary, the ability to merge 
multiple preset YAML files into a single WLED preset JSON file is a requirement.
By supporting a mix of structures, it allows merging of files containing both structures.

> **Sidebar:** Support for the original structure will continue indefinitely for this reason: 
> If a WLED presets JSON file is converted to YAML (using **json2yaml.py**) the resulting YAML 
> file will be in the original structure. 
> This makes it an easy way to get a starting YAML file 
> to use with this package to generate WLED presets JSON files.
