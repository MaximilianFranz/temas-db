from rest_framework import serializers
from django.contrib.auth.models import User
from restapi.models import Member, IDCard, SpecificDate, Supervisor
from restapi.models import Department, EventType, Course, Subscription, Payment
import collections


class IDCardSerializer(serializers.ModelSerializer):

    class Meta:
        model = IDCard
        fields = ('id', 'card_id', 'registered', 'member')



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

    # TODO: How to add IDCard to a member upon creation --> Overwrite create / perform_create to cast PK into the actual object.
    id_card = serializers.PrimaryKeyRelatedField(many=False, queryset=IDCard.objects.all())
    #id_card = IDCardSerializer(many=False)

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


class SpecificDateSerializer(serializers.ModelSerializer):

    attendees = MemberField(queryset=Member.objects.all(), many=True)

    class Meta:
        depth = 2
        model = SpecificDate

        # Add 'id' field to provide for automatic id generation and adressing
        fields = ('id',
                  'date',
                  'attendees')


class SupervisorSerializer(serializers.ModelSerializer):

    class Meta:
        model = Supervisor

        fields = ('first_name' , 'last_name', 'address', 'birthday', 'department', 'course', 'id_card')


class DepartmentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Department
        fields = ('id','name', 'course', 'supervisor')


class EventTypeSerializer(serializers.ModelSerializer):

    class Meta:
        model = EventType
        fields = ('id', 'name', 'has_prio', 'has_payment', 'has_subscription')


class CourseSerializer(serializers.ModelSerializer):

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


