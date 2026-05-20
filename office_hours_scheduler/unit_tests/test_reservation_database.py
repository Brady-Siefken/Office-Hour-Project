import unittest
from datetime import date, time, timedelta, datetime
from scheduler_app.models import User, Department, Course, Section, Timeslot, OfficeHour, Reservation
from classes.Reservation import ReservationClass
from classes.ReservationDatabase import (
    isSlotTaken,
    getAvailableSlots,
    getReservation,
    getReservationsByStudent,
    getReservationsByOfficeHour,
    createReservation,
)


class TestReservationDatabase(unittest.TestCase):

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

    # ----------------------------
    # isSlotTaken tests
    # ----------------------------

    def test_is_slot_taken_returns_false_when_empty(self):
        self.assertFalse(isSlotTaken("instructor@test.com", "CS", 101, self.future_date, 1))

    def test_is_slot_taken_returns_true_when_reserved(self):
        Reservation.objects.create(
            student=self.student,
            office_hour=self.office_hour,
            date=self.future_date,
            chunk_start_time=time(9, 0),
            status="PENDING"
        )
        self.assertTrue(isSlotTaken("instructor@test.com", "CS", 101, self.future_date, 1))

    def test_is_slot_taken_returns_false_for_different_date(self):
        Reservation.objects.create(
            student=self.student,
            office_hour=self.office_hour,
            date=self.future_date,
            chunk_start_time=time(9, 0),
            status="PENDING"
        )
        other_date = self.future_date + timedelta(days=7)
        self.assertFalse(isSlotTaken("instructor@test.com", "CS", 101, other_date, 1))

    def test_is_slot_taken_returns_false_for_out_of_range_slot(self):
        self.assertFalse(isSlotTaken("instructor@test.com", "CS", 101, self.future_date, 999))

    def test_is_slot_taken_returns_false_for_missing_office_hour(self):
        self.assertFalse(isSlotTaken("nobody@test.com", "CS", 101, self.future_date, 1))

    # ----------------------------
    # getAvailableSlots tests
    # ----------------------------

    def test_get_available_slots_returns_all_slots_when_empty(self):
        slots = getAvailableSlots("instructor@test.com", "CS", 101, self.future_date)
        self.assertEqual(len(slots), 4)  # 9:00-10:00 = 4 slots

    def test_get_available_slots_returns_dicts(self):
        slots = getAvailableSlots("instructor@test.com", "CS", 101, self.future_date)
        self.assertIn('slot_number', slots[0])
        self.assertIn('start_time', slots[0])
        self.assertIn('end_time', slots[0])

    def test_get_available_slots_excludes_taken_slot(self):
        Reservation.objects.create(
            student=self.student,
            office_hour=self.office_hour,
            date=self.future_date,
            chunk_start_time=time(9, 0),
            status="PENDING"
        )
        slots = getAvailableSlots("instructor@test.com", "CS", 101, self.future_date)
        self.assertEqual(len(slots), 3)

    def test_get_available_slots_correct_times(self):
        slots = getAvailableSlots("instructor@test.com", "CS", 101, self.future_date)
        self.assertEqual(slots[0]['start_time'], "09:00 AM")
        self.assertEqual(slots[0]['end_time'], "09:15 AM")

    def test_get_available_slots_raises_for_missing_office_hour(self):
        with self.assertRaises(ValueError):
            getAvailableSlots("nobody@test.com", "CS", 101, self.future_date)

    # ----------------------------
    # getReservation tests
    # ----------------------------

    def test_get_reservation_returns_reservation_class(self):
        Reservation.objects.create(
            student=self.student,
            office_hour=self.office_hour,
            date=self.future_date,
            chunk_start_time=time(9, 0),
            status="PENDING"
        )
        r = getReservation("student@test.com", "instructor@test.com", "CS", 101, self.future_date, 1)
        self.assertIsInstance(r, ReservationClass)

    def test_get_reservation_returns_none_for_missing(self):
        r = getReservation("student@test.com", "instructor@test.com", "CS", 101, self.future_date, 1)
        self.assertIsNone(r)

    # ----------------------------
    # getReservationsByStudent tests
    # ----------------------------

    def test_get_reservations_by_student_returns_empty(self):
        result = getReservationsByStudent("student@test.com")
        self.assertEqual(result, [])

    def test_get_reservations_by_student_returns_correct_count(self):
        Reservation.objects.create(
            student=self.student,
            office_hour=self.office_hour,
            date=self.future_date,
            chunk_start_time=time(9, 0),
            status="PENDING"
        )
        result = getReservationsByStudent("student@test.com")
        self.assertEqual(len(result), 1)

    def test_get_reservations_by_student_returns_reservation_class(self):
        Reservation.objects.create(
            student=self.student,
            office_hour=self.office_hour,
            date=self.future_date,
            chunk_start_time=time(9, 0),
            status="PENDING"
        )
        result = getReservationsByStudent("student@test.com")
        self.assertIsInstance(result[0], ReservationClass)

    # ----------------------------
    # getReservationsByOfficeHour tests
    # ----------------------------

    def test_get_reservations_by_office_hour_returns_empty(self):
        result = getReservationsByOfficeHour("instructor@test.com", "CS", 101, self.future_date)
        self.assertEqual(result, [])

    def test_get_reservations_by_office_hour_returns_correct_count(self):
        Reservation.objects.create(
            student=self.student,
            office_hour=self.office_hour,
            date=self.future_date,
            chunk_start_time=time(9, 0),
            status="PENDING"
        )
        result = getReservationsByOfficeHour("instructor@test.com", "CS", 101, self.future_date)
        self.assertEqual(len(result), 1)

    # ----------------------------
    # createReservation tests
    # ----------------------------

    def test_create_reservation_creates_reservation(self):
        r = createReservation("student@test.com", "instructor@test.com", "CS", 101, self.future_date, 1)
        self.assertIsInstance(r, ReservationClass)

    def test_create_reservation_status_is_pending(self):
        r = createReservation("student@test.com", "instructor@test.com", "CS", 101, self.future_date, 1)
        self.assertEqual(r.getStatus(), "PENDING")

    def test_create_reservation_correct_date(self):
        r = createReservation("student@test.com", "instructor@test.com", "CS", 101, self.future_date, 1)
        self.assertEqual(r.getDate(), self.future_date)

    def test_create_reservation_raises_for_missing_student(self):
        with self.assertRaises(ValueError):
            createReservation("nobody@test.com", "instructor@test.com", "CS", 101, self.future_date, 1)

    def test_create_reservation_raises_for_non_student(self):
        with self.assertRaises(ValueError):
            createReservation("instructor@test.com", "instructor@test.com", "CS", 101, self.future_date, 1)

    def test_create_reservation_raises_for_missing_office_hour(self):
        with self.assertRaises(ValueError):
            createReservation("student@test.com", "nobody@test.com", "CS", 101, self.future_date, 1)

    def test_create_reservation_raises_for_out_of_range_slot(self):
        with self.assertRaises(ValueError):
            createReservation("student@test.com", "instructor@test.com", "CS", 101, self.future_date, 999)

    def test_create_reservation_raises_for_taken_slot(self):
        createReservation("student@test.com", "instructor@test.com", "CS", 101, self.future_date, 1)
        student2 = User.objects.create(
            email="student2@test.com",
            password="pass",
            name="Bob Williams",
            user_type="STUDENT"
        )
        with self.assertRaises(ValueError):
            createReservation("student2@test.com", "instructor@test.com", "CS", 101, self.future_date, 1)

    def test_create_reservation_raises_for_less_than_24_hours(self):
        tomorrow = date.today() + timedelta(days=1)
        with self.assertRaises(ValueError):
            createReservation("student@test.com", "instructor@test.com", "CS", 101, tomorrow, 1)