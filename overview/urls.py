from django.conf.urls import url
from django.urls import path
from django.contrib.auth import views as auth_views
from overview import views


urlpatterns = [
    path('', views.course_list, name="course-list-overview"),
    path('course_detail/(?P<course_id>[0-9]+)', views.course_detail, name="course-detail-overview"),
    path('course_finance_detail/(?P<course_id>[0-9]+)', views.course_finance_detail, name="course-detail-finance-overview"),
    url(r'^login/$', auth_views.login, {'template_name': 'overview/login.html'}, name='login'),
    url(r'^logout/$', auth_views.logout, name='logout')
]