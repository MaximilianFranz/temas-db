from rest_framework import serializers
from rest_framework.validators import  UniqueForMonthValidator
from django.contrib.auth.models import User
from restapi.models import Member, IDCard, SpecificDate, SupervisorProfile, Attendance
from restapi.models import Department, EventType, Course, Subscription, Payment, SupervisorPayment
import collections
import datetime

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

    id_card = serializers.PrimaryKeyRelatedField(many=False, queryset=IDCard.objects.all(), required=False, allow_null=True)
    birthday = serializers.DateField(input_formats=settings.DATE_INPUT_FORMATS)

    class Meta:
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
                  'attended_dates',
                  'balance')


class IDCardSerializer(serializers.ModelSerializer):

    # These are required as the fields are reverse and cannot be made 'blank' in models.py
    member = MemberField(queryset=Member.objects.all(), allow_empty=True, allow_null=True)

    class Meta:
        model = IDCard
        fields = ('id', 'card_id', 'registered', 'member')


class AttendanceSerializer(serializers.ModelSerializer):

    member = MemberField(many=False, queryset=Member.objects.all())

    class Meta:
        model = Attendance
        fields = ('id', 'member', 'date', 'status', 'note')


class SpecificDateSerializer(serializers.ModelSerializer):

    attendees = serializers.SerializerMethodField()
    date = serializers.DateField(input_formats=settings.DATE_INPUT_FORMATS)

    course = serializers.PrimaryKeyRelatedField(queryset=Course.objects.all())
    supervisor = serializers.PrimaryKeyRelatedField(queryset=SupervisorProfile.objects.all(), many=True, required=False)

    class Meta:
        depth = 0
        model = SpecificDate

        # Add 'id' field to provide for automatic id generation and adressing
        fields = ('id',
                  'date',
                  'attendees',
                  'course',
                  'supervisor',
                  'start_time',
                  'end_time')

    def create(self, validated_data):
        """
        FEATURE: Overrides create to ensure the SpecificDate instance inherits its details from the related course if not
        specified differently. This applies to attendees, start- and end-times

        :param validated_data:
        :return: the full fledged instance of the SpecificDate model
        """
        if len(validated_data['supervisor']) == 0:
            validated_data['supervisor'] = validated_data['course'].supervisor.all()

        specific_date = super(SpecificDateSerializer, self).create(validated_data)

        return specific_date

    def get_attendees(self, obj):
        """
        Special serializer method field to ensure a SpecificDate always represents the attendees
        based on the active subscription to the related course

        :param obj: the currently serialized instance
        :return: the serialized data for the field attendees
        """
        for sub in obj.course.subscriptions.all():
            if sub.active:
                Attendance.objects.get_or_create(member=sub.member, date=obj)

        attendance_set = obj.attendance_set
        serializer = AttendanceSerializer(attendance_set, many=True)

        return serializer.data

    def validate(self, data):
        """
        Making sure only dates related to the course dates (i.e weekday of the course) can be created

        :param data:
        :return:
        """
        if data['date'].weekday() != data['course'].day_of_week:
            raise serializers.ValidationError('Date is not on the weekday of this course')


class SupervisorField(serializers.PrimaryKeyRelatedField):
    """
    Custom Field for Supervisor to allow nested representation and update by PK
    """

    def to_representation(self, value):
        pk = super(SupervisorField, self).to_representation(value)
        try:
            item = SupervisorProfile.objects.get(pk=pk)
            serializer = SupervisorSerializer(item)
            return serializer.data
        except SupervisorProfile.DoesNotExist:
            return None

    def get_choices(self, cutoff=None):
        queryset = self.get_queryset()
        if queryset is None:
            return {}

        return collections.OrderedDict([(item.id, str(item)) for item in queryset])


class SupervisorSerializer(serializers.ModelSerializer):

    # TODO: Make the CREATE call only accessible with admin permissions

    birthday = serializers.DateField(input_formats=settings.DATE_INPUT_FORMATS)
    # required user fields
    username = serializers.CharField(source='user.username')
    email = serializers.EmailField(source='user.email')
    password = serializers.CharField(source='user.password', write_only=True)

    class Meta:
        model = SupervisorProfile

        fields = ('id','first_name','last_name', 'address', 'birthday', 'department',
                  'courses', 'username', 'email', 'password')
        related_fields = ['user']

    def update(self, instance, validated_data):
        super(SupervisorSerializer, self).update(instance, validated_data)
        instance.user.set_password(validated_data.get('user',{}).get('password'))
        instance.user.email = validated_data.get('user', {}).get('email')
        instance.user.username = validated_data.get('user', {}).get('username')
        instance.save()

    def create(self, validated_data):
        kwargs = {'email' : validated_data['user'].pop('email'),
                  'username' : validated_data['user'].pop('username'),}
        user = User.objects.create(**kwargs)

        # Password must be hashed and ought not be stored raw, thus use .set_password
        user.set_password(validated_data['user'].pop('password'))
        user.save()
        validated_data['user'] = user

        supervisor = super(SupervisorSerializer, self).create(validated_data)
        return supervisor

class UserSerializer(serializers.ModelSerializer):

    """
    Custom User serializer to support all fields in supervisor profile natively
    """

    address = serializers.CharField(source='supervisor_profile.address')

    class Meta:
        model = User
        fields = ('id', 'password', 'first_name', 'last_name', 'email', 'address')
        write_only_fields = ('password',)
        read_only_fields = ('is_staff', 'is_superuser', 'is_active', 'date_joined',)


class DepartmentField(serializers.PrimaryKeyRelatedField):
    """
    Custom Field for Department to allow nested representation and update by PK
    """

    def to_representation(self, value):
        pk = super(DepartmentField, self).to_representation(value)
        try:
            item = Department.objects.get(pk=pk)
            serializer = DepartmentSerializer(item)
            return serializer.data
        except Department.DoesNotExist:
            return None

    def get_choices(self, cutoff=None):
        queryset = self.get_queryset()
        if queryset is None:
            return {}

        return collections.OrderedDict([(item.id, str(item)) for item in queryset])


class DepartmentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Department
        fields = ('id', 'name', 'courses', 'supervisors')


class EventTypeSerializer(serializers.ModelSerializer):

    class Meta:
        model = EventType
        fields = ('id', 'name', 'has_prio', 'has_payment', 'has_subscription', 'courses')


class CourseSerializer(serializers.ModelSerializer):

    supervisor = SupervisorField(queryset=SupervisorProfile.objects.all(), many=True)
    department = DepartmentField(queryset=Department.objects.all())

    # Lists full fledge member serialization of all members ignoring the subscription 'through-model'
    # For low-prio mode courses there is no subcription and thus no members to be listed.
    members = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Course
        fields = ('id','name', 'day_of_week', 'supervisor', 'department', 'members', 'eventtype', 'start_time', 'end_time' )

    def get_members(self, obj):
        """

        Returns current members of this course by querying active subscriptions and returning the related members
        :param obj: the instance of this Course model
        :return: serialized data for the field members

        """
        subscriptions = Subscription.objects.filter(course=obj.pk)
        active_subscriptions = [sub for sub in subscriptions if sub.active] # filter out passive subscriptions
        members = Member.objects.filter(subscriptions__in=active_subscriptions)
        serializer = MemberSerializer(members, many=True)
        return serializer.data


class SubscriptionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Subscription
        fields = ('course', 'member', 'start_date', 'end_date',
                  'value', 'accumulated_value', 'length', 'active')



class PaymentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Payment
        fields = ('id', 'member', 'course', 'date', 'value')

class SupervisorPaymentSerializer(serializers.ModelSerializer):

    supervisor = SupervisorField(queryset=SupervisorProfile.objects.all())

    class Meta:
        model = SupervisorPayment
        fields = ('id', 'supervisor', 'date', 'value', 'note')