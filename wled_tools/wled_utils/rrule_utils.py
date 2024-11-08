import re

from dateutil.rrule import *


YEARLY_STR = 'YEARLY'
MONTHLY_STR = 'MONTHLY'
WEEKLY_STR = 'WEEKLY'
DAILY_STR = 'DAILY'
HOURLY_STR = 'HOURLY'
MINUTELY_STR = 'MINUTELY'
SECONDLY_STR = 'SECONDLY'

FREQUENCIES = {YEARLY_STR: YEARLY, MONTHLY_STR: MONTHLY, WEEKLY_STR: WEEKLY, DAILY_STR: DAILY, HOURLY_STR: HOURLY,
               MINUTELY_STR: MINUTELY, SECONDLY_STR: SECONDLY}
BY_WEEKDAY_RE_STR = "(MO|TU|WE|TH|FR|SA|SU) *([(](-?[1-5])[)])? *$"


def get_frequency(frequency_string: str):
    return FREQUENCIES[frequency_string.upper()] if frequency_string.upper() in FREQUENCIES else None


def get_dow_and_occurrence(dow):
    match = re.match(BY_WEEKDAY_RE_STR, dow)
    if match is None:
        raise ValueError("Invalid weekday spec: {}".format(dow))
    else:
        dow = match.group(1)
        occurrence = match.group(3)
        return dow, int(occurrence) if occurrence is not None else None


def get_byweekday(dow):
    day_of_week_abbreviation, occurrence = get_dow_and_occurrence(dow)
    if day_of_week_abbreviation == 'MO':
        weekday_obj = MO(occurrence) if occurrence is not None else MO
    elif day_of_week_abbreviation == 'TU':
        weekday_obj = TU(occurrence) if occurrence is not None else TU
    elif day_of_week_abbreviation == 'WE':
        weekday_obj = WE(occurrence) if occurrence is not None else WE
    elif day_of_week_abbreviation == 'TH':
        weekday_obj = TH(occurrence) if occurrence is not None else TH
    elif day_of_week_abbreviation == 'FR':
        weekday_obj = FR(occurrence) if occurrence is not None else FR
    elif day_of_week_abbreviation == 'SA':
        weekday_obj = SA(occurrence) if occurrence is not None else SA
    elif day_of_week_abbreviation == 'SU':
        weekday_obj = SU(occurrence) if occurrence is not None else SU
    else:
        raise ValueError("Invalid day of week.")

    return weekday_obj


def interpret_general_rrule(frequency, interval, by_month, by_weekday, by_monthday, start_date):
    holiday_date = rrule(frequency, dtstart=start_date, interval=interval, count=1, bymonth=by_month,
                         byweekday=by_weekday, bymonthday=by_monthday)

    return holiday_date[0]


def interpret_easter_rrule(frequency, interval, by_easter, start_date):
    holiday_date = rrule(frequency, interval=interval, dtstart=start_date, count=1, byeaster=by_easter)

    return holiday_date[0]
