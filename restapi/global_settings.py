"""
Contains
 - global Settings for default values with explanations
 - Error messages used in Validation
 - ...

"""

import datetime

# ----------------------------------
# Validation Error Message
# ----------------------------------

SUBSCRIPTION_CONFLICT = 'Only one active subscription per Member and Course is allowed'

COURSE_FULL = 'Course is full, automatically put member on waiting list'

AUTO_ADD_WAITINGLIST_NOTE = 'Automatically added to the waiting list because course is full'

WRONG_PASSWORD = "Wrong password, use same password on edit to confirm"

DATE_NOT_ON_WEEKDAY = 'Date is not on the weekday of this course'

TOO_MANY_SUPERVISROS = 'Only one supervisor per Free-Training is allowed'

START_AFTER_END = 'Start Date cannot be after the End Date for a subscription'
START_AFTER_END_TIME = 'Start Time cannot be after the End Time'

# ----------------------------------
# Meaningful Default Model Variables
# ----------------------------------

# Cost for attending a course without subscription (i.e. free training)
DEFAULT_ATTENDANCE_COST = 3

DEFAULT_WAGE = 15
DEFAULT_SECONDARY_WAGE = 10

DEFAULT_START_TIME = datetime.time(16, 00, 00)
DEFAULT_END_TIME = datetime.time(17, 30, 00)
DEFAULT_TIME_IN_HOURS = 1.5

# ----------------------------------
# Choices
# ----------------------------------

DEPARTMENTS = ((0, 'Parkour'),
               (1, 'Tricking'),
               (2, 'BJJ'),
               (3, 'Hort'),
               (4, 'Misc.'),
               )

DAYS_OF_WEEK = ((0, 'Monday'),
                (1, 'Tuesday'),
                (2, 'Wednesday'),
                (3, 'Thursday'),
                (4, 'Friday'),
                (5, 'Saturday'),
                (6, 'Sunday')
                )

EVENT_TYPES = ((0, 'Course'),
               (1, 'Free Training'))

ATTENDANCE_STATUS = ((0, 'not specified'),
                     (1, 'excused'),
                     (2, 'attended'),
                     (3, 'not attended'))

# Valid Date input formats accepted by serializers
# Last two for month fields implicity set day to 1
DATE_INPUT_FORMATS = ['%Y-%m-%d',
                      '%d-%m-%Y',
                      '%d-%m-%Y %H:%M',
                      '%Y-%m', '%m-%Y']

