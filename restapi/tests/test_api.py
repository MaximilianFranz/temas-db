from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIRequestFactory, APITestCase
from restapi.models import Department
from restapi.views import DepartmentList

# Create your tests here.


class DepartmentTestCase(APITestCase):

    def setUp(self):
        pass

    def test_department_creation(self):
        url = reverse('department-list')
        print('reversed url: ' + url)
        data = {'name':'Parkour', 'course':[], 'supervisor':[]}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Department.objects.filter(name='Parkour').count(), 1)

