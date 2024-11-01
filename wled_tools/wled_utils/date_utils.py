from datetime import datetime

from wled_constants import NAME_KEY, ABBREVIATION_KEY, INDEX_KEY
from wled_utils.rrule_utils import YEARLY_STR, MONTHLY_STR, DAILY_STR

DATE_FORMAT = '%Y-%m-%d'

DAYS_OF_THE_WEEK = [{INDEX_KEY: 0, NAME_KEY: 'Monday', ABBREVIATION_KEY: 'mon'},
                    {INDEX_KEY: 1, NAME_KEY: 'Tuesday', ABBREVIATION_KEY: 'tue'},
                    {INDEX_KEY: 2, NAME_KEY: 'Wednesday', ABBREVIATION_KEY: 'wed'},
                    {INDEX_KEY: 3, NAME_KEY: 'Thursday', ABBREVIATION_KEY: 'thu'},
                    {INDEX_KEY: 4, NAME_KEY: 'Friday', ABBREVIATION_KEY: 'fri'},
                    {INDEX_KEY: 5, NAME_KEY: 'Saturday', ABBREVIATION_KEY: 'sat'},
                    {INDEX_KEY: 6, NAME_KEY: 'Sunday', ABBREVIATION_KEY: 'sun'}]


def get_todays_date_str():
    return get_date_str(datetime.today())


def get_date_str(date_value):
    return date_value.strftime(DATE_FORMAT)


def parse_date_str(date_str):
    return datetime.strptime(date_str, DATE_FORMAT)


def calculate_day_of_year_and_week(evaluation_date: datetime, evaluation_month=None, evaluation_day=None):
    calc_date = calculate_date(evaluation_date, evaluation_day, evaluation_month)
    time_tuple = calc_date.timetuple()

    return time_tuple.tm_yday, DAYS_OF_THE_WEEK[time_tuple.tm_wday]


def calculate_date(evaluation_date: datetime, frequency_str, interval=1, mod=0, evaluation_day=None, evaluation_month=None):
    if interval is None or interval == 1:
        return calculate_simple_date(evaluation_date, evaluation_day, evaluation_month)
    else:
        return calculate_interval_based_date(evaluation_date, frequency_str, interval, mod, evaluation_day, evaluation_month)


def calculate_simple_date(evaluation_date: datetime, evaluation_day, evaluation_month):
    evaluation_year = evaluation_date.year
    if evaluation_month is None:
        evaluation_month = evaluation_date.month
    if evaluation_day is None:
        evaluation_day = evaluation_date.day
    calc_date = datetime(evaluation_year, evaluation_month, evaluation_day)
    return calc_date


def calculate_interval_based_date(evaluation_date, frequency_str, interval, mod, evaluation_day, evaluation_month):
    evaluation_year = evaluation_date.year
    if frequency_str == YEARLY_STR:
        while evaluation_year % interval != mod:
            evaluation_year += 1
    if evaluation_month is None:
        evaluation_month = evaluation_date.month
    if frequency_str == MONTHLY_STR:
        while evaluation_month % interval != mod:
            evaluation_month += 1
    if evaluation_day is None:
        evaluation_day = evaluation_date.day
    if frequency_str == DAILY_STR:
        while evaluation_day % interval != mod:
            evaluation_day += 1
    calc_date = datetime(evaluation_year, evaluation_month, evaluation_day)
    return calc_date
