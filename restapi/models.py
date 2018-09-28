from decimal import Decimal
import datetime

from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

from rest_framework.authtoken.models import Token

from . import global_settings as gs


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
    """Create Token vor newly created member automatically"""
    if created:
        Token.objects.create(user=instance)


class IDCard(models.Model):
    """Initially optional IDCard model"""
    card_id = models.CharField(max_length=16, unique=True)
    registered = models.DateField(default=datetime.date.today)


class Member(models.Model):
    created = models.DateField(auto_now_add=True, help_text="Date created")
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    address = models.CharField(max_length=400)
    birthday = models.DateField(default=datetime.date.today)
    mail = models.EmailField(default="")
    phone = models.CharField(max_length=20)
    picked_up = models.BooleanField(default=False, help_text="Whether this member is picked up by his parents")
    guardian = models.CharField(max_length=20,
                                default="",
                                help_text="Legal Guardian of the member if under 18")
    mailNotification = models.BooleanField(default=False,
                                           help_text="Whether this user wants to"
                                                     "receive mail "
                                                     "notification")

    id_card = models.OneToOneField(IDCard,
                                   on_delete=models.CASCADE,
                                   related_name='member',
                                   blank=True,
                                   null=True,
                                   help_text="Optional Relation to IDCard")

    def __str__(self):
        """Return string representation (for internal use mostly)"""
        return self.first_name + " " + self.last_name

    @property
    def is_waiting(self):
        """Whether this member is on a waiting list"""
        return self.waiting_for.all().count() is not 0

    @property
    def balance(self):
        """
        Returns the balance of this Member considering payments and
        subscriptions



        :return:
        """
        balance = self.payments.all().aggregate(payed=models.Sum('value')).get('payed')
        subscriptions = self.subscriptions.all().filter(
            start_date__lte=datetime.date.today())

        if balance is None:
            # If balance is NoneType make it 0
            balance = 0

        for subscription in subscriptions:
            balance -= subscription.accumulated_value

        # TODO: optimize this with proper algorithm (e.g. sliding window)
        # TODO: order subs by date, so one does not have to check all subs
        # Find all Dates attended by this users where the user does not have a
        # subscription to the related course, which is only possible in
        # free training
        all_free_training_dates = self.attended_dates.all()\
            .filter(course__eventtype=1)
        all_free_training_subs = self.subscriptions.all()\
            .filter(course__eventtype=1)

        for date in all_free_training_dates:
            has_sub = False
            for sub in all_free_training_subs:
                has_sub = self.colides(date, sub)
            if not has_sub:
                # if no subscription for this date exists charge 3€
                balance -= gs.DEFAULT_ATTENDANCE_COST

        return round(balance, 2)

    def colides(self, date, sub):
        """
        Whether the given date lies within the date range of the
        given subscription

        :param date: SpecificDate object
        :param sub: Subscription object
        :return: Whether the dates collide
        """
        if sub.end_date is None:
            # Subscription is open-ended, then on start_date has to be
            # considered
            return date.date > sub.start_date

        if date.date < sub.start_date or date.date > sub.end_date:
            return False
        else:
            return True

    @property
    def percentage_attended(self):
        """
        :return: Percentage of past, subscribed course-dates this member
        attended
        """
        number_attended = self.attendance_set.filter(status__in=[2]).count()
        total_number = self.attendance_set.count()
        if number_attended is 0 or total_number is 0:
            return 0

        return round(number_attended / total_number, 2)

    @property
    def last_payment_date(self):
        """
        :return: Date of the last payment made by this member
        """
        payments = self.payments.all()
        if payments.count() != 0:
            last_payment = payments.order_by('-date')[0]
            return last_payment.date
        else:
            return datetime.date.min

    @property
    def attended_last_4_dates(self):
        """Whether this Member attended last 4 dates"""
        return self.member_attended_past_x_dates(4)

    def member_attended_past_x_dates(self, number_of_dates):
        """
        When subscribed to a normal course, this shows whether a member was
        absent more than 'number_of_dates' dates in a row.
        :param: number_of_dates: number of dates in the past to check
        :return:
        """
        active_course_subscriptions = self.subscriptions.all()\
            .exclude(course__eventtype=1)\
            .filter(models.Q(end_date__isnull=True)
                    | models.Q(end_date__gte=datetime.date.today()))

        for sub in active_course_subscriptions:
            course = sub.course
            last_dates = course.get_last_dates(number_of_dates)
            for date in last_dates:
                attended_members = date.attendees.all().filter(
                    attendance__status=2)

                if self not in attended_members:
                    return False

        return True

    def get_last_payments(self):
        return self.payments.all().order_by('-date')[:12]


class SupervisorProfile(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    address = models.TextField(max_length=400)
    birthday = models.DateField(default=datetime.date.today)

    # 4 max digits and two digits after dot. e.g. 15.00 € but not 150.0 €...; Default 15
    wage = models.DecimalField(decimal_places=2,
                               max_digits=4,
                               default=gs.DEFAULT_WAGE,
                               help_text="Hourly wage of the supervisor")

    secondary_wage = models.DecimalField(decimal_places=2,
                                         max_digits=4,
                                         default=gs.DEFAULT_SECONDARY_WAGE,
                                         help_text="Secondary Hourly wage of "
                                                   "the supervisor, i.e for "
                                                   "free training")

    banking_info = models.TextField(
        help_text="banking information of the supervisor to pay")

    department = models.IntegerField(choices=gs.DEPARTMENTS,
                                     blank=True,
                                     null=True)

    # The SupervisorProfile is a sort of facade or add-on to the User model
    # as it provides exentsive and specific detail for our case but still
    # allows us to use built-in admin functionality from Django.
    user = models.OneToOneField(User,
                                on_delete=models.CASCADE,
                                default=None,
                                related_name='supervisor_profile')

    is_admin = models.BooleanField(default=False)

    def __str__(self):
        return self.first_name + " " + self.last_name

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
        Calculates the amount of money this supervisor has to receive
        considering the amount_due on course wages and the payments already made

        :return: amount to be payed since last payment to this supervisor
        """
        # query time spent on courses
        primary_time_in_hours = self.supervised_dates.all().filter(
            models.Q(date__lte=datetime.date.today())
            & ~models.Q(course__eventtype=1)).aggregate(
            total_time=models.Sum('time_in_hours')).get('total_time')

        if primary_time_in_hours is None:
            # if is NoneType replace with 0
            primary_time_in_hours = 0

        total_amount_due = primary_time_in_hours * self.wage

        # query time spent on secondary courses (free training)
        secondary_time_in_hours = self.supervised_dates.all().filter(
            models.Q(date__lte=datetime.date.today())
            & models.Q(course__eventtype=1)).aggregate(
            total_time=models.Sum('time_in_hours')).get('total_time')

        if secondary_time_in_hours is None:
            # if NoneType replace with 0
            secondary_time_in_hours = 0

        total_amount_due += secondary_time_in_hours * self.secondary_wage

        # Add the amount of money the supervisor gets from extra work put in
        extra_hours_amount = self.extra_hours.all().aggregate(
            sum_amount=models.Sum(models.F('wage_to_pay')
                                  * models.F('time_in_hours')))\
            .get('sum_amount')

        if extra_hours_amount is None:
            # If NoneType replace with 0
            extra_hours_amount = 0

        total_amount_due += extra_hours_amount
        return round(total_amount_due - self.total_amount_payed, 2)

    @property
    def total_amount_payed(self):
        """
        TODO: To omptimize, one could add a attribute 'last_neutralized',
        which states the last date when the amount_due
        was 0. This way, one does not have to aggregate over
        all payments / dates in order to calculate the current amount_due

        :return: total amount payed to this supervisor
        """
        amount_payed = self.payments.all().aggregate(total_amount=models.Sum('value')).get('total_amount')
        if amount_payed is None:
            amount_payed = 0

        return round(amount_payed, 2)


    def get_last_payments(self):
        """
        :return: last four payments to this supervisor
        """
        return self.payments.all().order_by('-date')[:4]


class Course(models.Model):
    name = models.CharField(max_length=50)

    day_of_week = models.IntegerField(choices=gs.DAYS_OF_WEEK,
                                      max_length=10,
                                      blank=True, null=True)

    supervisor = models.ManyToManyField(SupervisorProfile,
                                        related_name='courses',
                                        blank=True, null=True)

    department = models.IntegerField(choices=gs.DEPARTMENTS,
                                     blank=True,
                                     null=True)

    eventtype = models.IntegerField(choices=gs.EVENT_TYPES,
                                    max_length=1,
                                    default=0)

    max_attendees = models.IntegerField(max_length=2,
                                        default=15,
                                        help_text='maximum number of members '
                                                  'that can subscribe')

    start_time = models.TimeField(default=gs.DEFAULT_START_TIME)
    end_time = models.TimeField(default=gs.DEFAULT_END_TIME)
    time_in_hours = models.DecimalField(max_digits=3,
                                        decimal_places=2,
                                        default=gs.DEFAULT_TIME_IN_HOURS,
                                        help_text="Start to end-time in hours")

    def __str__(self):
        """String representation for internal use"""
        return self.name

    @property
    def number_of_participants(self):
        """
        :return: the number of active subscriptions
        """

        active_subcriptions = self.subscriptions.all().filter(
                models.Q(end_date__isnull=True)
                | models.Q(end_date__gte=datetime.date.today()))

        return active_subcriptions.count()

    @property
    def total_money_earned(self):
        """
        :return: total money earned on this course through payments
        """
        total_value = self.payments.all().aggregate(
            total_value=models.Sum('value')).get('total_value')

        if total_value is None:
            # If NoneType replace with 0
            total_value = 0

        return round(total_value, 2)

    @property
    def total_money_spent(self):
        """Return total money spend on supervisor wages"""
        total = 0
        all_past_dates = self.dates.all().filter(date__lte=datetime.date.today())

        # TODO: Replace this with an optimized query expression?
        for date in all_past_dates:
            for sup in date.supervisor.all():
                total += date.time_in_hours * sup.wage

        return round(total, 2)

    @property
    def balance(self):
        """
        :return: Balance considering money spent and earned on this course
        """
        return self.total_money_earned - self.total_money_spent

    @property
    def avg_attendance(self):
        """
        :return: average percentage of participants that attended past courses
        """
        all_past_dates = self.dates.all().filter(date__lte=datetime.date.today())
        count = all_past_dates.count()
        attendance_sum = 0
        for date in all_past_dates:
            attendance_sum += date.percentage_attended

        if count or attendance_sum is 0:
            # Avoid division by zero
            return 0

        return round(attendance_sum / count, 2)

    @property
    def size_of_waitinglist(self):
        """
        :return: Number of people waiting to join this course
        """
        count = self.waiting_list.all().count()
        if count is None:
            return 0
        return count

    def get_last_dates(self, number_of_dates=4):
        """
        :param number_of_dates: last 'number_of_dates' dates are to be returned
        :return: queryset containing the last x dates of this course
        """
        return self.dates.all().order_by('-date')[:number_of_dates]

    def get_members(self):
        """
        Return Members currently subscribed to this course, ordered by
        name
        """

        active_subscriptions = self.subscriptions.all().filter(
            models.Q(end_date__isnull=True)
            | models.Q(end_date__gte=datetime.date.today()))

        return Member.objects.filter(subscriptions__in=active_subscriptions)\
            .order_by('last_name')

    def save(self, *args, **kwargs):
        """
        Override save() to set time_in_hours as a database field calculated
        from start and end-tim
        Params see Django doc.
        """
        self.time_in_hours = \
            Decimal(self.end_time.hour - self.start_time.hour +
                    (self.end_time.minute - self.start_time.minute) / 60)

        super(Course, self).save()


class SpecificDate(models.Model):
    date = models.DateField(auto_now_add=False, default=datetime.date.today)

    attendees = models.ManyToManyField(Member,
                                       related_name='attended_dates',
                                       through='Attendance')

    course = models.ForeignKey(Course,
                               on_delete=models.CASCADE,
                               related_name='dates')

    supervisor = models.ManyToManyField(SupervisorProfile,
                                        related_name='supervised_dates',
                                        blank=True, null=True)

    start_time = models.TimeField(blank=True, null=True)
    end_time = models.TimeField(blank=True, null=True)

    time_in_hours = models.DecimalField(max_digits=3,
                                        decimal_places=2,
                                        help_text="End minus Start-Time in hours",
                                        default=1.5)

    def __str__(self):
        """String representation for internal use"""
        return self.course.name + " on " + str(self.date)

    class Meta:
        """Defines unique fields to avoid duplicates"""
        unique_together = ('date', 'course')

    def is_past(self):
        return self.date < datetime.datetime.today().date()

    @property
    def percentage_attended(self):
        number_attended = self.attendance_set.all().filter(status__in=[2]).count()
        total = self.attendance_set.all().count()

        if number_attended is 0 or total is 0:
            return 0

        return round(number_attended / total, 2)

    def save(self, *args, **kwargs):
        """
        Override save() to:
        1. fill fields from related course if not stated otherwise
        2. create Attendance based on subscription that were active on this
        date or will be active on this date

        Note: Supervision is managed in Serialzer create(),
        since manipulation m2m relationships in here is not viable.
        :return: Model instance as required
        """
        # pre_save to work with relations and model
        super(SpecificDate, self).save(*args, **kwargs)

        # when custom start and end time are required,
        # one must set them both, otherwise course data will be used
        if self.start_time is None or self.end_time is None:
            self.start_time = self.course.start_time
            self.end_time = self.course.end_time
            self.time_in_hours = self.course.time_in_hours
        else:
            # set time_in_hours independently of course if start and end-time are set.
            self.time_in_hours = \
                Decimal(self.end_time.hour - self.start_time.hour +
                        (self.end_time.minute - self.start_time.minute) / 60)

        active_course_subcriptions = self.course.subscriptions.all().filter(
            models.Q(start_date__lte=self.date)
            & (models.Q(end_date__isnull=True)
               | models.Q(end_date__gte=self.date))
        )

        # active_course_subcriptions = self.course.subscriptions.all().filter(
        #     models.Q(end_date__isnull=True)
        #     | models.Q( end_date__gte=datetime.date.today()))

        if self.course.eventtype is not 1:
            # auto-generate attendance for Courses that are not 'free-training'
            for sub in active_course_subcriptions:
                # for each subscription generate attendance
                Attendance.objects.get_or_create(status=0,
                                          member=sub.member,
                                          date=self)

        super(SpecificDate, self).save()

    def get_attendees(self):
        """
        Special Method that ensures that only attendance objects exist for this
        date if there is an active subscription. This is achieved by
        rechecking every time the attendees are queried.
        Example: It could happen that an attendance is auto-created based on a
        subscription, which is then later deleted or shortened (i.e. canceled)
        so that the attendance object is obsolete.

        :return: Attendees of this date based on active subcriptions
        """

        # Create attendance for this date based on subscriptions that are active on
        # this date.
        active_subscriptions = self.course.subscriptions.all().exclude(
            course__eventtype=1).filter(
                            models.Q(start_date__lte=self.date)
                            & (models.Q(end_date__isnull=True)
                                | models.Q(end_date__gte=self.date)))

        for sub in active_subscriptions:
            Attendance.objects.get_or_create(member=sub.member, date=self)

        # Clean out obsolete attendance objects
        for attendance in self.attendance_set.all():

            active_subscriptions = self.course.subscriptions.all().filter(
                        member=attendance.member).filter(
                            models.Q(start_date__lte=self.date)
                            & (models.Q(end_date__isnull=True)
                                | models.Q(end_date__gte=self.date)))

            if self.course.eventtype is not 1:
                if not active_subscriptions.exists():
                    attendance.delete()

        return self.attendance_set.all()



class Attendance(models.Model):
    member = models.ForeignKey(Member,
                               on_delete=models.CASCADE,
                               blank=False)

    date = models.ForeignKey(SpecificDate,
                             on_delete=models.CASCADE,
                             blank=False)

    status = models.PositiveSmallIntegerField(choices=gs.ATTENDANCE_STATUS,
                                              blank=False, default=0,
                                              help_text="Status of the "
                                                        "Attendance (e.g. "
                                                        "excused, attended,..")

    note = models.TextField(blank=True, null=True, default="")

    class Meta:
        """Set unique together to avoid duplicates in DB"""
        unique_together = ('member', 'date')


class Subscription(models.Model):
    member = models.ForeignKey(Member,
                               on_delete=models.CASCADE,
                               related_name='subscriptions')

    course = models.ForeignKey(Course,
                               on_delete=models.CASCADE,
                               related_name='subscriptions')

    start_date = models.DateField(default=datetime.date.today)
    end_date = models.DateField(null=True, blank=True)

    value = models.DecimalField(decimal_places=2,
                                max_digits=4,
                                help_text="monthly value of this subscription")

    @property
    def length(self):
        """
        :return: length in months of this subscription
        """
        if self.end_date is not None:
            delta = self.end_date - self.start_date
            return delta.days // 30

        else:
            return 'unlimited'

    @property
    def active(self):
        """
        Considered at the time of the request

        :return: Whether this subscription is currently active
        """
        if self.end_date is not None:
            return self.end_date > datetime.datetime.today().date()
        else:
            return True

    @property
    def accumulated_value(self):
        """
        Note: This returns 0 as long as the subscription is less than one month.
        It may be useful to allow half / quarter months as
        well to enable clearer distinction / billing

        TODO: make this more intelligent based on
        real months and sharper distinctions
        :return: total cost of this subscription
        """
        if self.active:
            delta = datetime.datetime.today().date() - self.start_date
            return round(self.value * (delta.days // 30), 2)
        else:
            delta = self.end_date - self.start_date
            return round(self.value * (delta.days // 30), 2)


class Payment(models.Model):
    member = models.ForeignKey(Member,
                               on_delete=models.CASCADE,
                               related_name='payments')

    course = models.ForeignKey(Course,
                               on_delete=models.CASCADE,
                               related_name='payments')

    supervisor = models.ForeignKey(SupervisorProfile,
                                   on_delete=models.CASCADE,
                                   related_name='supervised_payments',
                                   help_text="Supervisor responsible "
                                             "for this payment",
                                   blank=True, null=True)

    date = models.DateField(default=datetime.date.today)
    value = models.DecimalField(decimal_places=2, max_digits=5)

    def __str__(self):
        return "Payment: " + str(self.member) + " " + str(self.value) + " for " \
               + str(self.course)


class SupervisorPayment(models.Model):
    supervisor = models.ForeignKey(SupervisorProfile,
                                   on_delete=models.CASCADE,
                                   related_name='payments')

    date = models.DateField(auto_now_add=True,
                            help_text="Date of the payment; auto add now is on",
                            blank=True, null=True)

    value = models.DecimalField(decimal_places=2,
                                max_digits=5,
                                default=0,
                                help_text="Loan paid to supervisor")

    note = models.TextField(help_text="Additional notes regarding the payment",
                            blank=True, null=True)

    def __str__(self):
        return str(self.supervisor) + "; " + str(self.value) + " on " + str(self.date)


class WaitingDetails(models.Model):
    member = models.ForeignKey(Member,
                               on_delete=models.CASCADE,
                               related_name='waiting_for')

    # Doesn't have to wait for a specific course
    course = models.ForeignKey(Course,
                               on_delete=models.CASCADE,
                               related_name='waiting_list',
                               blank=True, null=True)

    # e.g. write in note for which courses member is potentially waiting.
    note = models.TextField(
        help_text='Additional info about the waiting list entry',
        blank=True, null=True)

    waiting_since = models.DateField(default=datetime.date.today,
                                     help_text="date since when the member is "
                                               "waiting",
                                     null=True, blank=True)


class ExtraHours(models.Model):
    supervisor = models.ForeignKey(SupervisorProfile,
                                   on_delete=models.CASCADE,
                                   related_name='extra_hours')
    date = models.DateField(default=datetime.date.today,
                            help_text='Date of the extra work')

    # explicit times are required
    start_time = models.TimeField(help_text='Start time of the extra work')
    end_time = models.TimeField(help_text='End time of the extra work')

    time_in_hours = models.DecimalField(max_digits=4,
                                        decimal_places=2,
                                        help_text='time in hours',
                                        null=True, blank=True)

    wage_to_pay = models.DecimalField(max_digits=4,
                                      decimal_places=2,
                                      help_text='Wage to be paid for this time,'
                                                ' if none supervisor.wage is '
                                                'used',
                                      null=True, blank=True)

    note = models.TextField(help_text='Note on the reason or '
                                      'content of the extra work',
                            null=True, blank=True)

    def save(self, *args, **kwargs):
        """Overwrite save() to set time_in_hours and default wage if
        necessary
        """
        self.time_in_hours = Decimal(self.end_time.hour - self.start_time.hour + \
                                         (self.end_time.minute - self.start_time.minute) / 60)

        if not self.wage_to_pay:
            # use default wage if not explicitly set
            self.wage_to_pay = self.supervisor.wage

        super(ExtraHours, self).save()

