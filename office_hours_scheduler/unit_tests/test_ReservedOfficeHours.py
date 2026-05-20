import unittest
from datetime import date, datetime, time, timedelta
from scheduler_app.models import (
    User, Course, Department, Section, Timeslot, OfficeHourReservation,
)
from classes.ReservedOfficeHours import ReservedOfficeHoursClass
from classes.Users import UserClass
from classes.Course import CourseClass


class ReservedOfficeHoursTestSetup(unittest.TestCase):

    #Builds: one instructor, one TA, one student, one course with
    #one section, one Tuesday-2pm-3pm timeslot, and one reservation where the
    #student books the TA for tomorrow.

    def setUp(self):
        OfficeHourReservation.objects.all().delete()
        Section.objects.all().delete()
        Course.objects.all().delete()
        Department.objects.all().delete()
        Timeslot.objects.all().delete()
        User.objects.all().delete()

        self.department = Department.objects.create(departmentName="COMPSCI")
        self.course = Course.objects.create(
            department=self.department,
            courseCode=361,
            courseName="Intro to Software Engineering",
        )
        self.instructor = User.objects.create(
            email="instructor@uwm.edu", password="inst123",
            name="Test Instructor", user_type="INSTRUCTOR",
        )
        self.ta = User.objects.create(
            email="ta@uwm.edu", password="ta123",
            name="Test TA", user_type="TA",
        )
        self.student = User.objects.create(
            email="student@uwm.edu", password="stu123",
            name="Test Student", user_type="STUDENT",
        )
        self.section = Section.objects.create(
            course=self.course, sectionCode=101,
            instructor=self.instructor, ta=self.ta,
        )
        self.timeslot = Timeslot.objects.create(
            start_time=time(14, 0), end_time=time(15, 0), tuesday=True,
        )
        self.reservation_date = date.today() + timedelta(days=1)
        self.reservation = OfficeHourReservation.objects.create(
            student=self.student,
            staff=self.ta,
            course=self.course,
            timeslot=self.timeslot,
            reservationDate=self.reservation_date,
        )

class TestReservedOfficeHoursConstruction(ReservedOfficeHoursTestSetup):

    def test_construct_with_valid_id(self):
        wrapper = ReservedOfficeHoursClass(self.reservation.id)
        self.assertEqual(wrapper.getId(), self.reservation.id)

    def test_construct_with_invalid_id_raises(self):
        with self.assertRaises(ValueError):
            ReservedOfficeHoursClass(999999)

class TestReservedOfficeHoursGetters(ReservedOfficeHoursTestSetup):

    def setUp(self):
        super().setUp()
        self.wrapper = ReservedOfficeHoursClass(self.reservation.id)

    def test_getId(self):
        self.assertEqual(self.wrapper.getId(), self.reservation.id)

    def test_getStudent_returns_userclass(self):
        student = self.wrapper.getStudent()
        self.assertIsInstance(student, UserClass)
        self.assertEqual(student.getEmail(), "student@uwm.edu")

    def test_getStaff_returns_userclass(self):
        staff = self.wrapper.getStaff()
        self.assertIsInstance(staff, UserClass)
        self.assertEqual(staff.getEmail(), "ta@uwm.edu")

    def test_getCourse_returns_courseclass(self):
        course = self.wrapper.getCourse()
        self.assertIsInstance(course, CourseClass)
        self.assertEqual(course.getCourseDepartment(), "COMPSCI")
        self.assertEqual(course.getCourseCode(), 361)

    def test_getTimeslot_returns_model_instance(self):
        ts = self.wrapper.getTimeslot()
        self.assertEqual(ts.id, self.timeslot.id)

    def test_getReservationDate_returns_date(self):
        self.assertEqual(self.wrapper.getReservationDate(), self.reservation_date)

    def test_getStartTime_combines_date_and_timeslot_start(self):
        expected = datetime.combine(self.reservation_date, time(14, 0))
        self.assertEqual(self.wrapper.getStartTime(), expected)

class TestReservedOfficeHoursStr(ReservedOfficeHoursTestSetup):

    def test_str_includes_student_staff_and_course(self):
        wrapper = ReservedOfficeHoursClass(self.reservation.id)
        result = str(wrapper)
        self.assertIn("Test Student", result)
        self.assertIn("Test TA", result)
        self.assertIn("COMPSCI", result)
        self.assertIn("361", result)