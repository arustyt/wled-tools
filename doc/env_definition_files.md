# Environment Definition Files Specifications
This section covers files that can be used to define various WLED environments within a given household.
These files are:
- properties YAML file
- segments YAML file

The following subsections use examples of properties and segments files for two environments:
- ```lab_300``` is a "development" environment. The lab_300 environment consists of a 300-LED strip 
controlled by a DIY ESP8266-based controller.  It is used for testing preset and configuration 
files before moving them into production.
- ```roof``` is a "production" environment.  It is made up of two LED pixel strings (439 LEDs total) along 
the roof-line of the house controlled by a QuinLED DigiQuad controller.
 
## Properties YAML file {#properties}
Properties can be used to substitute values in a WLED presets or configuration file.  
Property substitution can be used to replace any *value* in a presets or configuration 
file by wled_yaml2json.py.

Property substitution is specified by enclosing the property name with a leading '${' and closing '}' 
In a presets or configuration YAML file item this would something like:
```
   name: ${property_name}
```

Here is an example properties file.
```
lab_300:
  sunset:
    begin_dark_duration: 10
    sun_duration: 600
    sunset_duration: 600
    end_dark_duration: 10
    begin_dark_transition: 0
    sun_transition: 30
    sunset_transition: 30
    end_dark_transition: 0
    sunset_sx: 61
  playlist_duration: 300
  playlist_repeat: 2
roof:
  sunset:
    begin_dark_duration: 10
    sun_duration: 6000
    sunset_duration: 18000
    end_dark_duration: 10
    begin_dark_transition: 0
    sun_transition: 300
    sunset_transition: 300
    end_dark_transition: 0
    sunset_sx: 90
  playlist_duration: 3000
  playlist_repeat: 0
```
Multiple levels in the properties file can be specified by concatenating consecutive levels, 
separated by periods '.'.  From the example properties file above, the following could be 
used to vary the speed setting for a preset.
```
    .
    .
    .
    sx: ${sunset.sunset_sx}
    .
    .
    .
```
Note that [wled_yaml2json.py](wled_yaml2json.py.md) will automatically prepend the environment 
(specified with the --env option) to the property name and look for that value first. For example,
if the --env lab_300 is specified on the command line, properties will first be searched for 
```lab_300.sunset.sunset_sx```. If that property is not found, the property name without environment will be 
searched, e.g. ```sunset.sunset_sx```.

The example above with ```--env lab_300``` specified would result in the following after substitution 

```
    .
    .
    .
    sx: 61
    .
    .
    .
```
The example above with ```--env roof``` specified would result in the following after substitution: 

```
    .
    .
    .
    sx: 90
    .
    .
    .
```

The normal/default name for the properties file is ```properties.yaml```.  You can also define 
specific properties files for different environments by including the environment in the file name.
For example with two environments, lab_300 
and roof, wled_yaml2json.py would look for ```properties-lab_300.yaml``` or ```properties-roof.yaml``` 
depending on the --env option. Thus, there are two ways that properties enable using a 
single presets file across multiple environments.

## Segments YAML file {#segments}

The segments file provides a way to define WLED segments and access them by name in a presets file.
It is recommended that the **segments.yaml** file be used for defining segment name and layout by only including 
the **n**, **start** and **stop** key value pairs.
While it is allowed to include any WLED segment key/value pairs in the segment definitions, 
it is not recommended.
Doing so will reduce the reusability of the segment definitions. 

> **NOTE:** *The **id** key should never be included in a segment definition, thus allowing the
> segment **id**s to be generated when the presets YAML file is processed by **wled_yaml2json.py**.*

Here is an example segments file.
```
lab_300:
  segments:
  - n: First Floor
    start: 0
    stop: 150
  - n: Second Floor
    start: 150
    stop: 300
  - n: Whole Roof
    start: 0
    stop: 300
roof:
  segments:
  - n: First Floor
    start: 0
    stop: 222
  - n: Second Floor
    start: 222
    stop: 439
  - n: Whole Roof
    start: 0
    stop: 439
```

Usage of segments definitions is done by using the wled-tools specific element, 
```
seg_name: <segment name>
``` 
instead of the WLED "n", "start", and "stop"

Given the example data above, this entry in a presets YAML segment definition:
```yaml
  seg:
  - id: 0
    ...
    seg_name: Whole Roof
  ```
Would result in the following in the generated WLED presets JSON file for the ```lab_300``` 
environment:
```json lines:
    "seg": [
      {
        "id": 0,
        ...
        "n": "Whole Roof",
        "start": 0,
        "stop": 300,
        ...
```
or, for the ```roof``` environment:
```json lines
     "seg": [
      {
        "id": 0,
        ...
        "n": "Whole Roof",
        "start": 0,
        "stop": 439,
        ...
```
Similar to properties processing, [wled_yaml2json.py](wled_yaml2json.py.md) will automatically look 
for an environment-specific (specified with the --env option) set of segments when run.

The normal/default name for the segments file is ```segments.yaml```.  You can also define 
specific segments files for different environments by including the environment in the file name.  
For example with two environments, ```lab_300``` and ```roof``` wled_yaml2json.py would look for 
```segments-lab_300.yaml``` or ```segments-roof.yaml``` 
depending on the --env option. Thus, there are two ways that segments can be defined
across multiple environments.
