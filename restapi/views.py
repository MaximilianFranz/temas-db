from rest_framework import mixins, generics, viewsets
from rest_framework import permissions

from django.contrib.auth.models import User

#TODO: Sort and structure imports

from restapi.models import Member, SpecificDate, SupervisorProfile, Course, EventType, Payment
from restapi.models import Attendance, Subscription, IDCard, Department
from restapi.serializer import MemberSerializer, SpecificDateSerializer, IDCardSerializer, SubscriptionSerializer, AttendanceSerializer
from restapi.serializer import EventTypeSerializer, PaymentSerializer, CourseSerializer, SupervisorSerializer, DepartmentSerializer, UserSerializer

# Create your views here.


class MemberList(generics.ListCreateAPIView):

    """
    List all members, or create a new member.
    """

    queryset = Member.objects.all()
    serializer_class = MemberSerializer


# TODO: Bundle Views into ViewSets where applicable

class MemberDetail(generics.RetrieveUpdateDestroyAPIView):

    queryset = Member.objects.all()
    serializer_class = MemberSerializer



class SpecificDateList(generics.ListCreateAPIView):

    queryset = SpecificDate.objects.all()
    serializer_class = SpecificDateSerializer


class SpecificDateDetail(generics.RetrieveUpdateDestroyAPIView):

    queryset = SpecificDate.objects.all()
    serializer_class = SpecificDateSerializer

####----------------------------------------------

class SupervisorList(generics.ListCreateAPIView):

    queryset = SupervisorProfile.objects.all()
    serializer_class = SupervisorSerializer


class SupervisorDetail(generics.RetrieveUpdateDestroyAPIView):

    queryset = SupervisorProfile.objects.all()
    serializer_class = SupervisorSerializer


class UserList(generics.ListCreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class UserDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

####----------------------------------------------

class DepartmentList(generics.ListCreateAPIView):

    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer

    permission_classes = [permissions.IsAuthenticated]


class DepartmentDetail(generics.RetrieveUpdateDestroyAPIView):

    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer


####----------------------------------------------

class CourseList(generics.ListCreateAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer


class CourseDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer


####----------------------------------------------

class EventTypeList(generics.ListCreateAPIView):
    queryset = EventType.objects.all()
    serializer_class = EventTypeSerializer


class EventTypeDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = EventType.objects.all()
    serializer_class = EventTypeSerializer

####----------------------------------------------

class PaymentList(generics.ListCreateAPIView):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer


class PaymentDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer

####----------------------------------------------

class SubscriptionList(generics.ListCreateAPIView):
    queryset = Subscription.objects.all()
    serializer_class = SubscriptionSerializer


class SubscriptionDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Subscription.objects.all()
    serializer_class = SubscriptionSerializer

####----------------------------------------------

class IDCardList(generics.ListCreateAPIView):
    queryset = IDCard.objects.all()
    serializer_class = IDCardSerializer

    def perform_create(self, serializer):
        print('got here')
        serializer.save(member=None, supervisor=None)

class IDCardDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = IDCard.objects.all()
    serializer_class = IDCardSerializer


####----------------------------------------------

class AttendanceList(generics.ListCreateAPIView):
    queryset = Attendance.objects.all()
    serializer_class = AttendanceSerializer


class AttendanceDetails(generics.RetrieveUpdateDestroyAPIView):
    queryset = Attendance.objects.all()
    serializer_class = AttendanceSerializer