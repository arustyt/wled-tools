# Definition Files Specifications
This section covers the various definition files used by the wled-tools. 
These files fall into three different categories:
1. WLED Version Dependent Files - Files that are WLED version dependent.  These files should work for anyone 
that understands English. However, they may need to be updated for new WLED 
releases. Files in this category include palettes.yaml, effects.yaml.
2. Files that are WLED independent.  This category includes only colors.yaml.
3. Files that are likely dependent on your preferences and/or locale, and 
potentially on WLED version.

## WLED Version Dependent Files

### /etc/palettes.yaml
This file contains a single top-level "palettes" entry that contains a list
of palette definitions. Each definition includes:
- **id** is the WLED assigned ID integer for the palette,
- **name** is the name of the palette. Normally these would be the WLED
assigned names but you can change them if you like.
- **desc** is an optional description of the palette.

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
### /etc/effects.yaml
This file contains a single top-level "effects" entry that contains a list
of effect definitions with structure that is analogous to palettes.yaml.

Each definition includes:
- **id** is the WLED assigned ID integer for the effect,
- **name** is the name of the effect. Normally these would be the WLED
assigned names but you can change them if you like.
- **desc** is an optional description of the effect.

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

### /etc/colors.yaml
This file contains a single top-level "colors" entry that contains a list
of color definitions. The data in this file was originally source from 
https://htmlcolors.com/color-names. 

Each definition includes: 
- **code** is the hexadecimal RGB code, without the leading # sign. The code
value must be enclosed in quotes so it is interpreted as a string, not a
number.
- **name** is the name of the color.

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

### /etc/holidays.yaml
Holidays.yaml contains a single top-level "holidays" entry that contains a set of
objects, one for each holiday. Holidays can be defined as a specific day of the year 
which is appropriate for holidays such as New Years Day and Valentines Day.  
The day of the year is formatted as 'MMDD'
and must appear in quotes to be interpreted as a string. 
Alternatively, a holiday can be defined in a rule (see dateutil.rrule). A rule
is needed to define variable holidays such as Easter or in US, Memorial Day.

A fixed-date holiday entry includes:
- **The Holiday Name**
  - **date** is the date of the holiday as 'MMDD'. The date
  value must be enclosed in quotes so it is interpreted as a string, not a
  number.

Variable-date holiday entries have two variations. 
The first variation is for holidays **not** based on the date of Easter and 
include:
- **The Holiday Name**
  - **rrule** object containing the holiday rule
    - **frequency** - is the frequency a which this holiday occurs. Typically
    this will be YEARLY, but it must be one of YEARLY, MONTHLY, WEEKLY, or DAILY.
    - **month** - is the month of the year as an integer 1 through 12
    - **day_of_week** - is the day of the week.  Must be one of 
    (MO, TU, WE, TH, FR, SA, SU).
    - **occurrence** - which occurrence of the day of the week for the holiday 

The second variation for a variable-date holiday is for holidays that are based
on the date of Easter:
- **The Holiday Name**
  - **rrule** object containing the holiday rule
    - **frequency** - is the frequency a which this holiday occurs. Typically
    this will be YEARLY, but it must be one of YEARLY, MONTHLY, WEEKLY, or DAILY.
    - **by_easter** - is the number of days before (-int) or after (+int) easter 


Here is a snippet from holidays.yaml containing all three variations.
```
# Date format is MMDD
holidays:
  "new_years_day":
    date: '0101'
  martin_luther_king_jr_day:
    rrule: 
      frequency: YEARLY
      month: 1
      day_of_week: MO
      occurrence: 3
  ground_hog_day:
    date: '0202'
  valentines_day:
    date: '0214'
  presidents_day:
    rrule: 
      frequency: YEARLY
      month: 2
      day_of_week: MO
      occurrence: 4
  mardi_gras:
    rrule:
      frequency: YEARLY
      by_easter: -47
```

### /etc/holiday_lights.yaml

Holiday_lights.yaml defines what WLED presets to use on a given day based 
a single date or a range of days.  Although "holiday" is in the name, 
definitions in this file do not necessarily have to correspond to holidays 
defined in holidays.yaml.  For example, you could define a preset to use
on your birthday based on the date (MMDD), alone.

Variable-date holiday entries have two variations. 
The first variation is for holidays **not** based on the date of Easter and 
include:
- **The Holiday Name** - This name is arbitrary but will usually be the name 
of the associated holiday.
  - **start_date** is the first date on which the associated holiday presets 
  will be used (see NOTE below).
  - **end_date** - is the last date on which the associated holiday presets 
  will be used (see NOTE below).
  - **lights** - the day-specific part of the presets file name 
  (see [File Name Conventions](file_name_conventions.md)).

> NOTE: Start_date and end_date can be either a specific date (MMDD) or the
> name of a holiday in holidays.yaml. In addition, the date or holiday name
> can be followed by -N or +N where N is the number of days before or after
> the date or holiday.

Here is a snippet from holiday_lights.yaml.

```
# Date format is MMDD
holidays:
  "new_years_day":
    start_date: '0101'
    end_date: '0101+6'
    lights: newyearsday
  martin_luther_king_jr_day:
    start_date: martin_luther_king_jr_day
    end_date: martin_luther_king_jr_day
    lights: mlkday
  ground_hog_day:
    start_date: ground_hog_day
    end_date: ground_hog_day
    lights: groundhogday
  valentines_day:
    start_date: valentines_day
    end_date: valentines_day
    lights: valentinesday
  presidents_day:
    start_date: presidents_day
    end_date: presidents_day
    lights: presidentsday
  mardi_gras:
    start_date: mardi_gras
    end_date: mardi_gras
    lights: mardigras
  st_patricks_day:
    start_date: st_patricks_day-7
    end_date: st_patricks_day
    lights: stpatricksday
  lent:
    start_date: ash_wednesday
    end_date: holy_saturday
    lights: lent
  palm_sunday:
    start_date: palm_sunday
    end_date: palm_sunday
    lights: palm_sunday
```
