from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User

from rest_framework import status
from rest_framework.test import APIRequestFactory, APITestCase
from restapi.models import Department, IDCard, SupervisorProfile
from restapi.views import DepartmentList

# Create your tests here.
# For each function within an APITestCase the database is 'restarted' empty
# Thus if you want to build on models created through other requests you need to put them in one function

class DepartmentTestCase(APITestCase):

    def setUp(self):

        # Logs in a user in order to access authenticated_only views
        user = User.objects.create_user('username', 'Pas$w0rd')
        self.client.force_login(user=user)

    def test_department_endpoint(self):

        # test POST
        url = reverse('department-list')
        data = {'name':'Parkour', 'courses':[], 'supervisors':[]}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Department.objects.filter(name='Parkour').count(), 1)

        # test GET
        response = self.client.get(url)
        self.assertEqual(response.data[0]['name'], 'Parkour')
        self.assertEqual(response.data[0]['id'], 1)

        # test DELETE
        url = reverse('department-detail', kwargs={'pk': 1})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)


class SupervisorTestCase(APITestCase):

    data = {'first_name': 'Max',
            'last_name': 'Mustermann',
            'address': 'Some Address of home',
            'birthday': '15-05-1996',
            'department': 1,
            'id_card': 1,
            'courses': []
            }

    def setUp(self):
        d = Department(name='TestDepartment')
        d.save()

        id = IDCard(card_id="2244")
        id.save()

    def test_supervisor_endpoint(self):

        # test POST
        url = reverse('supervisor-list')
        response = self.client.post(url, self.data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # test GET
        url = reverse('supervisor-list')
        response = self.client.get(url)
        self.assertTrue(len(response.data) > 0)
        self.assertEqual(response.data[0]['id_card'], 1)

        url = reverse('idcard-detail', kwargs={'pk': 1})
        response = self.client.get(url)

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

    course_arg = {
        'name': 'Montags-Kurs',
        'day_of_week': 'MON',
        'supervisor': 1,
        'department': 1
    }

    def setUp(self):
        d = Department(name='TestDepartment')
        d.save()

        id = IDCard(card_id="2244")
        id.save()

        supervisor_args = {
            'first_name': 'Max',
            'last_name': 'Mustermann',
            'address': 'Some Address of home',
            'birthday': '15-05-1996',
            'department': 1,
            'id_card': 1,
            'courses': []
            }

        setup_url = reverse('supervisor-list')
        response = self.client.post(setup_url, data=supervisor_args)

    def test_course_endpoint(self):

        #test POST
        url = reverse('course-list')
        response = self.client.post(url, data=self.course_arg)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        #test GET
        response = self.client.get(url)
        self.assertEqual(response.data[0]['name'], 'Montags-Kurs')
