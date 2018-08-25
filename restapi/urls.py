from django.conf.urls import url
from restapi import views

from rest_framework.urlpatterns import format_suffix_patterns
from rest_framework.authtoken import views as rest_framework_views

# TODO: Replace pattern matching with django short cuts for that

urlpatterns = [
    url(r'^members/$', views.MemberList.as_view(), name='member-list'),
    url(r'^members/(?P<pk>[0-9]+)/$', views.MemberDetail.as_view(), name='member-detail'),
    url(r'^dates/$', views.SpecificDateList.as_view(), name='specificdate-list'),
    url(r'^dates/(?P<pk>[0-9]+)/$', views.SpecificDateDetail.as_view(), name='specificdate-detail'),
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
    url(r'^attendance/$', views.AttendanceList.as_view(), name='attendance-list'),
    url(r'^attendance/(?P<pk>[0-9]+)/$', views.AttendanceDetails.as_view(), name='attendance-detail'),
    url(r'^users/$', views.UserList.as_view(), name='user-list'),
    url(r'^users/(?P<pk>[0-9]+)/$', views.UserDetail.as_view(), name='user-detail'),


    url(r'^supervisor_payments/$', views.SupervisorPaymentList.as_view(), name='supervisor_payment-list'),
    url(r'^supervisor_payments/(?P<pk>[0-9]+)/$', views.SupervisorPaymentDetail.as_view(), name='supervisor_payment-detail'),

    url(r'^waiting_details/$', views.WaitingDetailList.as_view(), name='waiting_details-list'),
    url(r'^waiting_details/(?P<pk>[0-9]+)/$', views.WaitingDetailSingle.as_view(), name='waiting_details-single'),

    url(r'^extrahours/$', views.ExtraHoursList.as_view(), name='extrahours-list'),
    url(r'^extrahours/(?P<pk>[0-9]+)/$', views.ExtraHoursDetail.as_view(), name='extrahours-single'),

    url(r'^coursedates/(?P<course_pk>[0-9]+)/$', views.CourseDatesList.as_view(), name='coursedates'),
    url(r'^get_sub/(?P<member_pk>[0-9]+)/(?P<course_pk>[0-9]+)/$', views.UnsubscribeMember.as_view(), name='unsubscribe'),



    url(r'^get_auth/$', rest_framework_views.obtain_auth_token, name='get_auth_token'),
    # url(r'^get_auth/$', views.auth_view, name='get_auth_token'),
    url(r'^get_userinfo/(?P<username>[\w-]+)/$', views.GetUserInfo.as_view(), name='get_user_info'),
]

# This allows to use multiple formats together with the generic 'Response' used in class based views
urlpatterns = format_suffix_patterns(urlpatterns)
