from django.contrib import admin
from scheduler_app.models import (
    User,
    Course,
    Department,
    Section,
    Timeslot,
    OfficeHour,
    OfficeHourReservation,
    Reservation,
)

# Register your models here.
admin.site.register(User)
admin.site.register(Course)
admin.site.register(Department)
admin.site.register(Section)
admin.site.register(OfficeHour)
admin.site.register(OfficeHourReservation)
