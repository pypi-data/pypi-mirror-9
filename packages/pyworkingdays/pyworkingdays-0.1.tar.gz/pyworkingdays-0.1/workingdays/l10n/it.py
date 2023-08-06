from datetime import date, timedelta
from dateutil.easter import *

_holidays_cache = {}

def _get_holidays(year):
    # return holidays in italy for a given year
    return [
        # Capodanno (1st of january);
        date(year, 1, 1),
        #Epifania (6th of january);
        date(year, 1, 6),
        #Pasqua (easter, always sunday);
        #Lunedi' dell'Angelo, o Pasquetta (monday after easter);
        easter(year) + timedelta(days=1),
        #Festa della Liberazione (25th of april);
        date(year, 4, 25),
        #Festa dei lavoratori (1st of may);
        date(year, 5, 1),
        #Pentecoste (50 days after easter, always sunday);
        #Festa della Repubblica (2nd of june);
        date(year, 6, 2),
        #Assunzione di Maria Vergine o Ferragosto (15th of august);
        date(year, 8, 15),
        #Tutti i santi (1st of november);
        date(year, 11, 1),
        #Immacolata Concezione (8th of december);
        date(year, 12, 8),
        #Natale (25th of december);
        date(year, 12, 25),
        #Santo Stefano (26th of december).
        date(year, 12, 26),
    ]

def is_workingday(input_date):
    if input_date.isoweekday() > 5:
        return False
    year = input_date.year
    holidays = _holidays_cache.setdefault(year, _get_holidays(year))
    return input_date not in holidays
