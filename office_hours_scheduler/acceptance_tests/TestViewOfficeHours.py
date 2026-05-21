from datetime import date, datetime, time, timedelta
from django.test import TestCase, Client
from scheduler_app.models import (User, Department, Course, Section, Timeslot, OfficeHour,)

class TestStudentViewAvailableHours(TestCase):

    def setUp(self):
        self.client = Client()

        self.department = Department.objects.create(departmentName="COMPSCI")
        self.course = Course.objects.create(
            department=self.department, courseCode=361, courseName="Intro SE",
        )
        self.student = User.objects.create(
            email="student@uwm.edu", password="stupass",
            name="Stu Dent", user_type="STUDENT",
        )
        self.ta = User.objects.create(
            email="ta@uwm.edu", password="tapass",
            name="Test TA", user_type="TA",
        )
        self.instructor = User.objects.create(
            email="prof@uwm.edu", password="profpass",
            name="Dr Prof", user_type="INSTRUCTOR",
        )
        self.section = Section.objects.create(
            course=self.course, sectionCode=101,
            instructor=self.instructor, ta=self.ta,
        )
        self.section.students.add(self.student)

        self.timeslot = Timeslot.objects.create(
            start_time=time(14, 0), end_time=time(15, 0), tuesday=True,
        )
        OfficeHour.objects.create(
            staff=self.ta, course=self.course,
            timeslot=self.timeslot, approved=True,
        )

        session = self.client.session
        session["user_id"] = self.student.email
        session["user_type"] = "STUDENT"
        session.save()

    def test_course_picker_shows_enrolled_course(self):
        response = self.client.get("/student/reserve/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "COMPSCI")
        self.assertContains(response, "361")

    def test_available_hours_page_loads(self):
        response = self.client.get("/student/reserve/COMPSCI/361/")
        self.assertEqual(response.status_code, 200)

    def test_unenrolled_student_redirected(self):
        other = User.objects.create(
            email="other@uwm.edu", password="x",
            name="Other", user_type="STUDENT",
        )
        session = self.client.session
        session["user_id"] = other.email
        session["user_type"] = "STUDENT"
        session.save()
        response = self.client.get("/student/reserve/COMPSCI/361/")
        self.assertRedirects(response, "/student/reserve/")

    def test_non_student_blocked(self):
        session = self.client.session
        session["user_id"] = self.ta.email
        session["user_type"] = "TA"
        session.save()
        response = self.client.get("/student/reserve/")
        self.assertRedirects(response, "/")