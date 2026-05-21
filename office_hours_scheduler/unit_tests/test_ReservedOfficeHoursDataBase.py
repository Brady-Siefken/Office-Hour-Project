import unittest
from datetime import date, datetime, time, timedelta
from scheduler_app.models import (
    User, Course, Department, Timeslot, OfficeHour, OfficeHourReservation,
)
from classes.ReservedOfficeHours import ReservedOfficeHoursClass
from classes.ReservedOfficeHoursDatabase import (createReservation,validateReservation,getReservation,getUpcomingReservationsForStudent,getUpcomingReservationsForStaff,getReservationsForOfficeHour,)

class ReservationsTestSetup(unittest.TestCase):

    # one student, one TA, one course, one Tuesday-2pm-3pm
    #office hour block. Individual tests create reservations inside that block.

    def setUp(self):
        OfficeHourReservation.objects.all().delete()
        OfficeHour.objects.all().delete()
        Timeslot.objects.all().delete()
        Course.objects.all().delete()
        Department.objects.all().delete()
        User.objects.all().delete()

        self.department = Department.objects.create(departmentName="COMPSCI")
        self.course = Course.objects.create(
            department=self.department, courseCode=361, courseName="Intro SE",
        )
        self.student = User.objects.create(
            email="student@uwm.edu", password="x", name="Stu Dent", user_type="STUDENT",
        )
        self.other_student = User.objects.create(
            email="other@uwm.edu", password="x", name="Other Student", user_type="STUDENT",
        )
        self.ta = User.objects.create(
            email="ta@uwm.edu", password="x", name="Test TA", user_type="TA",
        )

        # An OfficeHour block: Tuesdays 2pm-3pm for CS361, hosted by the TA
        self.block_timeslot = Timeslot.objects.create(
            start_time=time(14, 0), end_time=time(15, 0), tuesday=True,
        )
        self.office_hour = OfficeHour.objects.create(
            staff=self.ta, course=self.course,
            timeslot=self.block_timeslot, approved=True,
        )

        # Pick "next Tuesday" so test runs deterministically
        today = date.today()
        days_until_tuesday = (1 - today.weekday()) % 7
        if days_until_tuesday == 0:
            days_until_tuesday = 7
        self.next_tuesday = today + timedelta(days=days_until_tuesday)

        # Reference datetimes inside the block
        self.slot_2_00 = datetime.combine(self.next_tuesday, time(14, 0))
        self.slot_2_15 = datetime.combine(self.next_tuesday, time(14, 15))
        self.slot_2_30 = datetime.combine(self.next_tuesday, time(14, 30))

        # A "now" reference well before next Tuesday so 24hr validation passes
        self.safe_now = datetime.combine(today, time(0, 0))

# createReservation

class TestCreateReservation(ReservationsTestSetup):

    def test_create_returns_wrapper(self):
        result = createReservation("student@uwm.edu", self.office_hour.id, self.slot_2_00)
        self.assertIsInstance(result, ReservedOfficeHoursClass)

    def test_create_persists_a_row(self):
        createReservation("student@uwm.edu", self.office_hour.id, self.slot_2_00)
        self.assertEqual(OfficeHourReservation.objects.count(), 1)

    def test_create_stores_correct_student_staff_course(self):
        result = createReservation("student@uwm.edu", self.office_hour.id, self.slot_2_00)
        self.assertEqual(result.getStudent().getEmail(), "student@uwm.edu")
        self.assertEqual(result.getStaff().getEmail(), "ta@uwm.edu")
        self.assertEqual(result.getCourse().getCourseCode(), 361)

    def test_create_stores_correct_date_and_start_time(self):
        result = createReservation("student@uwm.edu", self.office_hour.id, self.slot_2_15)
        self.assertEqual(result.getReservationDate(), self.next_tuesday)
        self.assertEqual(result.getStartTime(), self.slot_2_15)

    def test_create_makes_timeslot_15_minutes_long(self):
        result = createReservation("student@uwm.edu", self.office_hour.id, self.slot_2_15)
        ts = result.getTimeslot()
        self.assertEqual(ts.start_time, time(14, 15))
        self.assertEqual(ts.end_time, time(14, 30))

    def test_create_raises_for_missing_student(self):
        with self.assertRaises(ValueError):
            createReservation("ghost@uwm.edu", self.office_hour.id, self.slot_2_00)

    def test_create_raises_for_missing_office_hour(self):
        with self.assertRaises(ValueError):
            createReservation("student@uwm.edu", 999999, self.slot_2_00)

# validateReservation

class TestValidateReservation(ReservationsTestSetup):

    def test_valid_request_returns_none_or_true(self):
        # Convention: returns None on success, raises ValueError on failure.
        result = validateReservation(
            "student@uwm.edu", self.office_hour.id, self.slot_2_00, self.safe_now,
        )
        self.assertIsNone(result)

    def test_raises_when_less_than_24_hours_in_advance(self):
        now = self.slot_2_00 - timedelta(hours=23)
        with self.assertRaises(ValueError) as ctx:
            validateReservation(
                "student@uwm.edu", self.office_hour.id, self.slot_2_00, now,
            )
        self.assertIn("24", str(ctx.exception))

    def test_raises_when_slot_in_past(self):
        now = self.slot_2_00 + timedelta(hours=1)
        with self.assertRaises(ValueError):
            validateReservation(
                "student@uwm.edu", self.office_hour.id, self.slot_2_00, now,
            )

    def test_raises_when_slot_already_taken(self):
        createReservation("other@uwm.edu", self.office_hour.id, self.slot_2_15)
        with self.assertRaises(ValueError) as ctx:
            validateReservation(
                "student@uwm.edu", self.office_hour.id, self.slot_2_15, self.safe_now,
            )
        self.assertIn("taken", str(ctx.exception).lower())

    def test_raises_for_missing_student(self):
        with self.assertRaises(ValueError):
            validateReservation(
                "ghost@uwm.edu", self.office_hour.id, self.slot_2_00, self.safe_now,
            )

    def test_raises_for_missing_office_hour(self):
        with self.assertRaises(ValueError):
            validateReservation(
                "student@uwm.edu", 999999, self.slot_2_00, self.safe_now,
            )

def test_raises_when_same_staff_same_day_already_booked(self):
    #A student can only book each staff member once per day.
    # Book the TA at 14:00 on next Tuesday
    createReservation("student@uwm.edu", self.office_hour.id, self.slot_2_00)

    # Try to book the same TA at 14:30 on the same Tuesday
    with self.assertRaises(ValueError) as ctx:
        validateReservation(
            "student@uwm.edu", self.office_hour.id, self.slot_2_30, self.safe_now,
        )
    self.assertIn("already", str(ctx.exception).lower())


def test_allows_same_staff_different_day(self):
    #Same staff on a different day is fine.
    createReservation("student@uwm.edu", self.office_hour.id, self.slot_2_00)

    # Same TA, two weeks later (still Tuesday at 14:00)
    from datetime import timedelta
    far_future = self.slot_2_00 + timedelta(days=14)
    result = validateReservation(
        "student@uwm.edu", self.office_hour.id, far_future, self.safe_now,
    )
    self.assertIsNone(result)

def test_allows_different_staff_same_day(self):
    #Booking instructor and TA on the same day is allowed.
    # Add an instructor OH on the same Tuesday afternoon
    from scheduler_app.models import User as UserModel, OfficeHour, Timeslot
    from datetime import time as time_type
    instructor = UserModel.objects.create(
        email="prof@uwm.edu", password="x", name="Dr Prof", user_type="INSTRUCTOR",
    )
    instructor_ts = Timeslot.objects.create(
        start_time=time_type(16, 0), end_time=time_type(17, 0), tuesday=True,
    )
    instructor_oh = OfficeHour.objects.create(
        staff=instructor, course=self.course,
        timeslot=instructor_ts, approved=True,
    )

    # Book the TA at 14:00
    createReservation("student@uwm.edu", self.office_hour.id, self.slot_2_00)

    # Try to book the instructor at 16:00 the same Tuesday
    from datetime import datetime as dt
    instructor_slot = dt.combine(self.next_tuesday, time_type(16, 0))
    result = validateReservation(
        "student@uwm.edu", instructor_oh.id, instructor_slot, self.safe_now,
    )
    self.assertIsNone(result)

# getReservation

class TestGetReservation(ReservationsTestSetup):

    def test_returns_wrapper_for_existing_id(self):
        created = createReservation("student@uwm.edu", self.office_hour.id, self.slot_2_00)
        result = getReservation(created.getId())
        self.assertIsInstance(result, ReservedOfficeHoursClass)
        self.assertEqual(result.getId(), created.getId())

    def test_returns_none_for_missing_id(self):
        self.assertIsNone(getReservation(999999))

# getUpcomingReservationsForStudent

class TestGetUpcomingReservationsForStudent(ReservationsTestSetup):

    def test_returns_empty_when_no_reservations(self):
        result = getUpcomingReservationsForStudent("student@uwm.edu")
        self.assertEqual(result, [])

    def test_returns_only_this_students_reservations(self):
        createReservation("student@uwm.edu", self.office_hour.id, self.slot_2_00)
        createReservation("other@uwm.edu", self.office_hour.id, self.slot_2_15)
        result = getUpcomingReservationsForStudent("student@uwm.edu")
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].getStudent().getEmail(), "student@uwm.edu")

    def test_excludes_past_reservations(self):
        # Manually create a reservation in the past
        past_date = date.today() - timedelta(days=7)
        past_ts = Timeslot.objects.create(
            start_time=time(14, 0), end_time=time(14, 15), tuesday=True,
        )
        OfficeHourReservation.objects.create(
            student=self.student, staff=self.ta, course=self.course,
            timeslot=past_ts, reservationDate=past_date,
        )
        result = getUpcomingReservationsForStudent("student@uwm.edu")
        self.assertEqual(result, [])

    def test_returns_wrappers_not_models(self):
        createReservation("student@uwm.edu", self.office_hour.id, self.slot_2_00)
        result = getUpcomingReservationsForStudent("student@uwm.edu")
        self.assertIsInstance(result[0], ReservedOfficeHoursClass)

# getUpcomingReservationsForStaff

class TestGetUpcomingReservationsForStaff(ReservationsTestSetup):

    def test_returns_empty_when_no_reservations(self):
        result = getUpcomingReservationsForStaff("ta@uwm.edu")
        self.assertEqual(result, [])

    def test_returns_all_reservations_made_with_this_staff(self):
        createReservation("student@uwm.edu", self.office_hour.id, self.slot_2_00)
        createReservation("other@uwm.edu", self.office_hour.id, self.slot_2_15)
        result = getUpcomingReservationsForStaff("ta@uwm.edu")
        self.assertEqual(len(result), 2)

    def test_excludes_past_reservations(self):
        past_date = date.today() - timedelta(days=7)
        past_ts = Timeslot.objects.create(
            start_time=time(14, 0), end_time=time(14, 15), tuesday=True,
        )
        OfficeHourReservation.objects.create(
            student=self.student, staff=self.ta, course=self.course,
            timeslot=past_ts, reservationDate=past_date,
        )
        result = getUpcomingReservationsForStaff("ta@uwm.edu")
        self.assertEqual(result, [])

# getReservationsForOfficeHour

class TestGetReservationsForOfficeHour(ReservationsTestSetup):

    def test_returns_empty_when_no_reservations(self):
        result = getReservationsForOfficeHour(self.office_hour.id)
        self.assertEqual(result, [])

    def test_returns_only_reservations_for_this_office_hour(self):
        # Make a second office hour for a different course, reserve there
        other_course = Course.objects.create(
            department=self.department, courseCode=362, courseName="Other",
        )
        other_ts = Timeslot.objects.create(
            start_time=time(10, 0), end_time=time(11, 0), wednesday=True,
        )
        other_oh = OfficeHour.objects.create(
            staff=self.ta, course=other_course, timeslot=other_ts, approved=True,
        )

        createReservation("student@uwm.edu", self.office_hour.id, self.slot_2_00)
        # Make a reservation in the other OH on a Wednesday next week
        today = date.today()
        days = (2 - today.weekday()) % 7 or 7
        next_wed = today + timedelta(days=days)
        createReservation(
            "other@uwm.edu", other_oh.id, datetime.combine(next_wed, time(10, 0)),
        )

        result = getReservationsForOfficeHour(self.office_hour.id)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].getStudent().getEmail(), "student@uwm.edu")