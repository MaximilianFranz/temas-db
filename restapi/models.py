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
    card_id = models.CharField(max_length=16, unique=True)  # Uniqueness by card_id is required
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
    # photo = models.ImageField()
    id_card = models.OneToOneField(IDCard, on_delete=models.CASCADE, related_name='member', blank=True, null=True)

    def __str__(self):
        return self.first_name + " " + self.last_name

    @property
    def is_waiting(self):
        return self.waiting_for.all().count() is not 0

    @property
    def balance(self):
        # TODO: Update to use query expression
        payments = self.payments.all()
        balance = self.payments.all().aggregate(payed=models.Sum('value')).get('payed')
        subcriptions = self.subscriptions.all()


        if balance is None:
            balance = 0

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
        if number_attended is 0 or total_number is 0:
            return 0

        return number_attended / total_number

    @property
    def last_payment_date(self):
        """
        Date of last payment made by this member
        :return:
        """

        payments = self.payments.all()
        if payments.count() != 0:
            last_payment = payments.order_by('-date')[0]
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
    has_prio = models.BooleanField(default=False)  # whether or not attendance ought to be reported!
    has_payment = models.BooleanField(default=True)
    has_subscription = models.BooleanField(default=True)


class SupervisorProfile(models.Model):
    first_name = models.CharField(max_length=50)

    last_name = models.CharField(max_length=50)

    address = models.TextField(max_length=400)

    birthday = models.DateField(default=datetime.date.today)

    # 4 max digits and two digits after dot. e.g. 15.00 € but not 150.0 €...; Default 15
    wage = models.DecimalField(decimal_places=2, max_digits=4, default=15, help_text="Hourly wage of the supervisor")

    banking_info = models.TextField(help_text="banking information of the supervisor to pay")

    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='supervisors', blank=True,
                                   null=True)  # multiple per Dep

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
        # query SpecificDates until today and sum over time_in_hours
        # models.Q(date__gte = self.last_payment_date) &
        total_time_in_hours = self.supervised_dates.all().filter(models.Q(date__lte=datetime.date.today())). \
            aggregate(total_time=models.Sum('time_in_hours')).get('total_time')

        if total_time_in_hours is None:
            total_time_in_hours = 0

        total_amount_due = total_time_in_hours * self.wage
        return total_amount_due - self.total_amount_payed

    @property
    def total_amount_payed(self):
        amount_payed = self.payments.all().aggregate(total_amount=models.Sum('value')).get('total_amount')
        if amount_payed is None:
            amount_payed = 0

        return amount_payed

DAYS_OF_WEEK = ((0, 'Monday'),
                (1, 'Tuesday'),
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
    max_attendees = models.IntegerField(max_length=2, default=15, help_text='maximum number of members that can subscribe')

    # TODO : Refactor default times clean!
    start_time = models.TimeField(default=datetime.time(16, 00, 00))
    end_time = models.TimeField(default=datetime.time(17, 30, 00))
    time_in_hours = models.DecimalField(max_digits=3, decimal_places=2, default=1.5,
                                        help_text="Start to end-time in hours")

    @property
    def number_of_participants(self):
        """
        Number of Attendees this course currently has, as in the number of active subscriptions
        :return:
        """

        active_subcriptions = self.subscriptions.all().filter(models.Q(end_date__isnull=True) |
                                                              models.Q(end_date__gte=datetime.date.today()))
        return active_subcriptions.count()

    @property
    def total_money_earned(self):
        # Always check aggregated values for None, as it doesn't return 0 when no entries were found
        total_value = self.payments.all().aggregate(total_value=models.Sum('value')).get('total_value')
        if total_value is None:
            total_value = 0

        return total_value

    @property
    def total_money_spent(self):
        total = 0
        all_past_dates = self.dates.all().filter(date__lte=datetime.date.today())

        # TODO: Replace this with a query expression?
        for date in all_past_dates:
            # manually calculate total time in hours of this course from datetime.time objects
            for sup in date.supervisor.all():
                total += date.time_in_hours * sup.wage

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
            attendance_sum += date.percentage_attended

        if count is 0:
            return 0

        return attendance_sum / count


    def save(self, *args, **kwargs):
        """

        Override save() to set time_in_hours as a database field calculated from start and end-tim

        Params see Django doc.
        """
        self.time_in_hours = Decimal(self.end_time.hour - self.start_time.hour + \
                                     (self.end_time.minute - self.start_time.minute) / 60)

        super(Course, self).save()


class SpecificDate(models.Model):
    date = models.DateField(auto_now_add=False, default=datetime.date.today)
    attendees = models.ManyToManyField(Member, related_name='attended_dates', through='Attendance')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, default=None, related_name='dates')
    supervisor = models.ManyToManyField(SupervisorProfile, blank=True, null=True, related_name='supervised_dates')

    start_time = models.TimeField(blank=True, null=True)
    end_time = models.TimeField(blank=True, null=True)
    time_in_hours = models.DecimalField(max_digits=3, decimal_places=2, help_text="End minus Start-Time in hours",
                                        default=1.5)

    # DEBUG Representation
    def __str__(self):
        return self.course.name + " am " + str(self.date)

    class Meta:
        unique_together = ('date', 'course')

    def is_past(self):
        return self.date < datetime.datetime.today().date()

    @property
    def percentage_attended(self):
        number_attended = self.attendance_set.all().filter(status__in=[2]).count()
        total = self.attendance_set.all().count()

        if number_attended is 0 or total is 0:
            return 0

        return number_attended / total

    def save(self, *args, **kwargs):
        """

        Override save() to
        1. fill fields from related course if not stated otherwise
        2. create Attendance based on subscription

        Note: Supervision is managed in Serialzer create(), since manipulation m2m relationships
        in here is not viable.

        :return:
        """
        # pre_save to work with relations and model
        super(SpecificDate, self).save(*args, **kwargs)

        # when custom start and end time are required, one must set them both, otherwise course data will be used
        if self.start_time is None or self.end_time is None:
            self.start_time = self.course.start_time
            self.end_time = self.course.end_time
            self.time_in_hours = self.course.time_in_hours  # Also set this, as it only depends on start / end time
        else:
            # set time_in_hours independently of course if start and end-time are set.
            self.time_in_hours = Decimal(self.end_time.hour - self.start_time.hour + \
                                         (self.end_time.minute - self.start_time.minute) / 60)

        # TODO: Fix. This should return subscriptions that were active on the specificDate date.
        active_course_subcriptions = self.course.subscriptions.all().filter(models.Q(end_date__isnull=True) |
                                                                            models.Q(
                                                                                end_date__gte=datetime.date.today()))
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
    value = models.DecimalField(decimal_places=2, max_digits=4, help_text="monthly value of this subscription")

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
            return self.value * (delta.days // 30)


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
    date = models.DateField(auto_now_add=True, help_text="Date of the payment; auto add now is on", blank=True,
                            null=True)
    value = models.DecimalField(decimal_places=2, max_digits=5, default=15, help_text="Loan paid")
    note = models.TextField(help_text="Additional notes regarding the payment", blank=True, null=True)


class WaitingDetails(models.Model):
    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='waiting_for')
    # Doesn't have to wait for a specific course
    course = models.ForeignKey(Course, on_delete=models.CASCADE, blank=True, null=True, related_name='waiting_list')
    note = models.TextField(help_text='Additional info about the waiting list entry', blank=True, null=True)
    waiting_since = models.DateField(default=datetime.date.today, help_text="since when the member is waiting")
