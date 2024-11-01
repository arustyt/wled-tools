from dateutil.rrule import *

FREQUENCIES = {'YEARLY': YEARLY, 'MONTHLY': MONTHLY, 'WEEKLY': WEEKLY, 'DAILY': DAILY, 'HOURLY': HOURLY,
               'MINUTELY': MINUTELY, 'SECONDLY': SECONDLY}


def get_frequency(frequency_string: str):
    return FREQUENCIES[frequency_string.upper()] if frequency_string.upper() in FREQUENCIES else None


def get_byweekday(dow, occurrence):
    day_of_week_abbreviation = dow.upper()[0:2]
    if day_of_week_abbreviation == 'MO':
        weekday_obj = MO(occurrence)
    elif day_of_week_abbreviation == 'TU':
        weekday_obj = TU(occurrence)
    elif day_of_week_abbreviation == 'WE':
        weekday_obj = WE(occurrence)
    elif day_of_week_abbreviation == 'TH':
        weekday_obj = TH(occurrence)
    elif day_of_week_abbreviation == 'FR':
        weekday_obj = FR(occurrence)
    elif day_of_week_abbreviation == 'SA':
        weekday_obj = SA(occurrence)
    elif day_of_week_abbreviation == 'SU':
        weekday_obj = SU(occurrence)
    else:
        raise ValueError("Invalid day of week.")

    return weekday_obj


def interpret_general_rrule(frequency, by_month, by_weekday, first_day_of_year):
    holiday_date = rrule(frequency, dtstart=first_day_of_year, count=1, bymonth=by_month, byweekday=by_weekday)

    return holiday_date[0]


def interpret_easter_rrule(frequency, by_easter, first_day_of_year):
    holiday_date = rrule(frequency, dtstart=first_day_of_year, count=1, byeaster=by_easter)

    return holiday_date[0]
