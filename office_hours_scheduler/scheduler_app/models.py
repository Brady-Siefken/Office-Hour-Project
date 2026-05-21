from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from classes.constants import USER_TYPES

# Create your models here.
class StudentUser(models.Model):
    name = models.CharField(max_length=30)
    username = models.CharField(max_length=20)
    password = models.CharField(max_length=30)
    email = models.CharField(max_length=20)
    class Meta:
        app_label = 'scheduler_app'

class AdminUser(models.Model):
    name = models.CharField(max_length=30)
    username = models.CharField(max_length=20)
    password = models.CharField(max_length=30)
    email = models.CharField(max_length=20)
    class Meta:
        app_label = 'scheduler_app'

class InstructorUser(models.Model):
    name = models.CharField(max_length=30)
    username = models.CharField(max_length=20)
    password = models.CharField(max_length=30)
    email = models.CharField(max_length=20)
    class Meta:
        app_label = 'scheduler_app'

class AssistantUser(models.Model):
    name = models.CharField(max_length=30)
    username = models.CharField(max_length=20)
    password = models.CharField(max_length=30)
    email = models.CharField(max_length=20)
    class Meta:
        app_label = 'scheduler_app'

class Timeslot(models.Model):
    start_time = models.TimeField()
    end_time = models.TimeField()
    monday = models.BooleanField(default=False)
    tuesday = models.BooleanField(default=False)
    wednesday = models.BooleanField(default=False)
    thursday = models.BooleanField(default=False)
    friday = models.BooleanField(default=False)
    class Meta:
        app_label = 'scheduler_app'

    def __str__(self):
        # Build day abbreviations in calendar order (Mon-Fri).
        # Tuesday is "T" and Thursday is "Th" so they're distinguishable
        # when both are present (e.g., "TTh").
        day_tokens = []
        if self.monday:    day_tokens.append("M")
        if self.tuesday:   day_tokens.append("T")
        if self.wednesday: day_tokens.append("W")
        if self.thursday:  day_tokens.append("Th")
        if self.friday:    day_tokens.append("F")
        days_str = "".join(day_tokens)

        time_str = f"{self.start_time.strftime('%H:%M')}-{self.end_time.strftime('%H:%M')}"

        if days_str:
            return f"{days_str} {time_str}"
        return time_str


class Lecture(models.Model):
    CourseName = models.CharField(max_length=20)
    Instructor = models.ForeignKey(InstructorUser, on_delete=models.SET_NULL, null=True)
    MeetingTimes = models.ForeignKey(Timeslot, on_delete=models.SET_NULL, null=True, related_name='lecture_meeting_times')
    InstructorOfficeHours = models.ForeignKey(Timeslot, on_delete=models.SET_NULL, null=True, related_name='lecture_instructor_hours')
    TA = models.ForeignKey(AssistantUser, on_delete=models.SET_NULL, null=True)
    TAOfficeHours = models.ForeignKey(Timeslot, on_delete=models.SET_NULL, null=True, related_name='lecture_ta_hours')
    TAOfficeHoursApproved = models.BooleanField(default=False)

    def __str__(self):
        return self.CourseName





class Department(models.Model):
    departmentName = models.CharField(max_length=20)

    def __str__(self):
        return self.departmentName

class Course(models.Model):
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, related_name='courses')
    courseCode = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(999)])
    courseName = models.CharField(max_length=20)

    def __str__(self):
        return f"{self.department.departmentName} {self.courseCode} — {self.courseName}"



class User(models.Model):
    USER_TYPE_CHOICES = [(t, t) for t in USER_TYPES]
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)
    name = models.CharField(max_length=50)
    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES)

    def __str__(self):
        return f"{self.name} ({self.email})"

from classes.constants import SECTION_TYPES

class Section(models.Model):
    SECTION_TYPE_CHOICES = [(t, t) for t in SECTION_TYPES]

    instructor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='sections')
    ta = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='sections_assisting')
    students = models.ManyToManyField(User, blank=True, related_name='enrolled_sections')
    sectionCode = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(999)])
    course = models.ForeignKey(Course, on_delete=models.SET_NULL, null=True, related_name='sections')
    timeslot = models.ForeignKey(Timeslot, on_delete=models.SET_NULL, null=True, blank=True, related_name='sections')
    section_type = models.CharField(max_length=20, choices=SECTION_TYPE_CHOICES, default="LECTURE")

    def __str__(self):
        return f"{self.course} Section {self.sectionCode} ({self.section_type})"

class OfficeHourReservation(models.Model):
    student = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='office_hour_reservations_made'
    )

    staff = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='office_hour_reservations_received'
    )

    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='office_hour_reservations'
    )

    timeslot = models.ForeignKey(
        Timeslot,
        on_delete=models.CASCADE,
        related_name='office_hour_reservations'
    )

    reservationDate = models.DateField()
    reservedAt = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student.name} with {self.staff.name} on {self.reservationDate}"

class OfficeHour(models.Model):
        staff = models.ForeignKey(
            User,
            on_delete=models.CASCADE,
            related_name='office_hours_given'
        )

        course = models.ForeignKey(
            Course,
            on_delete=models.CASCADE,
            related_name='office_hours'
        )

        timeslot = models.ForeignKey(
            Timeslot,
            on_delete=models.CASCADE,
            related_name='office_hours'
        )

        approved = models.BooleanField(default=False) # field needed to implement proposed office hour approval

        def __str__(self):
            return f"{self.staff.name} — {self.course} ({'Approved' if self.approved else 'Pending'})"

class Reservation(models.Model):
    STATUS_CHOICES = [
        ("PENDING", "PENDING"),
        ("SUCCESSFUL", "SUCCESSFUL"),
        ("TARDY", "TARDY"),
        ("NO_SHOW", "NO_SHOW"),
    ]

    student = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reservations'
    )

    office_hour = models.ForeignKey(
        OfficeHour,
        on_delete=models.CASCADE,
        related_name='reservations'
    )

    date = models.DateField()

    chunk_start_time = models.TimeField()

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="PENDING")

    class Meta:
        unique_together = ('office_hour', 'date', 'chunk_start_time')

    def __str__(self):
        return f"{self.student.name} — {self.office_hour} on {self.date} at {self.chunk_start_time} ({self.status})"

