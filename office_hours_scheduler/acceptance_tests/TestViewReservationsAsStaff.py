from datetime import date, datetime, time, timedelta
from django.test import TestCase, Client
from scheduler_app.models import (
    User, Department, Course, Section, Timeslot,
    OfficeHour, OfficeHourReservation,
)


class TestViewReservationsAsStaffNew(TestCase):

    def setUp(self):
        self.client = Client()

        self.department = Department.objects.create(departmentName="COMPSCI")
        self.course = Course.objects.create(
            department=self.department, courseCode=361, courseName="Intro SE",
        )
        self.student = User.objects.create(
            email="student@uwm.edu", password="x",
            name="Stu Dent", user_type="STUDENT",
        )
        self.ta = User.objects.create(
            email="ta@uwm.edu", password="x",
            name="Test TA", user_type="TA",
        )
        self.instructor = User.objects.create(
            email="prof@uwm.edu", password="x",
            name="Dr Prof", user_type="INSTRUCTOR",
        )
        self.section = Section.objects.create(
            course=self.course, sectionCode=101,
            instructor=self.instructor, ta=self.ta,
        )

        today = date.today()
        days_until_tuesday = (1 - today.weekday()) % 7
        if days_until_tuesday == 0:
            days_until_tuesday = 7
        self.next_tuesday = today + timedelta(days=days_until_tuesday)

        ta_slot = Timeslot.objects.create(
            start_time=time(14, 0), end_time=time(14, 15), tuesday=True,
        )
        OfficeHourReservation.objects.create(
            student=self.student, staff=self.ta, course=self.course,
            timeslot=ta_slot, reservationDate=self.next_tuesday,
        )

        instructor_slot = Timeslot.objects.create(
            start_time=time(16, 0), end_time=time(16, 15), tuesday=True,
        )
        OfficeHourReservation.objects.create(
            student=self.student, staff=self.instructor, course=self.course,
            timeslot=instructor_slot, reservationDate=self.next_tuesday,
        )

    def _login_as(self, user, user_type):
        session = self.client.session
        session["user_id"] = user.email
        session["user_type"] = user_type
        session.save()

    def test_ta_sees_their_reservation(self):
        self._login_as(self.ta, "TA")
        response = self.client.get("/ta/reservations/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Stu Dent")

    def test_instructor_sees_their_reservation(self):
        self._login_as(self.instructor, "INSTRUCTOR")
        response = self.client.get("/instructor/reservations/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Stu Dent")

    def test_ta_does_not_see_instructors_reservation(self):
        self._login_as(self.ta, "TA")
        response = self.client.get("/ta/reservations/")
        self.assertNotContains(response, "4:00 PM")

    def test_student_blocked_from_ta_page(self):
        self._login_as(self.student, "STUDENT")
        response = self.client.get("/ta/reservations/")
        self.assertRedirects(response, "/")