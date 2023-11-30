from datetime import datetime

DATE_FORMAT = '%Y-%m-%d'


def get_todays_date_str():
    return get_date_str(datetime.today())


def get_date_str(date_value):
    return date_value.strftime(DATE_FORMAT)


def parse_date_str(date_str):
    return datetime.strptime(date_str, DATE_FORMAT)
