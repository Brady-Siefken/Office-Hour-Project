from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

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

class Lecture(models.Model):
    CourseName = models.CharField(max_length=20)
    Instructor = models.ForeignKey(InstructorUser, on_delete=models.SET_NULL, null=True, related_name='instructor')
    MeetingTimes = models.ForeignKey(Timeslot, on_delete=models.SET_NULL, null=True, related_name='MeetingTimes')
    InstructorOfficeHours = models.ForeignKey(Timeslot, on_delete=models.SET_NULL, null=True, related_name='InstructorOfficeHours')
    TA = models.ForeignKey(AssistantUser, on_delete=models.SET_NULL, null=True, related_name='TA')
    TAOfficeHours = models.ForeignKey(Timeslot, on_delete=models.SET_NULL, null=True, related_name='TAOfficeHours')
    TAOfficeHoursApproved = models.BooleanField(default=False)
    class Meta:
        app_label = 'scheduler_app'

class Department(models.Model):
    departmentName = models.CharField(max_length=20)

class Course(models.Model):
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, related_name='courses')
    courseCode = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(999)])
    courseName = models.CharField(max_length=20)

class User(models.Model):
    USER_TYPES = [
        ('INSTRUCTOR', 'Instructor'),
        ('TA', 'TA'),
        ('STUDENT', 'Student'),
    ]

    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)
    name = models.CharField(max_length=50)
    user_type = models.CharField(max_length=20, choices=USER_TYPES)

class Section(models.Model):
    instructor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='sections')
    ta = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='sections_assisting')
    sectionCode = models.IntegerField(validators=[MinValueValidator(1),MaxValueValidator(999)])
    course = models.ForeignKey(Course, on_delete=models.SET_NULL, null=True, related_name='sections')




