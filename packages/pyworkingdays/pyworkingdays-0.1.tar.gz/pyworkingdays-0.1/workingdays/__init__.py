from datetime import timedelta
from math import copysign

def is_workingday(input_date):
    return input_date.isoweekday() < 6

def add(datestart, days):
    sign = lambda x: int(copysign(1, x))
    dateend = datestart
    while days:
        dateend = dateend + timedelta(days=sign(days))
        if is_workingday(dateend):
            days -= sign(days)
    return dateend

def diff(date1, date2):
    if date1 == date2:
        return 0
    if date1 > date2:
        min_date = date2
        max_date = date1
    else:
        min_date = date1
        max_date = date2
    diff = 0
    current_date = min_date
    while current_date != max_date:
        current_date = current_date + timedelta(days=1)
        if is_workingday(current_date):
            diff += 1
    return diff

def next(datestart):
    while True:
        datestart = datestart + timedelta(days=1)
        if is_workingday(datestart):
            break
    return datestart