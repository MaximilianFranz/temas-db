"""
The goal of this script is to reset past courses, members and supervisors so that their respective
balances are 0, in case the log was not kept perfectly (like in the beginning test phase).

This gives everyone a clean start from the beginning of this month.

Procedure is:
 - Delete Supervisor Payments
 - Delete Member Payments
 - Delete SpecificDates in the past to reset amount due of supervisors and attendance of members
 - Delete Extra Logs of Supervisors in the past
 - update active subscriptions to start this month to reset member balance
 -
"""

import os
from datetime import datetime

# Make sure Application registry is setup properly
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "temas_db.settings")
import django
django.setup()

from restapi.models import *

def delete_member_payments(delete_before=datetime.date.today()):
    """

    :param delete_before: date before which all member payments should be deleted
    :return:
    """

    all_payments_before = Payment.objects.all().filter(date__lte=delete_before)

    for payment in all_payments_before:
        payment.delete()


def delete_supervisor_payments(delete_before=datetime.date.today()):
    """

    :param delete_before:
    :return:
    """

    all_payments_before = SupervisorPayment.objects.all().filter(date__lte=delete_before)

    for payment in all_payments_before:
        all_payments_before.delete()


def delete_specificdates(delete_before=datetime.date.today()):
    """

    :param delete_before: date before which to delete all specificdates
    :return:
    """

    all_dates_before = SpecificDate.objects.all().filter(date__lte=delete_before)

    for date in all_dates_before:
        date.delete()


def update_active_subscriptions(keydate=datetime.date.today()):
    """

    :param delete_before:
    :return:
    """

    all_active_subscriptions = Subscription.objects.all().filter(
                models.Q(end_date__isnull=True)
                | models.Q(end_date__gte=keydate))

    for sub in all_active_subscriptions:
        # Set to the beginning of the month in which delete_before is
        sub.start_date = keydate.replace(day=1)
        sub.save()

def delete_extra_logs(delete_before=datetime.date.today()):
    """

    :param delete_before:
    :return:
    """
    all_extra_logs = ExtraHours.objects.all().filter(date__lte=delete_before)
    for log in all_extra_logs:
        log.delete()


if __name__ == '__main__':
    today = datetime.date.today()
    print('starting deletion process...')
    print('delete member payments')
    delete_member_payments(today)
    print('delete supervisor payments')
    delete_supervisor_payments(today)
    print('delete specific dates')
    delete_specificdates(today)
    print('delete extra hour logs')
    delete_extra_logs(today)
    print('update active subscription')
    update_active_subscriptions(today)

    print('Done!')

