from dateutil.relativedelta import *
from dateutil.easter import *
from dateutil.rrule import *
from dateutil.parser import *
from datetime import *

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

next_mardi_gras = next_easter + relativedelta(days=-40)
if next_mardi_gras < test_date:
    easter_after_next = easter(next_year)
    next_mardi_gras = easter_after_next + relativedelta(days=-40)

print("Next Mardi Gras is: %s" % next_mardi_gras)

