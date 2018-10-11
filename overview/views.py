from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from django.contrib.auth.decorators import login_required, user_passes_test

from .models import *


def admin_test(user):
    return user.supervisor_profile.is_admin


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
    template = loader.get_template('overview/course_finance_detail.html')

    context = {
        'course' : course,
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
    dates = []
    for date in supervisor.supervised_dates.all():
        dates.append({'model': date, 'payed': round(date.time_in_hours * supervisor.wage, 2)})

    template = loader.get_template('overview/supervisor_detail.html')
    context = {
        'supervisor' : supervisor,
        'dates' : dates
    }
    return HttpResponse(template.render(context, request))