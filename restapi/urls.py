from django.conf.urls import url
from restapi import views

from rest_framework.urlpatterns import format_suffix_patterns


urlpatterns = [
    url(r'^members/$', views.MemberList.as_view(), name='member-list'),
    url(r'^members/(?P<pk>[0-9]+)/$', views.MemberDetail.as_view(), name='member-detail'),
    url(r'^dates/$', views.SpecificDateList.as_view()),
    url(r'^dates/(?P<pk>[0-9]+)/$', views.SpecificDateDetail.as_view()),
    url(r'^eventtypes/$', views.EventTypeList.as_view()),
    url(r'^eventtypes/(?P<pk>[0-9]+)/$', views.EventTypeDetail.as_view()),
    url(r'^supervisors/$', views.SupervisorList.as_view()),
    url(r'^supervisors/(?P<pk>[0-9]+)/$', views.SupervisorDetail.as_view()),
    url(r'^courses/$', views.CourseList.as_view()),
    url(r'^courses/(?P<pk>[0-9]+)/$', views.CourseDetail.as_view()),
    url(r'^departments/$', views.DepartmentList.as_view(), name='department-list'),
    url(r'^departments/(?P<pk>[0-9]+)/$', views.DepartmentList.as_view(), name='department-detail'),
    url(r'^subscriptions/$', views.SubscriptionList.as_view()),
    url(r'^subscriptions/(?P<pk>[0-9]+)/$', views.SubscriptionDetail.as_view()),
    url(r'^payments/$', views.PaymentDetail.as_view()),
    url(r'^payments/(?P<pk>[0-9]+)/$', views.PaymentDetail.as_view()),
    url(r'^idcards/$', views.IDCardList.as_view()),
    url(r'^idcards/(?P<pk>[0-9]+)/$', views.IDCardDetail.as_view())
]

# This allows to use multiple formats together with the generic 'Response' used in class based views
urlpatterns = format_suffix_patterns(urlpatterns)
