"""
AgeCalc Module (Calculates birth information based on a specified DOB).
Displays:
    Age with 'age' function,
    Age in Months with 'age_months' function,
    Age in Years/Months with 'age_years_months' function,
    Day Of Birth with 'day_of_birth' function,
    Days Alive with 'days_alive' function,
    Days Since Last Birthday with 'last_birthday' function,
    Days Until Next Birthday with 'next_birthday' function.
"""

from datetime import datetime, date

__author__ = "Ali Raja"
__copyright__ = "Copyright 2013-2015, Ali Raja"
__credits__ = ["Ali Raja", "Ismail Ahmed", "Salim Abdala"]
__license__ = "GPL"
__version__ = "3.1"
__maintainer__ = "Ali Raja"
__email__ = "alir407@hotmail.co.uk"
__status__ = "Production"

__all__ = [  # CLASSES
             "AgeCalc",
             # FUNCTIONS
             "age", "age_months", "age_years_months", "day_of_birth",
             "days_alive", "last_birthday", "next_birthday"
             ]

now = datetime.now()


class Current:
    dd = now.day
    mm = now.month
    yy = now.year


class AgeCalc:
    """
    Stores DOB data into a class.
    You can then use the methods outlined above to get data from this.

    dd: Day
    mm: Month
    yy: Year

    Note: Dates should be passed as integers.
    If the Date/Month contains a "0" before the integer, the "0" should be
    omitted.
    E.G. DOB "01/02/2000" should be passed as:
        DD: 1
        MM: 2
        YY: 2000
    """

    def __init__(self, dd, mm, yy):
        self.dd = int(dd)
        self.mm = int(mm)
        self.yy = int(yy)

    @property
    def age(self):
        ag = Current.yy - self.yy
        if self.mm > Current.mm:
            ag -= 1
        elif self.mm < Current.mm:
            pass
        else:
            if self.dd < Current.dd:
                pass
            elif self.dd > Current.dd:
                ag -= 1
            else:
                pass
        return ag

    @property
    def age_months(self):
        am = Current.yy - self.yy
        am *= 12
        am += Current.mm - self.mm
        return am

    @property
    def age_years_months(self):
        ag = age(self.dd, self.mm, self.yy)
        months = age_months(self.dd, self.mm, self.yy)
        months -= (ag * 12)
        return {
            "years": ag,
            "months": months
        }

    @property
    def day_of_birth(self):
        db = date(self.yy, self.mm, self.dd)
        db = db.strftime("%A")
        return db

    @property
    def days_alive(self):
        da = datetime.now()
        da -= datetime(self.yy, self.mm, self.dd)
        da = da.days
        return da

    @property
    def last_birthday(self):
        dlb = datetime.now()
        dlb -= datetime(Current.yy, self.mm, self.dd)
        dlb = dlb.days
        if str(dlb)[0] == "-":
            dlb = datetime.now()
            dlb -= datetime(Current.yy - 1, self.mm, self.dd)
            dlb = dlb.days
        return dlb

    @property
    def next_birthday(self):
        dnb = datetime(Current.yy, self.mm, self.dd)
        dnb -= datetime.now()
        dnb = dnb.days + 1
        if str(dnb)[0] == "-":
            dnb = datetime(Current.yy + 1, self.mm, self.dd)
            dnb -= datetime.now()
            dnb = dnb.days + 1
        return dnb


def display_all(dd, mm, yy):
    """
    Returns all calculations, in a dictionary.
    See AgeCalc description for details.
    """
    ac = AgeCalc(dd, mm, yy)
    return {
        "age": ac.age,
        "age_months": ac.age_months,
        "age_years_months": ac.age_years_months,
        "day_of_birth": ac.day_of_birth,
        "days_alive": ac.days_alive,
        "last_birthday": ac.last_birthday,
        "next_birthday": ac.next_birthday
    }


def age(dd, mm, yy):
    """
    Find age by inputting a date of birth.
    """
    return AgeCalc(dd, mm, yy).age


def age_months(dd, mm, yy):
    """
    Find age in months by inputting a date of birth.
    """
    return AgeCalc(dd, mm, yy).age_months


def age_years_months(dd, mm, yy):
    """
    Find age in years and months by inputting a date of birth.
    Returns a dictionary with 'months', 'years' keys, containing these values.
    """
    return AgeCalc(dd, mm, yy).age_years_months


def day_of_birth(dd, mm, yy):
    """
    Find day of birth by inputting a date of birth.
    """
    return AgeCalc(dd, mm, yy).day_of_birth


def days_alive(dd, mm, yy):
    """
    Find days alive by inputting a date of birth.
    """
    return AgeCalc(dd, mm, yy).days_alive


def last_birthday(dd, mm, yy):
    """
    Find days since last birthday by inputting a date of birth.
    """
    return AgeCalc(dd, mm, yy).last_birthday


def next_birthday(dd, mm, yy):
    """
    Find days until next birthday by inputting a date of birth.
    """
    return AgeCalc(dd, mm, yy).next_birthday
