from django.contrib import admin

# Register your models here.
from .models import *

admin.site.register(SupervisorProfile)
admin.site.register(Member)
admin.site.register(Course)
admin.site.register(Subscription)
admin.site.register(SupervisorPayment)
admin.site.register(Payment)
admin.site.register(SpecificDate)
admin.site.register(ExtraHours)
admin.site.register(Attendance)
