from datetime import date, datetime, time, timedelta
from django.test import TestCase, Client
from scheduler_app.models import (User, Department, Course, Section, Timeslot,OfficeHour, OfficeHourReservation,)

class TestStudentReserveOfficeHours(TestCase):

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
        self.office_hour = OfficeHour.objects.create(
            staff=self.ta, course=self.course,
            timeslot=self.timeslot, approved=True,
        )

        today = date.today()
        days_until_tuesday = (1 - today.weekday()) % 7
        if days_until_tuesday == 0:
            days_until_tuesday = 7
        self.next_tuesday = today + timedelta(days=days_until_tuesday)
        self.slot_2_00 = datetime.combine(self.next_tuesday, time(14, 0))

        session = self.client.session
        session["user_id"] = self.student.email
        session["user_type"] = "STUDENT"
        session.save()

    def test_valid_reservation_creates_row(self):
        self.client.post(
            "/student/reserve/COMPSCI/361/",
            {
                "slot_start": self.slot_2_00.strftime("%Y-%m-%d %H:%M"),
                "office_hour_id": str(self.office_hour.id),
            },
        )
        self.assertEqual(OfficeHourReservation.objects.count(), 1)

    def test_same_staff_same_day_rejected(self):
        self.client.post(
            "/student/reserve/COMPSCI/361/",
            {
                "slot_start": self.slot_2_00.strftime("%Y-%m-%d %H:%M"),
                "office_hour_id": str(self.office_hour.id),
            },
        )
        slot_2_30 = datetime.combine(self.next_tuesday, time(14, 30))
        self.client.post(
            "/student/reserve/COMPSCI/361/",
            {
                "slot_start": slot_2_30.strftime("%Y-%m-%d %H:%M"),
                "office_hour_id": str(self.office_hour.id),
            },
        )
        self.assertEqual(OfficeHourReservation.objects.count(), 1)

    def test_non_student_blocked(self):
        session = self.client.session
        session["user_id"] = self.ta.email
        session["user_type"] = "TA"
        session.save()
        self.client.post(
            "/student/reserve/COMPSCI/361/",
            {
                "slot_start": self.slot_2_00.strftime("%Y-%m-%d %H:%M"),
                "office_hour_id": str(self.office_hour.id),
            },
        )
        self.assertEqual(OfficeHourReservation.objects.count(), 0)