from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

from rest_framework.authtoken.models import Token
from temas_db import settings
from decimal import Decimal

import datetime

# TODO: Test SupervisorPayments
# TODO: Test Statistics and Detail methods with edge cases
# TODO: Replace Python logic with Database query expressions
# TODO: move all static Sets & DEFAULTS somewhere with explanation
# TODO: Explain need of blank=True and null=True.
# TODO: Comments & Doc
# TODO: Helptexts
# TODO: QuerySets? When to use?

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
    waiting_for = models.ManyToManyField(Course, through=WaitingDetails)

    def __str__(self):
        return self.first_name + " " + self.last_name

    @property
    def is_waiting(self):
        return self.waiting_for.all().count() is not 0

    @property
    def balance(self):
        payments = self.payments.all()
        balance = self.payments.all().aggregate(payed=models.Sum('value')).get('payed')
        subcriptions = self.subscriptions.all().filter(models.Q(end_date__isnull = True) |
                                                       models.Q(end_date__gte = datetime.date.today()))
        for subcription in subcriptions:
            balance -= subcription.accumulated_value

        return balance

    @property
    def percentage_attended(self):
        """

        :return: Percentage of past subscribed course-dates this member attended
        """
        number_attended = self.attendance_set.filter(status__in=[2]).count()
        total_number = self.attendance_set.count()
        return number_attended / total_number

    @property
    def last_payment_date(self):
        """
        Date of last payment made by this member
        :return:
        """

        payments = self.payments.all()
        if payments.count() != 0:
            last_payment = payments.order_by('-date')[1]
            return last_payment.date
        else:
            return datetime.date.min

    def critical(self, critical_number):
        """
        :return: True if member attendance was unspecified or not-attended
        (i.e. not excused or attended) for more than 'critical_number' times
        """
        pass



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

    # 4 max digits and two digits after dot. e.g. 15.00 € but not 150.0 €...; Default 15
    wage = models.DecimalField(decimal_places=2, max_digits=4, default=15, help_text="Hourly wage of the supervisor")

    # banking_info = models.TextField(help_text="banking information of the supervisor to pay")

    user = models.OneToOneField(User, on_delete=models.CASCADE, default=None, related_name='supervisor_profile')

    @property
    def last_payment_date(self):
        """

        :return: date of the last payment made to this supervisor
        """

        if self.payments.all().count() is not 0:
            last_payment = self.payments.all().order_by('-date')[0]
            return last_payment.date
        else:
            return datetime.date.min

    @property
    def amount_due(self):
        """

        Calculates the amount of money this supervisor has to receive calculating from the last payment

        :return: amount to be payed since last payment to this supervisor
        """
        due_dates = self.supervised_dates.all().filter(models.Q(date__gte = self.last_payment_date) &
                                           models.Q(date__lte = datetime.date.today()))

        amount_due = 0

        for date in due_dates:
            # manually calculate total time in hours of this course from datetime.time objects
            total_time_in_hours = Decimal(date.end_time.hour - date.start_time.hour + \
                                  (date.end_time.minute - date.start_time.minute) / 60)

            amount_due += total_time_in_hours * self.wage

        return amount_due



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

    @property
    def number_of_participants(self):

        active_subcriptions = self.subscriptions.all().filter(models.Q(end_date__isnull = True) |
                                                       models.Q(end_date__gte = datetime.date.today()))
        return active_subcriptions.count()

    @property
    def total_money_earned(self):
        total_value = 0
        total_value = self.payments.all().aggregate(total_value=models.Sum('value')).get('total_value')
        #
        return total_value

    @property
    def total_money_spent(self):
        total = 0
        all_past_dates = self.dates.all().filter(date__lte = datetime.date.today())

        # TODO: Replace this with a query expression?
        for date in all_past_dates:
            # manually calculate total time in hours of this course from datetime.time objects
            total_time_in_hours = Decimal(date.end_time.hour - date.start_time.hour + \
                                  (date.end_time.minute - date.start_time.minute) / 60)
            for sup in date.supervisor.all():
                total += total_time_in_hours * sup.wage

        return total

    @property
    def balance(self):
        return self.total_money_earned - self.total_money_spent

    @property
    def avg_attendance(self):
        """

        :return: average percentage of total participants that attended past courses (STATUS 2 = 'attended')
        """
        all_past_dates = self.dates.all().filter(date__lte=datetime.date.today())
        count = all_past_dates.count()
        attendance_sum = 0
        for date in all_past_dates:
            attendance_sum += date.percentage_attended()

        return attendance_sum / count

class SpecificDate(models.Model):

    date = models.DateField(auto_now_add=False, default=datetime.date.today)
    attendees = models.ManyToManyField(Member, related_name='attended_dates', through='Attendance')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, default=None, related_name='dates')
    supervisor = models.ManyToManyField(SupervisorProfile, blank=True, null=True, related_name='supervised_dates')

    start_time = models.TimeField(blank=True, null=True)
    end_time = models.TimeField(blank=True, null=True)



    # DEBUG Representation
    def __str__(self):
        return self.course.name + " am " + str(self.date)

    class Meta:
        unique_together = ('date', 'course')

    def is_past(self):
        return self.date < datetime.datetime.today().date()

    @property
    def percentage_attended(self):
        number_attended = self.attendees.all().filter(status__in = [2]).count()
        total = self.attendees.all().count()
        return number_attended / total

    def save(self, *args, **kwargs):
        # pre_save to work with relations and model
        super(SpecificDate, self).save(*args, **kwargs)

        if self.start_time is None or self.end_time is None:
            self.start_time = self.course.start_time
            self.end_time = self.course.end_time

        active_course_subcriptions = self.course.subscriptions.all().filter(models.Q(end_date__isnull = True) |
                                                                            models.Q(end_date__gte = datetime.date.today()))
        for sub in active_course_subcriptions:
            Attendance.objects.create(status=0, member=sub.member, date=self)

        super(SpecificDate, self).save()


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
    value = models.DecimalField(decimal_places=2, max_digits=4)

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
    def accumulated_value(self):
        if self.active:
            delta = datetime.datetime.today().date() - self.start_date
            return self.value * (delta.days // 30)
        else:
            delta = self.end_date - self.start_date
            return self.value * delta.days // 30

    class Meta:
        unique_together = (('member', 'course'),)


class Payment(models.Model):
    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='payments')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='payments')
    supervisor = models.ForeignKey(SupervisorProfile,
                                   on_delete=models.CASCADE,
                                   blank=True, null=True,
                                   related_name='supervised_payments')
    date = models.DateField(default=datetime.date.today)
    value = models.DecimalField(decimal_places=2, max_digits=5)


class SupervisorPayment(models.Model):

    supervisor = models.ForeignKey(SupervisorProfile, on_delete=models.CASCADE, related_name='payments')
    date = models.DateField(auto_now_add=True, help_text="Date of the payment; auto add now is on")
    value = models.DecimalField(decimal_places=2, max_digits=5, default=15, help_text="Loan paid")
    note = models.TextField(help_text="Additional notes regarding the payment")

class WaitingDetails(models.Model):
    member = models.ForeignKey(Member, on_delete=models.CASCADE)
    # Doesn't have to wait for a specific course
    course = models.ForeignKey(Course, on_delete=models.CASCADE, blank=True, null=True)
    note = models.TextField(help_text='Additional info about the waiting list entry')
    waiting_since = models.DateField(default=datetime.date.today, help_text="since when the member is waiting")