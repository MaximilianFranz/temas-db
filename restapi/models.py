from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

from rest_framework.authtoken.models import Token
from temas_db import settings

import datetime



# TODO: move all static Sets somewhere with explanation

# TODO: Explain need of blank=True and null=True.

@receiver(post_save, sender=User)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)

class IDCard(models.Model):

    card_id = models.CharField(max_length=16, unique=True) #Uniqueness by card_id is required
    registered = models.DateField(default=datetime.date.today)



class Member(models.Model):

    created = models.DateField(auto_now_add=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    address = models.CharField(max_length=400)
    birthday = models.DateField(default=datetime.date.today)
    mail = models.EmailField(default="")
    phone = models.CharField(max_length=20)
    mailNotification = models.BooleanField(default=False)
    #photo = models.ImageField()
    id_card = models.OneToOneField(IDCard, on_delete=models.CASCADE, related_name='member', blank=True, null=True)

    def __str__(self):
        return self.first_name + " " + self.last_name

    @property
    def balance(self):
        payments = self.payments.all()
        balance = 0
        for payment in payments:
            balance += payment.value

        subcriptions = self.subscriptions.all()
        for subcription in subcriptions:
            balance -= subcription.value

        return balance


class Department(models.Model):

    name = models.CharField(max_length=50)

class EventType(models.Model):

    name = models.CharField(max_length=100)
    has_prio = models.BooleanField(default=False) # whether or not attendance ought to be reported!
    has_payment = models.BooleanField(default=True)
    has_subscription = models.BooleanField(default=True)


class SupervisorProfile(models.Model):

    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    address = models.CharField(max_length=400)
    birthday = models.DateField(default=datetime.date.today)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='supervisors', blank=True, null=True) # multiple per Dep

    user = models.OneToOneField(User, on_delete=models.CASCADE, default=None, related_name='supervisor_profile')

    # TODO: Create User model for authentication together with Supervisor
    # TODO: Banking information


DAYS_OF_WEEK = ((0, 'Monday'),
                (1,'Tuesday'),
                (2, 'Wednesday'),
                (3, 'Thursday'),
                (4, 'Friday'),
                (5, 'Saturday'),
                (6, 'Sunday')
                )

class Course(models.Model):

    name = models.CharField(max_length=50)
    day_of_week = models.IntegerField(choices=DAYS_OF_WEEK, max_length=10)
    supervisor = models.ManyToManyField(SupervisorProfile, related_name='courses', blank=True, null=True)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='courses', blank=True, null=True)
    eventtype = models.ForeignKey(EventType, on_delete=models.CASCADE, related_name='courses', blank=True, null=True)

    # TODO : Refactor default times clean!
    start_time = models.TimeField(default=datetime.time(16,00,00))
    end_time = models.TimeField(default=datetime.time(17,30,00))


class SpecificDate(models.Model):

    date = models.DateField(auto_now_add=False, default=datetime.date.today)
    attendees = models.ManyToManyField(Member, related_name='attended_dates', through='Attendance')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, default=None)
    supervisor = models.ManyToManyField(SupervisorProfile, blank=True, null=True)

    start_time = models.TimeField(blank=True, null=True)
    end_time = models.TimeField(blank=True, null=True)

    # DEBUG Representation
    def __str__(self):
        return self.course.name + " am " + str(self.date)

    class Meta:
        unique_together = ('date', 'course')


ATTENDANCE_STATUS = ((0, 'not specified'),
                     (1, 'excused'),
                     (2, 'attended'),
                     (3, 'not attended'))


class Attendance(models.Model):

    member = models.ForeignKey(Member, on_delete=models.CASCADE, blank=False)
    date = models.ForeignKey(SpecificDate, on_delete=models.CASCADE, blank=False)
    status = models.PositiveSmallIntegerField(choices=ATTENDANCE_STATUS, blank=False, default=0)
    note = models.TextField(blank=True, null=True, default="")

    class Meta:
        unique_together = ('member', 'date')


class Subscription(models.Model):

    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='subscriptions')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='subscriptions')
    start_date = models.DateField(default=datetime.date.today)
    end_date = models.DateField(null=True, blank=True)
    value = models.FloatField() # monthly value of this

    @property
    def length(self):
        if self.end_date is not None:
            delta = self.end_date - self.start_date
            return delta.days // 30

        else:
            return 'unlimited'

    @property
    def active(self):
        if self.end_date is not None:
            return self.end_date > datetime.datetime.today().date()
        else:
            return True

    @property
    def total_value(self):
        if self.end_date is not None:
            delta = self.end_date - self.start_date
            return self.value * delta.days // 30
        else:
            return 0

    @property
    def current_value(self):
        if self.active:
            delta = datetime.datetime.today().date() - self.start_date
            return self.value * (delta.days // 30)
        else:
            return self.total_value

    class Meta:
        unique_together = (('member', 'course'),)


class Payment(models.Model):
    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='payments')
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    supervisor = models.ForeignKey(SupervisorProfile, on_delete=models.CASCADE, blank=True, null=True)
    date = models.DateField(default=datetime.date.today)
    value = models.FloatField()


