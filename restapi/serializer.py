from rest_framework import serializers
from rest_framework.validators import  UniqueForMonthValidator
from django.contrib.auth.models import User
from restapi.models import Member, IDCard, SpecificDate, SupervisorProfile, Attendance, WaitingDetails
from restapi.models import Course, Subscription, Payment, SupervisorPayment, ExtraHours
import collections
from django.db import models
import datetime

# import settings for global constants
from temas_db import settings
from restapi import global_settings as gs

# ----------------------------------
# Custom Fields
# ----------------------------------

class MemberField(serializers.PrimaryKeyRelatedField):
    """
    Custom Field for Member in SpecificDate to allow nested
    representation while still allowing update by PK
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


# ----------------------------------
# Custom Serializers
# ----------------------------------

class SupervisorField(serializers.PrimaryKeyRelatedField):
    """
    Custom Field for Member in SpecificDate to allow nested
    representation while still allowing update by PK
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


class MemberSerializer(serializers.ModelSerializer):

    birthday = serializers.DateField(input_formats=settings.DATE_INPUT_FORMATS)

    class Meta:
        model = Member
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
                  # FK related fields
                  'attended_dates',
                  # property vields
                  'balance',
                  'percentage_attended',
                  'last_payment_date',
                  'attended_last_4_dates')


class SpecificDateSerializer(serializers.ModelSerializer):

    attendees = serializers.SerializerMethodField()
    date = serializers.DateField(input_formats=settings.DATE_INPUT_FORMATS)

    class Meta:
        model = SpecificDate

        fields = ('id',
                  'date',
                  'attendees',
                  'course',
                  'supervisor',
                  'start_time',
                  'end_time',
                  'time_in_hours'
                  )

    def create(self, validated_data):
        """
        Overwrites create() to ensure the course supervisors are used if not
        explicitly stated.

        Note: This cannot be done in the models save() method because changes
        to many-to-many fields are not valid in a specific models save procedure

        Also note how the validated_data already contains full fledged
        objects and not the original representations (PKs) passed to the API

        :param validated_data: Python-like data and full-fledged objects
        :return: the full fledged instance of the SpecificDate model
        """
        if len(validated_data['supervisor']) == 0:
            course = validated_data['course']
            validated_data['supervisor'] = course.supervisor.all()

        specific_date = super(SpecificDateSerializer, self).create(validated_data)

        return specific_date

    def get_attendees(obj):
        """
        Special serializer method field to ensure a SpecificDate
        always represents the attendees based on the active subscription to
        the related course

        :param obj: the currently serialized instance
        :return: the serialized data for the field attendees
        """
        for sub in obj.course.subscriptions.all().exclude(course__eventtype=1):
            if sub.active:
                Attendance.objects.get_or_create(member=sub.member, date=obj)

        # clean out obsolete attendance objects
        # TODO: Delete when no ACTIVE subscription at this date
        for attendance in obj.attendance_set.all():
            if not Subscription.objects.all().\
                    filter(member=attendance.member,
                           course=attendance.date.course).exists():

                if attendance.date.course.eventtype is not 1:
                    # No subscription for the course of this
                    # attendance, thus delete attendance
                    attendance.delete()

        attendance_set = obj.attendance_set
        serializer = AttendanceSerializer(attendance_set, many=True)

        return serializer.data

    def validate(self, data):
        """
        Validates:
         1. only dates related to the course dates (i.e weekday of the course)
         can be created
         2. Only one supervisor for Free-Training dates is submitted.

        :param data: to be validated
        :return: validated data
        """
        # only check for validity if course specifies a day
        # e.g. Free-training does not specify a day, thus all days are valid
        if data['course'].day_of_week is not None:
            if data['date'].weekday() != data['course'].day_of_week:
                raise serializers.ValidationError(gs.DATE_NOT_ON_WEEKDAY)

        if len(data['supervisor']) > 1 and data['course'].eventtype is 1:
            raise serializers.ValidationError(
                gs.TOO_MANY_SUPERVISROS)

        return super(SpecificDateSerializer, self).validate(data)


class SupervisorSerializer(serializers.ModelSerializer):

    birthday = serializers.DateField(input_formats=settings.DATE_INPUT_FORMATS)

    # required user fields
    username = serializers.CharField(source='user.username')
    email = serializers.EmailField(source='user.email')
    password = serializers.CharField(source='user.password', write_only=True)


    class Meta:
        model = SupervisorProfile

        fields = ('id',
                  'first_name',
                  'last_name',
                  'address',
                  'birthday',
                  'wage',
                  'secondary_wage',
                  'banking_info',
                  # user model
                  'username',
                  'email',
                  'password',
                  # property methods
                  'amount_due',
                  'last_payment_date',
                  # FK related fields
                  'department',
                  'courses',
                  'supervised_dates',
                  )

        related_fields = ['user']
        # make all FK fields read_only
        extra_kwargs = {
                        'courses' : {'read_only' : True},
                        'department' : {'read_only' : True},
                        'supervised_dates' : {'read_only' : True}
                        }

    def update(self, instance, validated_data):
        """Overwrite update() to set related user instance values"""

        pw = validated_data['user']['password']
        if instance.user.check_password(pw):
            # pretty much Non-sense
            instance.user.set_password(pw)
        else:
            raise serializers.ValidationError(gs.WRONG_PASSWORD)

        instance.user.email = validated_data['user']['email']
        instance.user.username = validated_data['user']['username']
        # pre-save to generate the full user instance
        instance.save()
        validated_data['user'] = instance.user
        return super(SupervisorSerializer, self).update(instance, validated_data)

    def create(self, validated_data):
        """Manually generate user instance to be added to the one-2-one field"""
        userdata = {'email' : validated_data['user'].pop('email'),
                  'username' : validated_data['user'].pop('username'),}
        user = User.objects.create(**userdata)

        # stores a salted hash of the password
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
        fields = ('id',
                  'password',
                  'first_name',
                  'last_name',
                  'email',
                  'address')

        write_only_fields = ('password',)
        read_only_fields = ('is_staff',
                            'is_superuser',
                            'is_active',
                            'date_joined',)


class CourseSerializer(serializers.ModelSerializer):

    supervisor = SupervisorField(queryset=SupervisorProfile.objects.all(), many=True)

    members = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Course
        fields = ('id',
                  'name',
                  'day_of_week',
                  'supervisor',
                  'department',
                  'members',
                  'waiting_list',
                  'eventtype',
                  'start_time',
                  'end_time',
                  'time_in_hours',
                  # property fields
                  'number_of_participants',
                  'total_money_earned',
                  'total_money_spent',
                  'balance',
                  'avg_attendance',
                  'max_attendees',
                  'size_of_waitinglist'
                  )

    def get_members(self, obj):
        """
        Returns current members of this course by querying active subscriptions
        and returning the related members

        :param obj: the instance of this Course model
        :return: serialized data for the field members
        """
        active_subscriptions = Subscription.objects.filter(
            models.Q(course=obj.pk)
            & (models.Q(end_date__isnull = True)
            | models.Q(end_date__gte = datetime.date.today()))
        )

        members = Member.objects.filter(subscriptions__in=active_subscriptions)
        serializer = MemberSerializer(members, many=True)
        return serializer.data


class SubscriptionSerializer(serializers.ModelSerializer):

    start_date = serializers.DateField(input_formats=settings.DATE_INPUT_FORMATS)
    end_date = serializers.DateField(input_formats=settings.DATE_INPUT_FORMATS)

    class Meta:
        model = Subscription
        fields = ('id',
                  'course',
                  'member',
                  'start_date',
                  'end_date',
                  'value',
                  # property fields
                  'accumulated_value',
                  'length',
                  'active')

    def validate(self, data):
        """
        Validates that:
         1. Course is not full yet
            if it is, a waiting-list entry is automatically created
         2. Start date is before end date
         3. No conflicting subscription exists
        :param data: to be validated
        :return: validated data
        """
        # note that number_of_participants refers to the number,
        # before this one is added thus use greater or equal
        if data['course'].number_of_participants >= data['course'].max_attendees:
            WaitingDetails.objects.create(member=data['member'],
                                          course=data['course'],
                                          note=gs.AUTO_ADD_WAITINGLIST_NOTE)
            raise serializers.ValidationError(gs.COURSE_FULL)

        # Check that start Date is before end date
        if 'end_date' in data and data['start_date'] >= data['end_date']:
            raise serializers.ValidationError(gs.START_AFTER_END)

        # Imagine a timeline with two intervals representing the subscriptions
        # A conflict, then, is either if A-start is in between B-start and
        # B-end or if A-end is between B-start and B-end or if neither A or B
        # have an end
        if 'end_date' not in data:
            conflict_count = Subscription.objects.all().\
                filter(member=data['member'].id).\
                filter(course=data['course'].id).\
                filter(models.Q(start_date__lte=data['start_date'])
                       & models.Q(end_date__gte=data['start_date'])
                       | models.Q(end_date__isnull=True)
                       ).count()
        else:
            conflict_count = Subscription.objects.all().\
                filter(member=data['member'].id).\
                filter(course=data['course'].id).\
                filter(models.Q(start_date__lte=data['start_date'])
                       & models.Q(end_date__gte=data['start_date'])
                       | models.Q(start_date__lte=data['end_date'])
                       & models.Q(end_date__gte=data['end_date'])).count()

        if conflict_count is not 0:
            raise serializers.ValidationError(gs.SUBSCRIPTION_CONFLICT)

        return super(SubscriptionSerializer, self).validate(data)


# ----------------------------------
# Standard Serializers
# ----------------------------------

class PaymentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Payment
        fields = ('id', 'member', 'course', 'date', 'value')


class SupervisorPaymentSerializer(serializers.ModelSerializer):

    supervisor = SupervisorField(queryset=SupervisorProfile.objects.all())


    class Meta:
        model = SupervisorPayment
        fields = ('id', 'supervisor', 'date', 'value', 'note')


class WaitingDetailsSerializer(serializers.ModelSerializer):

    member = MemberField(queryset=Member.objects.all())

    class Meta:
        depth = 0
        model = WaitingDetails
        fields = ('id', 'member', 'course', 'waiting_since', 'note')

class ExtraHoursSerializer(serializers.ModelSerializer):

    class Meta:
        model = ExtraHours
        fields = '__all__'
        extra_kwargs = {
            'time_in_hours' : {'read_only' : True},
        }


class IDCardSerializer(serializers.ModelSerializer):
    """Currently unused IDCard Serializer"""

    member = MemberField(queryset=Member.objects.all(),
                         allow_empty=True, allow_null=True)

    class Meta:
        model = IDCard
        fields = ('id', 'card_id', 'registered', 'member')


class AttendanceSerializer(serializers.ModelSerializer):

    member = MemberField(many=False, queryset=Member.objects.all())

    class Meta:
        model = Attendance
        fields = ('id', 'member', 'date', 'status', 'note')