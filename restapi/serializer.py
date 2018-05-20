from rest_framework import serializers
from django.contrib.auth.models import User
from restapi.models import Member, IDCard, SpecificDate, SupervisorProfile, Attendance
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
    member = MemberField(queryset=SupervisorProfile.objects.all(), allow_empty=True, allow_null=True)
    supervisor = serializers.PrimaryKeyRelatedField(queryset=SupervisorProfile.objects.all(), allow_empty=True, allow_null=True)

    class Meta:
        model = IDCard
        fields = ('id', 'card_id', 'registered', 'member', 'supervisor')


class SpecificDateSerializer(serializers.ModelSerializer):

    #TODO: Replace MemberField with something that automatically creates the transitionary class
    # 'Attendance' from given primary keys of members --> How to handle the status?
    attendees = MemberField(queryset=Member.objects.all(), many=True)
    course = serializers.PrimaryKeyRelatedField(queryset=Course.objects.all())
    supervisor = serializers.PrimaryKeyRelatedField(queryset=SupervisorProfile.objects.all(), many=True)

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

    # TODO: Make the CREATE call only accessible with admin permissions

    birthday = serializers.DateField(input_formats=settings.DATE_INPUT_FORMATS)
    #required user fields
    username = serializers.CharField(source='user.username')
    email = serializers.EmailField(source='user.email')
    password = serializers.CharField(source='user.password', write_only=True)

    class Meta:
        model = SupervisorProfile

        fields = ('id','first_name','last_name', 'address', 'birthday', 'department',
                  'courses', 'id_card','username', 'email', 'password')
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


        # TODO: Overwrite validate to make sure ID-Card only has either on Member or one Supervisor assigned (bad solution)


class UserSerializer(serializers.ModelSerializer):

    """
    Custom User serializer to support all fields in supervisor profile natively
    """

    address = serializers.CharField(source='supervisor_profile.address')

    class Meta:
        model = User
        fields = ('password', 'first_name', 'last_name', 'email', 'address')
        write_only_fields = ('password',)
        read_only_fields = ('is_staff', 'is_superuser', 'is_active', 'date_joined',)



class DepartmentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Department
        fields = ('id', 'name', 'courses', 'supervisors')


class EventTypeSerializer(serializers.ModelSerializer):

    class Meta:
        model = EventType
        fields = ('id', 'name', 'has_prio', 'has_payment', 'has_subscription')


class CourseSerializer(serializers.ModelSerializer):

    supervisor = serializers.PrimaryKeyRelatedField(queryset=SupervisorProfile.objects.all(), allow_empty=True, allow_null=True)
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
