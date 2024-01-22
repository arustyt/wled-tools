from datetime import datetime

DATE_FORMAT = '%Y-%m-%d'


def get_todays_date_str():
    return get_date_str(datetime.today())


def get_date_str(date_value):
    return date_value.strftime(DATE_FORMAT)


def parse_date_str(date_str):
    return datetime.strptime(date_str, DATE_FORMAT)


def calculate_day_of_year_and_week(evaluation_date: datetime, evaluation_month=None, evaluation_day=None):
    calc_date = calculate_date(evaluation_date, evaluation_day, evaluation_month)
    time_tuple = calc_date.timetuple()

    return time_tuple.tm_yday, time_tuple.tm_wday


def calculate_date(evaluation_date: datetime, evaluation_day, evaluation_month):
    evaluation_year = evaluation_date.year
    if evaluation_month is None:
        evaluation_month = evaluation_date.month
    if evaluation_day is None:
        evaluation_day = evaluation_date.day
    calc_date = datetime(evaluation_year, evaluation_month, evaluation_day)
    return calc_date



