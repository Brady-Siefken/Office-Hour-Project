import unittest
from datetime import date, datetime, time, timedelta
from scheduler_app.models import (
    User, Course, Department, Timeslot, OfficeHour, OfficeHourReservation,
)
from classes.ReservedOfficeHoursDatabase import (
    getAvailableSlotsForCourse,
    createReservation,
)


class AvailableSlotsTestSetup(unittest.TestCase):
    """
    Sets up:
      - one TA, one student
      - COMPSCI 361 course
      - One approved OH: Tuesdays 2pm-3pm for CS361 hosted by the TA
      - 'now' fixed at the start of a recent Monday so weekday math is
        deterministic.
    """

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
        self.ta = User.objects.create(
            email="ta@uwm.edu", password="x", name="Test TA", user_type="TA",
        )
        self.student = User.objects.create(
            email="student@uwm.edu", password="x", name="Stu", user_type="STUDENT",
        )

        self.tuesday_ts = Timeslot.objects.create(
            start_time=time(14, 0), end_time=time(15, 0), tuesday=True,
        )
        self.office_hour = OfficeHour.objects.create(
            staff=self.ta, course=self.course,
            timeslot=self.tuesday_ts, approved=True,
        )

        # Fix 'now' = a Monday at midnight; well-defined upcoming weekdays
        today = date.today()
        days_back_to_monday = today.weekday()
        self.monday = today - timedelta(days=days_back_to_monday)
        self.now = datetime.combine(self.monday, time(0, 0))

        # Next Tuesday after `now`
        self.next_tuesday = self.monday + timedelta(days=1)


# ---------------------------------------------------------------------------
# Basic behavior
# ---------------------------------------------------------------------------

class TestGetAvailableSlotsForCourse(AvailableSlotsTestSetup):

    def test_returns_list_of_date_slot_tuples(self):
        result = getAvailableSlotsForCourse("COMPSCI", 361, self.now)
        for entry in result:
            self.assertEqual(len(entry), 2)
            entry_date, slots = entry
            self.assertIsInstance(entry_date, date)
            self.assertIsInstance(slots, list)

    def test_slots_are_dicts_with_required_keys(self):
        result = getAvailableSlotsForCourse("COMPSCI", 361, self.now)
        found_any = False
        for _, slots in result:
            for slot in slots:
                self.assertIn("start", slot)
                self.assertIn("staff_name", slot)
                self.assertIn("staff_type", slot)
                self.assertIn("office_hour_id", slot)
                found_any = True
        self.assertTrue(found_any, "expected at least one slot")

    def test_returns_slots_for_next_tuesday(self):
        result = getAvailableSlotsForCourse("COMPSCI", 361, self.now)
        dates = [d for d, _ in result]
        self.assertIn(self.next_tuesday, dates)

    def test_tuesday_has_four_15min_slots(self):
        result = getAvailableSlotsForCourse("COMPSCI", 361, self.now)
        for d, slots in result:
            if d == self.next_tuesday:
                self.assertEqual(len(slots), 4)
                return
        self.fail("next Tuesday not in result")

    def test_slot_starts_match_office_hour_times(self):
        result = getAvailableSlotsForCourse("COMPSCI", 361, self.now)
        for d, slots in result:
            if d == self.next_tuesday:
                starts = [s["start"] for s in slots]
                expected = [
                    datetime.combine(self.next_tuesday, time(14, 0)),
                    datetime.combine(self.next_tuesday, time(14, 15)),
                    datetime.combine(self.next_tuesday, time(14, 30)),
                    datetime.combine(self.next_tuesday, time(14, 45)),
                ]
                self.assertEqual(starts, expected)
                return
        self.fail("next Tuesday not in result")

    def test_slot_carries_staff_name_and_type(self):
        result = getAvailableSlotsForCourse("COMPSCI", 361, self.now)
        for d, slots in result:
            if d == self.next_tuesday:
                for s in slots:
                    self.assertEqual(s["staff_name"], "Test TA")
                    self.assertEqual(s["staff_type"], "TA")
                return
        self.fail("next Tuesday not in result")


# ---------------------------------------------------------------------------
# 24-hour rule
# ---------------------------------------------------------------------------

class TestAvailableSlots24HourRule(AvailableSlotsTestSetup):

    def test_excludes_slots_within_24hrs_of_now(self):
        """If now is Monday 3pm and Tuesday 2pm is < 24hrs away, exclude it."""
        late_monday = datetime.combine(self.monday, time(15, 0))
        result = getAvailableSlotsForCourse("COMPSCI", 361, late_monday)
        dates = [d for d, _ in result]
        self.assertNotIn(self.next_tuesday, dates)

    def test_includes_slots_more_than_24hrs_out(self):
        """Monday midnight -> Tuesday 2pm = 38 hours out, must be included."""
        result = getAvailableSlotsForCourse("COMPSCI", 361, self.now)
        dates = [d for d, _ in result]
        self.assertIn(self.next_tuesday, dates)


# ---------------------------------------------------------------------------
# Reserved-slot exclusion
# ---------------------------------------------------------------------------

class TestAvailableSlotsExcludeReserved(AvailableSlotsTestSetup):

    def test_excludes_already_reserved_slot(self):
        slot_215 = datetime.combine(self.next_tuesday, time(14, 15))
        createReservation("student@uwm.edu", self.office_hour.id, slot_215)

        result = getAvailableSlotsForCourse("COMPSCI", 361, self.now)
        for d, slots in result:
            if d == self.next_tuesday:
                starts = [s["start"] for s in slots]
                self.assertNotIn(slot_215, starts)
                self.assertEqual(len(slots), 3)
                return
        self.fail("next Tuesday not in result")

    def test_drops_date_entirely_when_all_slots_reserved(self):
        for minute in (0, 15, 30, 45):
            createReservation(
                "student@uwm.edu", self.office_hour.id,
                datetime.combine(self.next_tuesday, time(14, minute)),
            )
        result = getAvailableSlotsForCourse("COMPSCI", 361, self.now)
        dates = [d for d, _ in result]
        self.assertNotIn(self.next_tuesday, dates)


# ---------------------------------------------------------------------------
# Course filtering
# ---------------------------------------------------------------------------

class TestAvailableSlotsCourseFilter(AvailableSlotsTestSetup):

    def test_excludes_office_hours_from_other_courses(self):
        other_course = Course.objects.create(
            department=self.department, courseCode=337, courseName="Other",
        )
        other_ts = Timeslot.objects.create(
            start_time=time(10, 0), end_time=time(11, 0), tuesday=True,
        )
        OfficeHour.objects.create(
            staff=self.ta, course=other_course,
            timeslot=other_ts, approved=True,
        )

        result = getAvailableSlotsForCourse("COMPSCI", 361, self.now)
        all_starts = [s["start"] for _, slots in result for s in slots]
        morning_starts = [s for s in all_starts if s.time() < time(12, 0)]
        self.assertEqual(morning_starts, [])

    def test_excludes_unapproved_office_hours(self):
        ts2 = Timeslot.objects.create(
            start_time=time(10, 0), end_time=time(11, 0), tuesday=True,
        )
        OfficeHour.objects.create(
            staff=self.ta, course=self.course,
            timeslot=ts2, approved=False,
        )
        result = getAvailableSlotsForCourse("COMPSCI", 361, self.now)
        all_starts = [s["start"] for _, slots in result for s in slots]
        morning_starts = [s for s in all_starts if s.time() < time(12, 0)]
        self.assertEqual(morning_starts, [])


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------

class TestAvailableSlotsEdgeCases(AvailableSlotsTestSetup):

    def test_no_office_hours_returns_empty(self):
        OfficeHour.objects.all().delete()
        result = getAvailableSlotsForCourse("COMPSCI", 361, self.now)
        self.assertEqual(result, [])

    def test_nonexistent_course_returns_empty(self):
        result = getAvailableSlotsForCourse("NOPE", 999, self.now)
        self.assertEqual(result, [])

    def test_results_are_sorted_by_date(self):
        result = getAvailableSlotsForCourse("COMPSCI", 361, self.now)
        dates = [d for d, _ in result]
        self.assertEqual(dates, sorted(dates))

    def test_days_ahead_parameter_limits_window(self):
        """With days_ahead=3, a Tuesday 1 week out should not appear."""
        result = getAvailableSlotsForCourse("COMPSCI", 361, self.now, days_ahead=3)
        # From Monday midnight, only Mon/Tue/Wed should be checked.
        # Tue is included (in range), but next next-Tuesday (8 days out) won't be.
        dates = [d for d, _ in result]
        for d in dates:
            days_out = (d - self.monday).days
            self.assertLessEqual(days_out, 3)

class TestAvailableSlotsMultipleStaff(AvailableSlotsTestSetup):
    """When TA and instructor both host the same time, both appear."""

    def test_two_staff_same_time_produce_two_slots(self):
        instructor = User.objects.create(
            email="prof@uwm.edu", password="x", name="Dr Prof",
            user_type="INSTRUCTOR",
        )
        instructor_ts = Timeslot.objects.create(
            start_time=time(14, 0), end_time=time(15, 0), tuesday=True,
        )
        OfficeHour.objects.create(
            staff=instructor, course=self.course,
            timeslot=instructor_ts, approved=True,
        )

        result = getAvailableSlotsForCourse("COMPSCI", 361, self.now)
        for d, slots in result:
            if d == self.next_tuesday:
                # 4 slots from TA + 4 from instructor = 8 distinct slots
                self.assertEqual(len(slots), 8)
                staff_types = {s["staff_type"] for s in slots}
                self.assertEqual(staff_types, {"TA", "INSTRUCTOR"})
                return
        self.fail("next Tuesday not in result")