from rest_framework import mixins, generics, viewsets, status
from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.response import Response
from rest_framework.authtoken import views as rest_framework_views
from rest_framework import permissions
from django.db import models

from django.contrib.auth.models import User
import datetime

#TODO: Sort and structure imports

from restapi.models import Member, SpecificDate, SupervisorProfile, Course, EventType, Payment, ExtraHours
from restapi.models import Attendance, Subscription, IDCard, Department, SupervisorPayment, WaitingDetails
from restapi.serializer import MemberSerializer, SpecificDateSerializer, IDCardSerializer, SubscriptionSerializer, AttendanceSerializer
from restapi.serializer import EventTypeSerializer, PaymentSerializer, CourseSerializer, SupervisorSerializer, DepartmentSerializer, UserSerializer
from restapi.serializer import SupervisorPaymentSerializer, WaitingDetailsSerializer, ExtraHoursSerializer
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

####----------------------------------------------


class SupervisorPaymentList(generics.ListCreateAPIView):
    queryset = SupervisorPayment.objects.all()
    serializer_class = SupervisorPaymentSerializer


class SupervisorPaymentDetail(generics.RetrieveAPIView):
    queryset = SupervisorPayment.objects.all()
    serializer_class = SupervisorPaymentSerializer

####----------------------------------------------


class WaitingDetailList(generics.ListCreateAPIView):
    queryset = WaitingDetails.objects.all()
    serializer_class = WaitingDetailsSerializer


class WaitingDetailSingle(generics.RetrieveUpdateDestroyAPIView):
    queryset = WaitingDetails.objects.all()
    serializer_class = WaitingDetailsSerializer

####----------------------------------------------


class ExtraHoursList(generics.ListCreateAPIView):
    queryset = ExtraHours.objects.all()
    serializer_class = ExtraHoursSerializer


class ExtraHoursDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = ExtraHours.objects.all()
    serializer_class = ExtraHoursSerializer

####-------------------------------------------------
# Special, functional views
####-------------------------------------------------

class CourseDatesList(APIView):

    def get(self, request, course_pk, format=None):

        dates = SpecificDate.objects.all().filter(course=course_pk)
        serializer = SpecificDateSerializer(dates, many=True)
        return Response(serializer.data)


class GetUserInfo(APIView):

    def get(self, request, username):

        user = User.objects.get(username=username)
        profile = user.supervisor_profile
        serializer = SupervisorSerializer(profile, many=False)
        return Response(serializer.data)


class UnsubscribeMember(APIView):
    """
    POST: Unsubscribe member by updating subscription based on member_id
    and course_id, since this is all the Frontend knows about the subscription as of now

    GET: Get active Subscription based on course and member, since these make a unique set among the active
    subscriptions
    """

    def post(self, request, member_pk, course_pk):

        subs = Subscription.objects.all().filter(member=member_pk, course=course_pk)
        for sub in subs:
            if sub.active:
                sub.end_date = datetime.date.today()
                sub.save()
                serializer = SubscriptionSerializer(sub)
                return Response(data=serializer.data, status=status.HTTP_200_OK)

        # Return Error message in the 'non_field_errors' field in this way so
        # that the error handling in Ionic works properly
        return Response(data={'non_field_errors' : ["No active Subscription for this course and member"]},
                        status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, member_pk, course_pk):

        active_sub = Subscription.objects.all().filter(member=member_pk).filter(course=course_pk)\
            .filter((models.Q(end_date__isnull = True) | models.Q(end_date__gte = datetime.date.today()))).get()


        if active_sub is None:
            return Response(data={'non_field_errors' : ["No active Subscription for this course and member"]},
            status=status.HTTP_400_BAD_REQUEST)

        serializer = SubscriptionSerializer(active_sub)
        return Response(data=serializer.data, status=status.HTTP_200_OK)





@api_view(['POST'])
@authentication_classes(())
@permission_classes(())
def auth_view(request, format=None):
    return rest_framework_views.obtain_auth_token