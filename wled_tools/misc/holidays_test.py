from datetime import *

from dateutil.easter import *
from dateutil.relativedelta import *
from dateutil.rrule import *

from wled_utils.rrule_utils import get_byweekday, get_frequency

test_date = date(2023, 3, 17)
this_year = test_date.year
this_month = test_date.month

print("If today were: %s" % test_date)

result = rrule(YEARLY, dtstart=test_date, bymonth=1, bymonthday=1)
next_year = result[0].year
year_after_next = result[1].year

print("This year is: %s" % this_year)
print("This month is: %s" % this_month)
print("Next year is: %s" % next_year)
print("Year after next is: %s" % year_after_next)

next_easter = easter(this_year)
if next_easter < test_date:  # Easter this year has passed
    next_easter = easter(next_year)

print("Next Easter is: %s" % next_easter)

next_mardi_gras = next_easter + relativedelta(days=-47)
if next_mardi_gras < test_date:
    easter_after_next = easter(next_year)
    next_mardi_gras = easter_after_next + relativedelta(days=-47)

print("Next Mardi Gras is: %s" % next_mardi_gras)

test_date = date(2023, 3, 17)
frequency_str = 'YEARLY'
month = 11
day_of_week = 'TH(4)'
by_easter = None

frequency = get_frequency(frequency_str)
weekday = get_byweekday(day_of_week)

result = rrule(frequency, dtstart=test_date, count=1, byeaster=by_easter, bymonth=month, byweekday=weekday)
print("Next Thanksgiving is: %s" % result[0])

test_date = date(2023, 10, 19)
frequency_str = 'yearly'
# month = None
# day_of_week = None
by_easter = 0

frequency = get_frequency(frequency_str)

result = rrule(frequency, dtstart=test_date, count=1, byeaster=by_easter)
print("Next Easter is: %s" % result[0])

by_easter = -47
result = rrule(frequency, dtstart=test_date, count=1, byeaster=by_easter)
easter_date = result[0]
print("Next Mardi Gras is: %s" % result[0])


start_date = date(2024, 1, 1)
end_date = date(2024, 12, 31)

frequency_str = 'WEEKLY'
month = None
day_of_week = 'MO'
by_easter = None

frequency = get_frequency(frequency_str)
weekday = get_byweekday(day_of_week)

result = list(rrule(WEEKLY, dtstart=start_date, until=end_date, byweekday=weekday))

for monday in result:
    print("MONDAY: {monday}".format(monday=monday))
