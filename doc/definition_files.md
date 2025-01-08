# Definition Files Specifications
This section covers the various definition files used by the wled-tools. 
These files fall into three different categories:
1. WLED Version Dependent Files - Files that are WLED version dependent.  These files should work for anyone 
that understands English. However, they may need to be updated for new WLED 
releases. Files in this category include: [palettes.yaml](#palettes), [effects.yaml](#effects).
2. Files that are WLED independent.  This category includes only [colors.yaml](#colors).
3. Files that are likely dependent on individual preferences and/or locale, and 
potentially on WLED version. These files include [holidays.yaml](#holidays) and 
[holiday_presets.yaml](#holiday_presets).

## WLED Version Dependent Files

### /etc/palettes.yaml {#palettes}
This file contains a single top-level "palettes" entry that contains a list
of palette definitions. Each definition includes:

| YAML key               | Type/Value Range | Description                                                                                                                                                                 |
|------------------------|------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| palettes[]             | Object           | Each item in the list represents a WLED palette.                                                                                                                            |
| palettes[].id          | Integer          | The WLED assigned ID integer for the palette.                                                                                                                               |
| palettes[].name        | String           | The name of the palette that will be used in presets YAML files to reference this palette. Normally this would be the WLED assigned name but you can change it if you like. |
| palettes[].description | String           | Is an optional description of the palette.                                                                                                                                  |


Here is a snippet from palettes.yaml.
```
palettes:
- id: 0
  name: Default
  desc: The palette is automatically selected depending on the effect. For most effects, this is the primary color
- id: 1
  name: Random Cycle
  desc: The palette changes to a random one every few seconds. Subject to change
- id: 2
  name: Color 1
  desc: A palette consisting only of the primary color
  .
  .
  .
```
### /etc/effects.yaml  {#effects}
This file contains a single top-level "effects" entry that contains a list
of effect definitions with structure that is analogous to palettes.yaml. Each definition includes:

| YAML key              | Type/Value Range | Description                                                                                                                                                               |
|-----------------------|------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| effects[]             | Object           | Each item in the list represents a WLED effect.                                                                                                                           |
| effects[].id          | Integer          | The WLED assigned ID integer for the effect.                                                                                                                              |
| effects[].name        | String           | The name of the effect that will be used in presets YAML files to reference this effect. Normally this would be the WLED assigned name but you can change it if you like. |
| effects[].description | String           | Is an optional description of the effect.                                                                                                                                 |


Here is a snippet from effects.yaml.
```
effects:
- id: 0
  name: Solid
  desc: Solid primary color on all LEDs
- id: 1
  name: Blink
  desc: Blinks between primary and secondary color
- id: 2
  name: Breathe
  desc: Fades between primary and secondary color
  .
  .
  .
```

## WLED Independent Files

### /etc/colors.yaml {#colors}
This file contains a single top-level "colors" entry that contains a list
of color definitions. The data in this file was originally source from 
https://htmlcolors.com/color-names. Each definition includes: 

| YAML key      | Type/Value Range | Description                                                                                                                                     |
|---------------|------------------|-------------------------------------------------------------------------------------------------------------------------------------------------|
| colors[]      | Object           | Each item in the list defines a color name/code pair.                                                                                           |
| colors[].name | String           | The name of the color.                                                                                                                          |
| colors[].code | String           | The hexadecimal RGB code, without the leading # sign. The code value must be enclosed in quotes so it is interpreted as a string, not a number. |


Here is a snippet from colors.yaml.

```
colors:
- code: '000000'
  name: Black
- code: '0C090A'
  name: Night
- code: '2C3539'
  name: Gunmetal
- code: '2B1B17'
  name: Midnight
- code: '34282C'
  name: Charcoal
  ```
## User Preference/Locale Dependent Files

These files contain the data to be used to determine which set of WLED presets 
(and possibly which WLED config file) to be used on a given day. You may want 
to modify these files based on your personal preferences and/or locale. 

### /etc/holidays.yaml {#holidays}
This functionality was initially envisioned to enable defining WLED presets 
for specific public holidays.  However, the concept has evolved to include 
defining WLED presets for any day (or days) that are "special" for a given 
locale or individual. In the discussion below, the word "holiday" refers to any 
"special" day (or days).

Holidays.yaml contains a single top-level "holidays" entry that contains a list of
objects, one for each holiday. Individual holidays can be defined by either a fixed date or a variable date.

Fixed-date holidays occur on a specific day of the year, for example, New Years Day and Valentine's Day. 
The day of the year is formatted as 'MMDD' and must appear in quotes to force interpretation as a string. 

Variable-date holidays are those that must be defined by rules (see [dateutil.rrule](https://dateutil.readthedocs.io/en/stable/rrule.html)).
Examples include Easter or in the US, Memorial Day and Thanksgiving. Variable-date rule
definitions have two variations, depending on whether the holiday is based on the date Easter.

This table shows YAML structure used to define each of these holiday variants:

| YAML key                                | Type/Value Range            | Description                                                                                                                                                                                                                                                                                                                                                                                                                                                             |
|-----------------------------------------|-----------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| holidays.<*name*>                       | Object                      | A holiday object where <*name*> is the holiday name.                                                                                                                                                                                                                                                                                                                                                                                                                    |
| ***FIXED DATE HOLIDAY***                |                             | *Defines a holiday with a fixed date.*                                                                                                                                                                                                                                                                                                                                                                                                                                  |
| holidays.<*name*>.date                  | String                      | The date of the holiday as 'MMDD'. The date value must be enclosed in quotes to force interpretation as a string, not a number.                                                                                                                                                                                                                                                                                                                                         |
| ***VARIABLE NON-EASTER BASED HOLIDAY*** |                             | *Defines a variable-date holiday that is **not** based on the date of Easter.*                                                                                                                                                                                                                                                                                                                                                                                          |
| holidays.<*name*>.rrule                 | Object                      | An object containing the holiday rule                                                                                                                                                                                                                                                                                                                                                                                                                                   |
| holidays.<*name*>.rrule.frequency       | String                      | Must be present and is the frequency at which this holiday occurs. Typically this will be **YEARLY**, but it must be one of **YEARLY**, **MONTHLY**, **WEEKLY**, or **DAILY**.                                                                                                                                                                                                                                                                                          |
| holidays.<*name*>.rrule.interval        | Integer                     | If present, it is the interval of *frequency* at which this holiday occurs, e.g. if *frequency* is **YEARLY** and *interval* is 2 the holiday will occur once every two years (see example below). Default value is 1.                                                                                                                                                                                                                                                  |
| holidays.<*name*>.rrule.mod             | Integer                     | If present, the result of *frequency* % *interval* at which this holiday occurs, e.g. if *frequency* is **YEARLY**, *interval* is 2, *mod* is 0 the holiday will occur on even years, or if *mod* is 1 the holiday will occur on odd years (see example below). Default value is 0.                                                                                                                                                                                     |
| holidays.<*name*>.rrule.month           | Integer [1-12]              | If present, it must be either an integer, meaning the month to apply the recurrence to.                                                                                                                                                                                                                                                                                                                                                                                 |
| holidays.<*name*>.rrule.day_of_week     | String or list of strings   | If present, must be one of (**MO**, **TU**, **WE**, **TH**, **FR**, **SA**, **SU**) or a list of these values. Each day of the week can, optionally, be followed by an integer argument enclosed in parentheses, e.g. TU(2). The value is the occurrence of this weekday in the period. For example, with **MONTHLY**, or with **YEARLY** and *month* provided, using TU(2) in *day_of_week* will specify the second Tuesday of the month where the recurrence happens. |
| holidays.<*name*>.rrule.day_of_month    | Integer or list of integers | Day or days of the month on which the holiday can occur.                                                                                                                                                                                                                                                                                                                                                                                                                |
| ***VARIABLE EASTER BASED HOLIDAY***     |                             | *Defines a variable-date holiday that is based on the date of Easter.*                                                                                                                                                                                                                                                                                                                                                                                                  |
| holidays.<*name*>.rrule                 | Object                      | An object containing the holiday rule                                                                                                                                                                                                                                                                                                                                                                                                                                   |
| holidays.<*name*>.rrule.frequency       | String                      | The frequency a which this holiday occurs. Typically this will be YEARLY, but it must be one of YEARLY, MONTHLY, WEEKLY, or DAILY.                                                                                                                                                                                                                                                                                                                                      |
| holidays.<*name*>.rrule.by_easter       | Integer                     | The number of days before (-negative integer) or after (positive integer) easter.                                                                                                                                                                                                                                                                                                                                                                                       |

US national election day provides an example when *interval* and *mod* would be applicable. US national elections occur 
in even years, the first Tuesday after a Monday in November. In this case, *frequency* would be **YEARLY**, *interval* 
would be 2 (every other year), and *mod* would be 0 (even years). Also, the first Tuesday after a Monday can only occur on days 2-8 of the month.
This definition is included in the example below.

Here is a snippet from holidays.yaml containing all three variations.
```yaml
# Date format is MMDD
holidays:
  new_years_day:
    date: '0101'
  martin_luther_king_jr_day:
    rrule: 
      frequency: YEARLY
      month: 1
      day_of_week: MO(3)
  ground_hog_day:
    date: '0202'
  valentines_day:
    date: '0214'
  presidents_day:
    rrule: 
      frequency: YEARLY
      month: 2
      day_of_week: MO(3)
  mardi_gras:
    rrule:
      frequency: YEARLY
      by_easter: -47
...
  election_day:
    rrule:
      frequency: YEARLY
      interval: 2
      mod: 0
      month: 11
      day_of_week: TU
      day_of_month: [2, 3, 4, 5, 6, 7, 8]
```

### /etc/holiday_presets.yaml {#holiday_presets}

Holiday_presets.yaml defines what WLED presets to use on a given day based 
a single date or a range of days.  Although "holiday" is in the name, 
definitions in this file do not necessarily have to correspond to holidays 
defined in holidays.yaml.  For example, you could define a preset to use
on your birthday based on the date (MMDD), alone.

Variable-date holiday entries have two variations. 
The first variation is for holidays **not** based on the date of Easter and 
include:

| YAML key                          | Type/Value Range | Description                                                                                                                                                               |
|-----------------------------------|------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| holidays.<*name*>                 | Object           | A holiday object where <*name*> is arbitrary but will usually be the name of the associated holiday.                                                                      |
| holidays.<*name*>.start_date      | **See note 1**   | The first date on which the associated holiday presets will be used.                                                                                                      |
| holidays.<*name*>.end_date        | **See note 1**   | The last date on which the associated holiday presets will be used.                                                                                                       |
| holidays.<*name*>.presets         | **See note 2**   | The date-specific part of the presets file name.                                                                                                                          |
|                                   |                  | **See note 3**                                                                                                                                                            |
| holidays.<*name*>.<*dow*>         | Object           | A day-of-the-week object to override settings from the main group. <*dow*> must be one of ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun'].                              |
| holidays.<*name*>.<*dow*>.holiday | String           | (Optional) Holiday name to be used for this day of the week. If not present, the holiday from the enclosing object will be used.                                          |
| holidays.<*name*>.<*dow*>.presets | String           | (Optional) The date-specific part of the presets file name to be used for this day of the week. If not present, the above presets from the enclosing object will be used. |


> NOTES:
> 1. Start_date and end_date can be either a specific date (MMDD) or the
>   name of a holiday in holidays.yaml. In addition, the date or holiday name
>   can be followed by -N or +N where N is the number of days before or after
>   the date or holiday.
> 2. The date-specific part of the presets file name is described in [File Name Conventions](file_name_conventions.md).
> 3. The day-of-the-week elements are optional and allow tailoring presets for specific 
>  days of the week within the holiday date range. The above holiday name and/or 
>  presets values will be used for days of the week not specified or for 
>  presets/holiday values not specified for a given day of the week. This
>  group can be repeated to specify multiple days of the week. 

Here is a snippet from holiday_presets.yaml.

```yaml
holidays:
  normal_night:
    start_date: new_years_day
    end_date: new_years_eve
    presets: twinkle
    mon:
      holiday: normal_monday
    tue:
      holiday: normal_tuesday
    wed:
      holiday: normal_wednesday
    thu:
      holiday: normal_thursday
    fri:
      holiday: normal_friday
  new_years_day:
    start_date: new_years_day
    end_date: new_years_day+6
    presets: newyears
  martin_luther_king_jr_day:
    start_date: martin_luther_king_jr_day-2
    end_date: martin_luther_king_jr_day
    presets: mlkday
  black_history_month:
    start_date: '0201'
    end_date: '0301-1'
    presets: black_history_month
  ground_hog_day:
    start_date: ground_hog_day
    end_date: ground_hog_day
    presets: groundhogday
  superbowl_sunday:
    start_date: '0211'
    end_date: '0211'
    presets: superbowl
  valentines_day:
    start_date: valentines_day
    end_date: valentines_day
    presets: valentinesday
  presidents_day:
    start_date: presidents_day-2
    end_date: presidents_day
    presets: patriotic
  mardi_gras:
    start_date: mardi_gras
    end_date: mardi_gras
    presets: mardigras
  st_patricks_day:
    start_date: st_patricks_day-7
    end_date: st_patricks_day
    presets: stpatricksday
  ash_wednesday:
    start_date: ash_wednesday
    end_date: ash_wednesday
    presets: twinkle
  lent:
    start_date: ash_wednesday
    end_date: holy_saturday
    presets: twinkle
  palm_sunday:
    start_date: palm_sunday
    end_date: palm_sunday
    presets: easter
```
