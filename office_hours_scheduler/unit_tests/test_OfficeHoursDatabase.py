from django.test import TestCase
from scheduler_app.models import (User, Course, Department, Section, Timeslot, OfficeHour)
from classes.OfficeHours import OfficeHoursClass
from classes.OfficeHoursDatabase import (getPendingOfficeHoursForInstructor, getOfficeHour,approveOfficeHour,  rejectOfficeHour,)

class OfficeHoursDatabaseTestSetup(TestCase):
    """
    Shared setUp:
      - one instructor teaching one section in COMPSCI 361
      - two TAs: ta1 assists the section, ta2 does NOT
      - one pending office hour for ta1's course (visible to instructor)
      - one approved office hour for ta1's course (NOT pending)
      - one pending office hour for an unrelated course (NOT visible)
    """

    def setUp(self):
        self.dept = Department.objects.create(departmentName = "COMPSCI")
        self.course = Course.objects.create(
            department = self.dept, courseCode= 361, courseName = "Intro to Software Engineering"
        )
        self.unrelated_course = Course.objects.create(
            department = self.dept, courseCode = 232, courseName = "Other"
        )

        self.instructor = User.objects.create(
            email = "instructor@uwm.edu", password = "inst123", name = "inst", user_type = "INSTRUCTOR"
        )
        self.other_instructor = User.objects.create(
            email = "other_inst@uwm.edu", password = "otherinst123", name = "other inst", user_type = "INSTRUCTOR"
        )
        self.ta1 = User.objects.create(
            email = "ta1@uwm.edu", password = "ta123", name = "TA1", user_type = "TA"
        )
        self.ta2 = User.objects.create(
            email = "ta2@uwm.edu", password = "ta234", name = "TA2", user_type = "TA"
        )

        self.section = Section.objects.create(
            course = self.course, sectionCode = 1,
            instructor = self.instructor, ta = self.ta1,
        )
        self.unrelated_section = Section.objects.create(
            course = self.unrelated_course, sectionCode = 1,
            instructor = self.other_instructor, ta = self.ta2,
        )

        self.timeslot = Timeslot.objects.create(
            start_time = "14:00", end_time = "15:00", tuesday=True
        )

        # Pending hour for our instructor's course
        self.pending_hour = OfficeHour.objects.create(
            staff = self.ta1, course = self.course, timeslot = self.timeslot,
            approved = False,
        )
        # Already approved for the same course
        self.approved_hour = OfficeHour.objects.create(
            staff= self.ta1, course = self.course, timeslot = self.timeslot,
            approved = True,
        )
        # Pending hour for an unrelated course
        self.unrelated_hour = OfficeHour.objects.create(
            staff = self.ta2, course = self.unrelated_course, timeslot =self.timeslot,
            approved = False,
        )


class TestGetPendingOfficeHoursForInstructor(OfficeHoursDatabaseTestSetup):

    def test_instructor_with_multiple_courses(self):
        #An instructor teaching multiple courses sees pending hours from all of them.
        second_course = Course.objects.create(
            department = self.dept, courseCode = 400, courseName = "Advanced Topic"
        )
        Section.objects.create(
            course = second_course, sectionCode=1,
            instructor = self.instructor, ta = self.ta1,
        )
        second_course_pending = OfficeHour.objects.create(
            staff = self.ta1, course = second_course, timeslot = self.timeslot,
            approved = False,
        )

        result = getPendingOfficeHoursForInstructor("instructor@uwm.edu")
        ids = [oh.getId() for oh in result]

        # Should see the pending hour from BOTH courses
        self.assertIn(self.pending_hour.id, ids)
        self.assertIn(second_course_pending.id, ids)

    def test_pending_hours_for_my_courses(self):
        result = getPendingOfficeHoursForInstructor("instructor@uwm.edu")
        ids = [oh.getId() for oh in result]
        self.assertIn(self.pending_hour.id, ids)

    def test_does_not_return_already_approved_hours(self):
        result = getPendingOfficeHoursForInstructor("instructor@uwm.edu")
        ids = [oh.getId() for oh in result]
        self.assertNotIn(self.approved_hour.id, ids)

    def test_does_not_return_other_instructors_hours(self):
        result = getPendingOfficeHoursForInstructor("instructor@uwm.edu")
        ids = [oh.getId() for oh in result]
        self.assertNotIn(self.unrelated_hour.id, ids)

    def test_returns_wrapper_class_instances(self):
        result = getPendingOfficeHoursForInstructor("instructor@uwm.edu")
        for item in result:
            self.assertIsInstance(item, OfficeHoursClass)

    def test_unknown_instructor(self):
        result = getPendingOfficeHoursForInstructor("unkown@uwm.edu")
        self.assertEqual(result, [])

    def test_instructor_with_no_pending_returns_empty_list(self):
        # other_inst teaches unrelated_course which has unrelated_hour pending,
        # so this test creates a third instructor with no sections at all.
        lonely = User.objects.create(
            email = "lonely@uwm.edu", password = "pw", name = "Lonely", user_type = "INSTRUCTOR"
        )
        result = getPendingOfficeHoursForInstructor("lonely@uwm.edu")
        self.assertEqual(result, [])

    def test_excludes_instructor_proposed_hours(self):
        # An instructor's own pending office hour should NOT appear in (instructor hours don't need approval).
        instructor_proposed = OfficeHour.objects.create(
            staff = self.instructor,  # instructor as staff, not a TA
            course = self.course,
            timeslot = self.timeslot,
            approved = False,
        )
        result = getPendingOfficeHoursForInstructor("instructor@uwm.edu")
        ids = [oh.getId() for oh in result]
        self.assertNotIn(instructor_proposed.id, ids)

class TestGetOfficeHour(OfficeHoursDatabaseTestSetup):

    def test_existing_id_returns_wrapper(self):
        result = getOfficeHour(self.pending_hour.id)
        self.assertIsNotNone(result)
        self.assertIsInstance(result, OfficeHoursClass)
        self.assertEqual(result.getId(), self.pending_hour.id)

    def test_nonexistent_id(self):
        result = getOfficeHour(999999)
        self.assertIsNone(result)


class TestApproveOfficeHour(OfficeHoursDatabaseTestSetup):

    def test_approve_flips_approved_to_true(self):
        approveOfficeHour(self.pending_hour.id)
        refreshed = OfficeHour.objects.get(id = self.pending_hour.id)
        self.assertTrue(refreshed.approved)

    def test_approve_already_approved_is_idempotent(self):
        # Already approved -> stays approved, no exception.
        approveOfficeHour(self.approved_hour.id)
        refreshed = OfficeHour.objects.get(id = self.approved_hour.id)
        self.assertTrue(refreshed.approved)

    def test_approve_nonexistent_id_raises_value_error(self):
        with self.assertRaises(ValueError):
            approveOfficeHour(999999)


class TestRejectOfficeHour(OfficeHoursDatabaseTestSetup):

    def test_reject_deletes_the_record(self):
        target_id = self.pending_hour.id
        rejectOfficeHour(target_id)
        self.assertFalse(OfficeHour.objects.filter(id = target_id).exists())

    def test_reject_nonexistent_id_raises_value_error(self):
        with self.assertRaises(ValueError):
            rejectOfficeHour(999999)

    def test_reject_does_not_affect_other_records(self):
        rejectOfficeHour(self.pending_hour.id)
        # The other hours should still exist
        self.assertTrue(OfficeHour.objects.filter(id = self.approved_hour.id).exists())
        self.assertTrue(OfficeHour.objects.filter(id =self.unrelated_hour.id).exists())