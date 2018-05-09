from rest_framework import serializers
from django.contrib.auth.models import User
from restapi.models import Member, IDCard, SpecificDate, Supervisor, Attendance
from restapi.models import Department, EventType, Course, Subscription, Payment

import collections

# import settings for global constants
from temas_db import settings



# TODO: Make automatically created fields like 'created' or 'registered' to read_only


class MemberField(serializers.PrimaryKeyRelatedField):
    """
    Custom Field for Member in SpecificDate to allow nested representation and update by PK
    """
    def to_representation(self, value):
        pk = super(MemberField, self).to_representation(value)
        try:
            item = Member.objects.get(pk=pk)
            serializer = MemberSerializer(item)
            return serializer.data
        except Member.DoesNotExist:
            return None

    def get_choices(self, cutoff=None):
        queryset = self.get_queryset()
        if queryset is None:
            return {}

        return collections.OrderedDict([(item.id, str(item)) for item in queryset])

class MemberSerializer(serializers.ModelSerializer):


    id_card = serializers.PrimaryKeyRelatedField(many=False, queryset=IDCard.objects.all())
    birthday = serializers.DateField(input_formats=settings.DATE_INPUT_FORMATS)

    #attended_dates = serializers.PrimaryKeyRelatedField(source=SpecificDate, queryset=SpecificDate.objects.all())

    class Meta:
        depth = 2
        model = Member
        # Add id field to provide for automatic id generation an adressing
        fields = ('id',
                  'created',
                  'first_name',
                  'last_name',
                  'address',
                  'mail',
                  'phone',
                  'birthday',
                  'mailNotification',
                  'id_card',
                  'attended_dates',)


class IDCardSerializer(serializers.ModelSerializer):

    # These are required as the fields are reverse and cannot be made 'blank' in models.py
    member = MemberField(queryset=Supervisor.objects.all(), allow_empty=True, allow_null=True)
    supervisor = serializers.PrimaryKeyRelatedField(queryset=Supervisor.objects.all(), allow_empty=True, allow_null=True)

    class Meta:
        model = IDCard
        fields = ('id', 'card_id', 'registered', 'member', 'supervisor')


class SpecificDateSerializer(serializers.ModelSerializer):

    #TODO: Replace MemberField with something that automatically creates the transitionary class
    # 'Attendance' from given primary keys of members --> How to handle the status?
    attendees = MemberField(queryset=Member.objects.all(), many=True)
    course = serializers.PrimaryKeyRelatedField(queryset=Course.objects.all())
    supervisor = serializers.PrimaryKeyRelatedField(queryset=Supervisor.objects.all(), many=True)

    class Meta:
        depth = 2
        model = SpecificDate

        # Add 'id' field to provide for automatic id generation and adressing
        fields = ('id',
                  'date',
                  'attendees',
                  'course',
                  'supervisor')



class SupervisorSerializer(serializers.ModelSerializer):

    birthday = serializers.DateField(input_formats=settings.DATE_INPUT_FORMATS)

    class Meta:
        model = Supervisor

        fields = ('id', 'first_name', 'last_name', 'address', 'birthday', 'department', 'courses', 'id_card')

    # TODO: Overwrite validate to make sure ID-Card only has either on Member or one Supervisor assigned (bad solution)

class DepartmentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Department
        fields = ('id', 'name', 'courses', 'supervisors')


class EventTypeSerializer(serializers.ModelSerializer):

    class Meta:
        model = EventType
        fields = ('id', 'name', 'has_prio', 'has_payment', 'has_subscription')


class CourseSerializer(serializers.ModelSerializer):

    supervisor = serializers.PrimaryKeyRelatedField(queryset=Supervisor.objects.all(), allow_empty=True, allow_null=True)
    department = serializers.PrimaryKeyRelatedField(queryset=Department.objects.all(), allow_empty=True, allow_null=True)

    class Meta:
        model = Course
        fields = ('name', 'day_of_week', 'supervisor', 'department')


class SubscriptionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Subscription
        fields = ('member', 'course', 'month', 'value')


class PaymentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Payment
        fields = ('member', 'course', 'date', 'value')

class AttendanceSerializer(serializers.ModelSerializer):

    class Meta:
        model = Attendance
        fields = ('member', 'date', 'status', 'note')
