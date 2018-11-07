from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from django.contrib.auth.decorators import login_required, user_passes_test

from django.db import models

from .models import *
from datetime import datetime

def admin_test(user):
    if user.is_staff:
        return True
    else:
        return user.supervisor_profile.is_admin

DATE_FORMAT = '%Y-%m-%d'

@login_required
def course_list(request):
    course_list = Course.objects.all()
    template = loader.get_template('overview/course_list.html')
    context = {
        'course_list' : course_list
    }
    return HttpResponse(template.render(context, request))


@user_passes_test(admin_test)
def course_detail(request, course_id):
    course = Course.objects.get(pk=course_id)
    template = loader.get_template('overview/course_detail.html')
    last_12_dates = course.get_last_dates(12)
    for date in last_12_dates:
        date.member_attendance = date.attendance_set.all().order_by('member__last_name')

    context = {
        'course' : course,
        'last_dates' : last_12_dates,

    }
    return HttpResponse(template.render(context, request))



@user_passes_test(admin_test)
def course_finance_detail(request, course_id):
    course = Course.objects.get(pk=course_id)

    if request.method == 'POST':
        if request.POST.get('dateFrom') is '':
            from_date = datetime.min
            to_date = datetime.max
        else:
            from_date = datetime.strptime(request.POST.get('dateFrom'), DATE_FORMAT)
            to_date = datetime.strptime(request.POST.get('dateTo'), DATE_FORMAT)
        payments = course.get_payments_in_range(from_date, to_date)
        dates = course.get_dates_in_range(from_date, to_date)
        payments_sum = course.total_money_earned_in_range(from_date, to_date)
        expenses_sum = course.total_money_spent_in_range(from_date, to_date)

    else:
        payments = course.payments.all()
        dates = course.get_past_dates()
        payments_sum = course.total_money_earned
        expenses_sum = course.total_money_spent

    template = loader.get_template('overview/course_finance_detail.html')

    context = {
        'course' : course,
        'dates' : dates,
        'payments' : payments,
        'payments_sum': payments_sum,
        'expenses_sum': expenses_sum
    }
    return HttpResponse(template.render(context, request))


@login_required
def supervisor_list(request):
    supervisors = SupervisorProfile.objects.all()
    template = loader.get_template('overview/supervisor_list.html')
    context = {
        'supervisors' : supervisors
    }
    return HttpResponse(template.render(context, request))

@login_required
def supervisor_detail(request, supervisor_id):
    supervisor = SupervisorProfile.objects.get(pk=supervisor_id)

    if request.method == 'POST':
        # Work with the requested dates
        if request.POST.get('dateFrom') is '':
            from_date = datetime.date.min
            to_date = datetime.date.max
        else:
            from_date = datetime.strptime(request.POST.get('dateFrom'), DATE_FORMAT)
            to_date = datetime.strptime(request.POST.get('dateTo'), DATE_FORMAT)

        payments = supervisor.get_payments_in_range(from_date, to_date)
        dates = supervisor.get_supervised_dates_in_range(from_date, to_date)
        extra_hours = supervisor.get_extra_logs_in_range(from_date, to_date)
        sum_earned = supervisor.total_amount_earned_in_range(from_date, to_date)

    else:
        # Show all
        payments = supervisor.get_all_payments()
        dates = supervisor.supervised_dates.all().order_by('-date')
        extra_hours = supervisor.extra_hours.all().order_by('-date')
        sum_earned = supervisor.total_amount_earned

    view_dates = []
    for date in dates:
        if date.course.eventtype is 1:
            wage = supervisor.secondary_wage
        else:
            wage = supervisor.wage

        view_dates.append({'model': date, 'payed': round(date.time_in_hours * wage, 2)})

    template = loader.get_template('overview/supervisor_detail.html')
    context = {
        'supervisor': supervisor,
        'dates': view_dates,
        'payments': payments,
        'payment_sum': payments.aggregate(sum=models.Sum('value')).get('sum'),
        'extra_hours': extra_hours,
        'sum_earned': sum_earned
    }
    return HttpResponse(template.render(context, request))