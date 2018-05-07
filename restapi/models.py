from django.db import models
from django.contrib.auth.models import User
import datetime
# Create your models here


class IDCard(models.Model):

    card_id = models.CharField(max_length=16, unique=True) #Uniqueness by card_id is required
    registered = models.DateField(default=datetime.date.today)



class Member(models.Model):

    created = models.DateTimeField(auto_now_add=True)
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

   # def save(self, force_insert=False, force_update=False, using=None,
    #         update_fields=None):
    #    self.id_card.member = self


class Department(models.Model):

    name = models.CharField(max_length=50)

class EventType(models.Model):

    name = models.CharField(max_length=100)
    has_prio = models.BooleanField(default=False) # whether or not attendance ought to be reported!
    has_payment = models.BooleanField(default=True)
    has_subscription = models.BooleanField(default=True)


class Supervisor(models.Model):

    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    address = models.CharField(max_length=400)
    birthday = models.DateField(default=datetime.date.today)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='supervisor')
    id_card = models.OneToOneField(IDCard, on_delete=models.CASCADE, related_name='supervisor')
    #user = models.OneToOneField(User, related_name="supervisor", on_delete=models.CASCADE)
    # TODO: Create User model for authentication together with Supervisor
    # TODO: Banking information


DAYS_OF_WEEK = (('MON','Monday'),
                ('TUE','Tuesday'),
                ('WED', 'Wednesday'),
                ('THU', 'Thursday'),
                ('FRI', 'Friday'),
                ('SAT', 'Saturday'),
                ('SUN', 'Sunday')
                )

class Course(models.Model):

    name = models.CharField(max_length=50)
    day_of_week = models.CharField(choices=DAYS_OF_WEEK, max_length=10)
    supervisor = models.ForeignKey(Supervisor, on_delete=models.CASCADE, related_name='course')
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='course')



class SpecificDate(models.Model):

    #TODO: What implications has unique_for_date ??? Can only be one instance of SpecificDate be created on any given date?
    date = models.DateField(auto_now_add=False, default=datetime.date.today)
    attendees = models.ManyToManyField(Member, related_name='attended_dates')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, default=None)
    supervisor = models.ManyToManyField(Supervisor)


    # DEBUG Representation
    def __str__(self):
        return "Specific date at " + str(self.date)


class Subscription(models.Model):

    member = models.ForeignKey(Member, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    month = models.DateTimeField(unique_for_month=True)
    value = models.FloatField()


class Payment(models.Model):
    member = models.ForeignKey(Member, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    date = models.DateTimeField(default=datetime.date.today)
    value = models.FloatField()



