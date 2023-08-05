"""Utilities for the freckle_budgets app."""
import calendar


def get_workday_number(day):
    """
    For any given day, returns the workday number.

    Let's say January 1st is a Monday. The next Monday would be January 8th.
    Since weekends don't count as workdays, January 8th would not be the 8th
    workday but the 6th.

    """
    month = calendar.Calendar(0).itermonthdates(day.year, day.month)
    counter = 1
    for month_day in month:
        if not month_day.month == day.month:
            continue
        if month_day.isoweekday() in [6, 7]:
            continue
        if month_day.day == day.day:
            return counter
        counter += 1
