from django.test import TestCase
from rest_framework.test import APIRequestFactory
from restapi.models import Department
from restapi.views import DepartmentList

# Create your tests here.

factory = APIRequestFactory()

class DepartmentTestCase(TestCase):

    def setUp(self):
        pass

    def test_department_creation(self):
        request = factory.post('/departments', {'name':'Parkour'}, format='json')



