import unittest
from datetime import date, time, timedelta
from scheduler_app.models import User, Department, Course, Section, Timeslot, OfficeHour, Reservation
from classes.Reservation import ReservationClass


class TestReservationClass(unittest.TestCase):

    def setUp(self):
        Reservation.objects.all().delete()
        OfficeHour.objects.all().delete()
        Timeslot.objects.all().delete()
        Section.objects.all().delete()
        Course.objects.all().delete()
        Department.objects.all().delete()
        User.objects.all().delete()

        self.department = Department.objects.create(departmentName="CS")
        self.course = Course.objects.create(
            department=self.department,
            courseCode=101,
            courseName="Intro to Programming"
        )
        self.instructor = User.objects.create(
            email="instructor@test.com",
            password="pass",
            name="Dr. Smith",
            user_type="INSTRUCTOR"
        )
        self.student = User.objects.create(
            email="student@test.com",
            password="pass",
            name="Alice Johnson",
            user_type="STUDENT"
        )
        self.timeslot = Timeslot.objects.create(
            start_time=time(9, 0),
            end_time=time(10, 0),
            monday=True,
            tuesday=False,
            wednesday=True,
            thursday=False,
            friday=False
        )
        self.office_hour = OfficeHour.objects.create(
            staff=self.instructor,
            course=self.course,
            timeslot=self.timeslot,
            approved=True
        )
        self.future_date = date.today() + timedelta(days=5)
        self.reservation = Reservation.objects.create(
            student=self.student,
            office_hour=self.office_hour,
            date=self.future_date,
            chunk_start_time=time(9, 0),
            status="PENDING"
        )

    # ----------------------------
    # Constructor tests
    # ----------------------------

    def test_constructor_wraps_existing_reservation(self):
        r = ReservationClass(self.reservation.id)
        self.assertIsNotNone(r)

    def test_constructor_raises_for_missing_reservation(self):
        with self.assertRaises(ValueError):
            ReservationClass(99999)

    # ----------------------------
    # Getter tests
    # ----------------------------

    def test_get_student_returns_user_class(self):
        from classes.Users import UserClass
        r = ReservationClass(self.reservation.id)
        self.assertIsInstance(r.getStudent(), UserClass)

    def test_get_student_returns_correct_student(self):
        r = ReservationClass(self.reservation.id)
        self.assertEqual(r.getStudent().getEmail(), "student@test.com")

    def test_get_date_returns_correct_date(self):
        r = ReservationClass(self.reservation.id)
        self.assertEqual(r.getDate(), self.future_date)

    def test_get_chunk_start_time_returns_correct_time(self):
        r = ReservationClass(self.reservation.id)
        self.assertEqual(r.getChunkStartTime(), time(9, 0))

    def test_get_chunk_end_time_is_15_minutes_after_start(self):
        r = ReservationClass(self.reservation.id)
        self.assertEqual(r.getChunkEndTime(), time(9, 15))

    def test_get_status_default_is_pending(self):
        r = ReservationClass(self.reservation.id)
        self.assertEqual(r.getStatus(), "PENDING")

    # ----------------------------
    # setStatus tests
    # ----------------------------

    def test_set_status_to_successful(self):
        r = ReservationClass(self.reservation.id)
        r.setStatus("SUCCESSFUL")
        self.assertEqual(r.getStatus(), "SUCCESSFUL")

    def test_set_status_to_tardy(self):
        r = ReservationClass(self.reservation.id)
        r.setStatus("TARDY")
        self.assertEqual(r.getStatus(), "TARDY")

    def test_set_status_raises_for_invalid_status(self):
        r = ReservationClass(self.reservation.id)
        with self.assertRaises(ValueError):
            r.setStatus("INVALID")

    def test_set_status_persists_to_database(self):
        r = ReservationClass(self.reservation.id)
        r.setStatus("SUCCESSFUL")
        r2 = ReservationClass(self.reservation.id)
        self.assertEqual(r2.getStatus(), "SUCCESSFUL")

    # ----------------------------
    # cancel tests
    # ----------------------------

    def test_cancel_deletes_reservation(self):
        r = ReservationClass(self.reservation.id)
        r.cancel()
        self.assertFalse(Reservation.objects.filter(id=self.reservation.id).exists())

    # ----------------------------
    # String representation
    # ----------------------------

    def test_str_contains_student_name(self):
        r = ReservationClass(self.reservation.id)
        self.assertIn("Alice Johnson", str(r))

    def test_str_contains_course_code(self):
        r = ReservationClass(self.reservation.id)
        self.assertIn("101", str(r))

    def test_str_contains_status(self):
        r = ReservationClass(self.reservation.id)
        self.assertIn("PENDING", str(r))