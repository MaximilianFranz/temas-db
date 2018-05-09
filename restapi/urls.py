from django.conf.urls import url
from restapi import views

from rest_framework.urlpatterns import format_suffix_patterns

# TODO: Replace pattern matching with django short cuts for that

urlpatterns = [
    url(r'^members/$', views.MemberList.as_view(), name='member-list'),
    url(r'^members/(?P<pk>[0-9]+)/$', views.MemberDetail.as_view(), name='member-detail'),
    url(r'^dates/$', views.SpecificDateList.as_view(), name='specificdate-list'),
    url(r'^dates/(?P<pk>[0-9]+)/$', views.SpecificDateDetail.as_view(), name='specificdate-detail'),
    url(r'^eventtypes/$', views.EventTypeList.as_view(), name='eventtype-list'),
    url(r'^eventtypes/(?P<pk>[0-9]+)/$', views.EventTypeDetail.as_view(), name='eventtype-detail'),
    url(r'^supervisors/$', views.SupervisorList.as_view(), name='supervisor-list'),
    url(r'^supervisors/(?P<pk>[0-9]+)/$', views.SupervisorDetail.as_view(), name='supervisor-detail'),
    url(r'^courses/$', views.CourseList.as_view(), name='course-list'),
    url(r'^courses/(?P<pk>[0-9]+)/$', views.CourseDetail.as_view(), name='course-detail'),
    url(r'^departments/$', views.DepartmentList.as_view(), name='department-list'),
    url(r'^departments/(?P<pk>[0-9]+)/$', views.DepartmentDetail.as_view(), name='department-detail'),
    url(r'^subscriptions/$', views.SubscriptionList.as_view(), name='subscription-list'),
    url(r'^subscriptions/(?P<pk>[0-9]+)/$', views.SubscriptionDetail.as_view(), name='subcription-detail'),
    url(r'^payments/$', views.PaymentList.as_view(), name='payment-list'),
    url(r'^payments/(?P<pk>[0-9]+)/$', views.PaymentDetail.as_view(), name='payment-detail'),
    url(r'^idcards/$', views.IDCardList.as_view(), name='idcard-list'),
    url(r'^idcards/(?P<pk>[0-9]+)/$', views.IDCardDetail.as_view(), name='idcard-detail'),
    url(r'^attendance/$', views.IDCardList.as_view(), name='attendance-list'),
    url(r'^attendance/(?P<pk>[0-9]+)/$', views.IDCardDetail.as_view(), name='attendance-detail')
]

# This allows to use multiple formats together with the generic 'Response' used in class based views
urlpatterns = format_suffix_patterns(urlpatterns)
