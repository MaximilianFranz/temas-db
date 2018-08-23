"""
One file to contain extensive test data used in unit- and integration-tests

"""

supervisor_1_data = {
    'first_name': 'Max',
    'last_name': 'Mustermann',
    'address': 'Some Address of home',
    'birthday': '15-05-1996',
    'department': 1,
    'courses': [],
    'username': 'testuser',
    'email': 'mail@mail.com',
    'wage': 15,
    'banking_info': 'some bank',
    'password': 'testpassword',
}

course_1_data = {
    'name': 'Montags-Kurs',
    'day_of_week': 0,
    'supervisor': [1],
    'start_time': '15:00',
    'department': 1,
    'max_attendees': 15
}

# faulty because date is not a monday (course 1 is monday)
specificdate_1_data = {
    'date': '01-08-2018',
    'course': 1,
    'supervisor': [1],
}

# legitimate
specificdate_2_data = {
    'date': '30-07-2018',
    'course': 1,
}

specificdate_3_data = {
    'date': '13-08-2018',
    'course': 1,
}

# Subscription from the past
# length: 1 year = 12 months
subscription_1_data = {
    'course': 1,
    'member': 1,
    'start_date': '01-08-2017',
    'end_date': '01-08-2018',
    'value': 20
}

# active subscription
subscription_2_data = {
    'course': 1,
    'member': 1,
    'start_date': '02-08-2018',
    'value': 20
}

# active subscription conflicting with subscription_2
subscription_3_data = {
    'course': 1,
    'member': 1,
    'start_date': '20-08-2018',
    'value': 20
}

member_1_data = {
    'first_name': 'hans',
    'last_name': 'peter',
    'address': 'some address',
    'mail': 'test@mail.com',
    'phone': '192322',
    'birthday': '15-05-1996',
    'mailNotification': True,
}

member_2_data = {
    'first_name': 'hans',
    'last_name': 'jörg',
    'address': 'some other address',
    'mail': 'test@mail.de',
    'phone': '192322',
    'birthday': '15-05-1993',
    'mailNotification': True,
}

attendance_1_patch_data = {
    'status' : 2
}

payment_1_data = {
    'member' : 1,
    'course' : 1,
    'value' : 40
}