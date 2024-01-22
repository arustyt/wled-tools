from dateutil.rrule import *

FREQUENCIES = {'YEARLY': YEARLY, 'MONTHLY': MONTHLY, 'WEEKLY': WEEKLY, 'DAILY': DAILY, 'HOURLY': HOURLY,
               'MINUTELY': MINUTELY, 'SECONDLY': SECONDLY}


def get_frequency(frequency_string: str):
    return FREQUENCIES[frequency_string.upper()] if frequency_string.upper() in FREQUENCIES else None


def get_byweekday(dow, occurrence):
    day_of_week_abbreviation = dow.upper()[0:2]
    if day_of_week_abbreviation == 'MO':
        weeday_obj = MO(occurrence)
    elif day_of_week_abbreviation == 'TU':
        weeday_obj = TU(occurrence)
    elif day_of_week_abbreviation == 'WE':
        weeday_obj = WE(occurrence)
    elif day_of_week_abbreviation == 'TH':
        weeday_obj = TH(occurrence)
    elif day_of_week_abbreviation == 'FR':
        weeday_obj = FR(occurrence)
    elif day_of_week_abbreviation == 'SA':
        weeday_obj = SA(occurrence)
    elif day_of_week_abbreviation == 'SU':
        weeday_obj = SU(occurrence)
    else:
        raise ValueError("Invalid day of week.")

    return weeday_obj


def interpret_general_rrule(frequency, by_month, by_weekday, first_day_of_year):
    holiday_date = rrule(frequency, dtstart=first_day_of_year, count=1, bymonth=by_month, byweekday=by_weekday)

    return holiday_date[0]


def interpret_easter_rrule(frequency, by_easter, first_day_of_year):
    holiday_date = rrule(frequency, dtstart=first_day_of_year, count=1, byeaster=by_easter)

    return holiday_date[0]
