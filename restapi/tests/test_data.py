"""
One file to contain extensive test data used in unit- and integration-tests

"""

supervisor_1_data = {
    'first_name': 'Max',
    'last_name': 'Mustermann',
    'address': 'Some Address of home',
    'birthday': '15-05-1996',
    'department': 0,
    'courses': [],
    'username': 'testuser',
    'email': 'mail@mail.com',
    'wage': 15,
    'banking_info': 'some bank',
    'password': 'testpassword',
}

supervisor_2_data = {
    'first_name': 'Sarah',
    'last_name': 'Stadtrand',
    'address': 'Some Address of home',
    'birthday': '15-05-1994',
    'department': 0,
    'courses': [],
    'username': 'otheruser',
    'email': 'mail@mail.com',
    'wage': 15,
    'banking_info': 'some bank',
    'password': 'testpassword2',
}

course_1_data = {
    'name': 'Montags-Kurs',
    'day_of_week': 0,
    'supervisor': [1],
    'start_time': '15:00',
    'end_time': '17:30',
    'department': 0,
    'max_attendees': 15
}

# free training
course_2_data = {
    'name': 'Free Training',
    'eventtype': 1,
    'start_time': '18:00',
    'end_time': '22:00',
    'department': 0,
    'max_attendees': 100
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

# free training date
specificdate_4_data = {
    'date': '14-08-2018',
    'course': 2,
    'supervisor': [1]
}

# free training patch for 'too many supervisor'-error
specificdate_4_patch = {
    'supervisor': [1, 2],
    'course': 2
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

subscription_4_data = {
    'course': 2,
    'member': 2,
    'start_date': '20-07-2018',
    'value': 15
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

# free training attendance without sub
attendance_2_data = {
    'member' : 1,
    'date' : 2,
    'status' : 2
}

payment_1_data = {
    'member' : 1,
    'course' : 1,
    'value' : 40
}

excuse_data = {
    'member_id' : 1,
    'date_from' : "2018-08-01",
    'date_to' : "2018-08-07",
    'note' : "test"
}