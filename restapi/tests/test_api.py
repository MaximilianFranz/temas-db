from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User

from rest_framework import status
from rest_framework.test import APIRequestFactory, APITestCase
from restapi.models import *
from . import test_data as td
from .. import global_settings as gs
from freezegun import freeze_time

# Create your tests here.
# For each function within an APITestCase the database is 'restarted' empty
# Thus if you want to build on models created through other requests you need to put them in one function


# class DepartmentTestCase(APITestCase):
#
#     def setUp(self):
#
#         # Logs in a user in order to access authenticated_only views
#         user = User.objects.create_user('username', 'Pas$w0rd')
#         self.client.force_login(user=user)
#
#     def test_department_endpoint(self):
#
#         # test POST
#         url = reverse('department-list')
#         data = {'name':'Parkour', 'courses':[], 'supervisors':[]}
#         response = self.client.post(url, data, format='json')
#         self.assertEqual(response.status_code, status.HTTP_201_CREATED)
#         self.assertEqual(Department.objects.filter(name='Parkour').count(), 1)
#
#         # test GET
#         response = self.client.get(url)
#         self.assertEqual(response.data[0]['name'], 'Parkour')
#         self.assertEqual(response.data[0]['id'], 1)
#
#         # test DELETE
#         url = reverse('department-detail', kwargs={'pk': 1})
#         response = self.client.delete(url)
#         self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)


class SupervisorTestCase(APITestCase):

    data = td.supervisor_1_data

    def setUp(self):
        pass

    def test_supervisor_endpoint(self):

        # test POST
        url = reverse('supervisor-list')
        response = self.client.post(url, self.data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # test GET
        url = reverse('supervisor-list')
        response = self.client.get(url)
        self.assertTrue(len(response.data) > 0)
        self.assertEqual(response.data[0]['email'], 'mail@mail.com')

        # test PUT
        url = reverse('supervisor-detail', kwargs={'pk': 1})
        self.data['last_name'] += " extended"
        response = self.client.put(url, data=self.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # test DELETE
        url = reverse('supervisor-detail', kwargs={'pk': 1})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)


class CourseTestCase(APITestCase):

    def setUp(self):
        pass

        setup_url = reverse('supervisor-list')
        response = self.client.post(setup_url, data=td.supervisor_1_data)

    def test_course_endpoint(self):

        #test POST
        url = reverse('course-list')
        response = self.client.post(url, data=td.course_1_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        #test GET
        response = self.client.get(url)
        self.assertEqual(response.data[0]['name'], 'Montags-Kurs')
        self.assertEqual(response.data[0]['number_of_participants'], 0)
        # setting explicit works
        self.assertEqual(response.data[0]['start_time'], '15:00:00')
        # default was used
        self.assertEqual(response.data[0]['end_time'], '17:30:00')


class MemberTestCase(APITestCase):
    """
    Tests:
    1. Simple generation and query of calculated properties:
        -
    """

    def setUp(self):
        pass

    def test_member_endpoint(self):

        url = reverse('member-list')
        response = self.client.post(url, data=td.member_1_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # initial balance is 0
        self.assertEqual(response.data['balance'], 0)
        self.assertEqual(response.data['percentage_attended'], 0)
        self.assertEqual(response.data['first_name'], 'hans')


class SubscriptionTestCase(APITestCase):
    """
    Tests:
    1. Simple generation and query of calculated properties:
        - accumulated value
        - length
    2. Uniqueness on (Member, Course) in active subscriptions
    """

    def setUp(self):
        setup_url = reverse('member-list')
        self.client.post(setup_url, data=td.member_1_data)
        setup_url = reverse('supervisor-list')
        response = self.client.post(setup_url, data=td.supervisor_1_data)
        setup_url = reverse('course-list')
        self.client.post(setup_url, data=td.course_1_data)

    def test_subscription_endpoint(self):

        url = reverse('subscription-list')
        # passive / old subscription
        response = self.client.post(url, data=td.subscription_1_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['length'], 12)
        self.assertEqual(response.data['accumulated_value'], 12*20)
        self.assertEqual(response.data['active'], False)

        # active subscription
        response = self.client.post(url, data=td.subscription_2_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['length'], 'unlimited')
        self.assertEqual(response.data['active'], True)

        # Uniqueness conflict
        response = self.client.post(url, data=td.subscription_3_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['non_field_errors'], [gs.SUBSCRIPTION_CONFLICT])



class SpecificDateTestCase(APITestCase):
    """
    Tests:
    1. Auto attendance generation based on subscription to course
    2. Auto-fill of start / end time and supervisors based on course
    3. Calculated Properties:
        - percentage_attended

    4. Error when date is not on the day of the course
    """

    def setUp(self):
        setup_url = reverse('member-list')
        self.client.post(setup_url, data=td.member_1_data)
        setup_url = reverse('supervisor-list')
        self.client.post(setup_url, data=td.supervisor_1_data)
        setup_url = reverse('course-list')
        self.client.post(setup_url, data=td.course_1_data)
        setup_url = reverse('subscription-list')
        # use active subscription
        self.client.post(setup_url, data=td.subscription_2_data)

    def test_specificdate_endpoint(self):


        url = reverse('specificdate-list')
        # Wrong weekday
        response = self.client.post(url, data=td.specificdate_1_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['non_field_errors'], [gs.DATE_NOT_ON_WEEKDAY])

        # Auto fill start and end time, auto-generate attendance, supervisor from course
        response = self.client.post(url, data=td.specificdate_3_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['start_time'], '15:00:00')
        self.assertEqual(response.data['attendees'][0]['member']['first_name'], td.member_1_data['first_name'])
        self.assertEqual(response.data['supervisor'], [1])
        self.assertEqual(response.data['attendees'][0]['member']['percentage_attended'], 0)

        # Change auto_generated attendance to 'attended' = 2
        url = reverse('attendance-detail', kwargs={'pk' : 1})
        response = self.client.patch(url, td.attendance_1_patch_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # updated percentage_attended should be 1
        self.assertEqual(response.data['member']['percentage_attended'], 1.0)


class AdvancedTestCase(APITestCase):
    """
    Tests:
    1. Balance Calculation on Member
    2. Balance calc on Course
    3. Max participants
    """

    def setUp(self):
        setup_url = reverse('member-list')
        self.client.post(setup_url, data=td.member_1_data)
        setup_url = reverse('supervisor-list')
        self.client.post(setup_url, data=td.supervisor_1_data)
        self.client.post(setup_url, data=td.supervisor_2_data)
        setup_url = reverse('course-list')
        self.client.post(setup_url, data=td.course_1_data)
        setup_url = reverse('subscription-list')
        # use active subscription
        self.client.post(setup_url, data=td.subscription_2_data)

    @freeze_time("2018-08-22")
    def test_advanced_cases(self):
        """
        Uses freeze_time to fix the current datetime to a certain point in order to allow
        consistent testing, as calculation of balance, etc. is dependent on the current date
        :return:
        """

        # Add passive old subscription to generate negative balance
        setup_url = reverse('subscription-list')
        resp = self.client.post(setup_url, data=td.subscription_1_data)
        url = reverse('member-detail', kwargs={'pk': 1})
        response = self.client.get(url)
        self.assertEqual(response.data['balance'], -240) # one year worth of 20€ / month

        url = reverse('specificdate-list')
        # Generate SpecificDate to adjust course balance
        self.client.post(url, data=td.specificdate_3_data)

        # Check effect on Course
        url = reverse('course-detail', kwargs={'pk': 1})
        response = self.client.get(url)
        self.assertEqual(response.data['balance'], -2.5*15) # 2.5h course at 15€/h

        # Check effect on SupervisorProfile
        url = reverse('supervisor-detail', kwargs={'pk': 1})
        response = self.client.get(url)
        self.assertEqual(response.data['amount_due'], 2.5*15) # 2.5h course at 15€/h


        # Generate 15 members and subscribe them with active subscription to course_1 in order to reach
        # maximumum participant limit and yield error
        setup_url = reverse('member-list')
        # be sure to copy dicts to maintain data integrity in test_data.py, because tests don't run chronologically
        member_data = td.member_2_data.copy()
        sub_data = td.subscription_2_data.copy()
        # One active subscription is there, generate 17 - 2 = 15 more to surpass the limit
        for i in range(2, 17):
            member_data['first_name'] += 'l'
            self.client.post(setup_url, data=member_data)
            sub_data['member'] = i
            url = reverse('subscription-list')
            response = self.client.post(url, data=sub_data)
            if i >= 16:
                self.assertEqual(response.data['non_field_errors'], [gs.COURSE_FULL])

        url = reverse('subscription-list')
        response = self.client.get(url)
        self.assertEqual(len(response.data), 16) # 15 active + 1 passive

        # participants are capped at 15
        url = reverse('course-detail', kwargs={'pk' : 1})
        response = self.client.get(url)
        self.assertEqual(response.data['number_of_participants'], 15)

        # waiting list entry has been created automatically
        url = reverse('waiting_details-list')
        response = self.client.get(url)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['course'], 1)

        # Add Payment
        url = reverse('payment-list')
        response = self.client.post(url, data=td.payment_1_data)

        # Check changes on course
        url = reverse('course-detail', kwargs={'pk' : 1})
        response = self.client.get(url)
        self.assertEqual(response.data['total_money_earned'], td.payment_1_data['value'])
        self.assertEqual(response.data['balance'], 2.5)


        """
        Create Free Training and attendance to test features

         1. Attendance without subscription is considered in balance calculation of member
         2. Free Training is considered with secondary_wage for amount_due of supervisor

         3. Attendance is NOT automatically generated even if subscription exists.
         4. No two supervisors are allowed for free-training

        """

        # Generate free training course + date + attendance
        url = reverse('course-list')
        response = self.client.post(url, td.course_2_data)
        url = reverse('subscription-list')
        response = self.client.post(url, td.subscription_4_data)
        url = reverse('specificdate-list')
        response = self.client.post(url, td.specificdate_4_data)

        # Implicit: No day_of_week check is performed (i.e. no error thrown because of wrong date)
        # No Attendance is automatically generated
        self.assertEqual(response.data['attendees'], [])

        url = reverse('attendance-list')
        response = self.client.post(url, td.attendance_2_data)

        # test that free training is considered in balance of member
        url = reverse('member-detail', kwargs={'pk': 1})
        response = self.client.get(url)
        self.assertEqual(response.data['balance'], -203) # -200 - 3 for free Training attendance without sub

        # test that free training is considered in amount_due of supervisor
        url = reverse('supervisor-detail', kwargs={'pk': 1})
        response = self.client.get(url)
        self.assertEqual(response.data['amount_due'], 2.5 * 15 + 4*10) #2,5 h course at 15€ and 4h at 10€

        # Too many supervisors results in error message
        url = reverse('specificdate-detail', kwargs={'pk': 2})
        response = self.client.patch(url, td.specificdate_4_patch)
        self.assertEqual(response.data['non_field_errors'], [gs.TOO_MANY_SUPERVISROS])



