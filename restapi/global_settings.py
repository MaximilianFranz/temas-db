"""
Contains
 - global Settings for default values with explanations
 - Error messages used in Validation
 - ...

"""

# ----------------------------------
# Validation Error Message
# ----------------------------------

SUBSCRIPTION_CONFLICT = 'Only one active subscription per Member and Course is allowed'

COURSE_FULL = 'Course is full, automatically put member on waiting list'

AUTO_ADD_WAITINGLIST_NOTE = 'Automatically added to the waiting list because course is full'

WRONG_PASSWORD = "Wrong password, use same password on edit to confirm"

DATE_NOT_ON_WEEKDAY = 'Date is not on the weekday of this course'

TOO_MANY_SUPERVISORS_FREE_TRAINING = 'Only one supervisor per Free-Training is allowed'