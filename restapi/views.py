from rest_framework import mixins, generics

#TODO: Sort and structure imports

from restapi.models import Member, SpecificDate, Supervisor, Course, EventType, Payment, Subscription, IDCard, Department
from restapi.serializer import MemberSerializer, SpecificDateSerializer, IDCardSerializer, SubscriptionSerializer
from restapi.serializer import EventTypeSerializer, PaymentSerializer, CourseSerializer, SupervisorSerializer, DepartmentSerializer

# Create your views here.


class MemberList(generics.ListCreateAPIView):

    """
    List all members, or create a new member.
    """

    queryset = Member.objects.all()
    serializer_class = MemberSerializer




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

    queryset = Supervisor.objects.all()
    serializer_class = SupervisorSerializer


class SupervisorDetail(generics.RetrieveUpdateDestroyAPIView):

    queryset = Supervisor.objects.all()
    serializer_class = SupervisorSerializer


####----------------------------------------------

class DepartmentList(generics.ListCreateAPIView):

    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer


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


class IDCardDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = IDCard.objects.all()
    serializer_class = IDCardSerializer