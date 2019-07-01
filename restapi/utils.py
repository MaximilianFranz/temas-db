from .models import SpecificDate
from datetime import timedelta, datetime, date


def course_date_helper(member, date_from, date_to):
    """
    Given a member object, this method searches for possible dates of subscribed courses in the range and creates
    them if necessary.

    :param member: member for which to check course dates
    :param date_from: start of the interval
    :param date_to:  end of the interval
    :return:
    """
    courses = []
    for sub in member.subscriptions.all():
        courses.append(sub.course)

    for course in courses:
        if not course.eventtype == 1:
            # No Free training
            dates = get_dates_of_weekdays_in_range(course.day_of_week, date_from, date_to)
            for date in dates:
                # Create Dates if they don't exist
                SpecificDate.objects.get_or_create(date=date, course=course)


def get_dates_of_weekdays_in_range(weekday, date_from, date_to):
    """
    Returns date objects of the dates that are on the given weekday within the given date range

    :param weekday:  int 0 - 6 for monday to sunday
    :param date_to: date
    :param date_from: date
    :return: list of dates, possibly empty
    """
    dates = []
    if date_from.weekday() == weekday:
        new_date = date_from
    elif date_from.weekday() < weekday:
        new_date = date_from + timedelta(days=(weekday - date_from.weekday()))
    else:
        new_date = date_from + timedelta(days=((weekday - date_from.weekday()) % 6) + 1)

    while new_date <= date_to:
        dates.append(new_date)
        new_date = new_date + timedelta(days=7)

    return dates


def get_next_date_from_weekday(weekday):
    """

    :param weekday: int 0 - 6 for monday through sunday
    :return: Next date on that weekday from today
    """

    today = date.today()

    if today.weekday() == weekday:
        return today
    if today.weekday() < weekday:
        return today + timedelta(days=(weekday - today.weekday()))
    else:
        return today + timedelta(days=((weekday - today.weekday()) % 6) + 1)

