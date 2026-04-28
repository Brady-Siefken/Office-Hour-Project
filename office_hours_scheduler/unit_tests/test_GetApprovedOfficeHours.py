from django.test import TestCase
from scheduler_app.models import (
    User, Course, Department, Section, Timeslot, OfficeHour,
)
from classes.OfficeHours import OfficeHoursClass
from classes.OfficeHoursDatabase import getApprovedOfficeHours


class ScheduleDatabaseTestSetup(TestCase):
    """
        Creates:
          - COMPSCI department, two courses: 361 and 351
          - 1 instructor (teaches both), 2 TAs, 1 student
          - One section per course
          - Two timeslots
          - Four office hours:
              oh_361_inst         361, instructor, approved=True
              oh_361_ta1          361, ta1,        approved=True
              oh_351_ta2_approved 351, ta2,        approved=True
              oh_351_ta2_pending  351, ta2,        approved=False
    """

    def setUp(self):
        self.dept = Department.objects.create(departmentName="COMPSCI")
        self.course361 = Course.objects.create(
            department=self.dept, courseCode=361, courseName="Intro to SE")
        self.course351 = Course.objects.create(
            department=self.dept, courseCode=351, courseName="Languages")

        self.instructor = User.objects.create(
            email="prof@uwm.edu", password="x",
            name="Prof", user_type="INSTRUCTOR")
        self.ta1 = User.objects.create(
            email="ta1@uwm.edu", password="x",
            name="Alice", user_type="TA")
        self.ta2 = User.objects.create(
            email="ta2@uwm.edu", password="x",
            name="Bob", user_type="TA")
        self.student = User.objects.create(
            email="stu@uwm.edu", password="x",
            name="Stu", user_type="STUDENT")

        Section.objects.create(course=self.course361, sectionCode=1,
                               instructor=self.instructor, ta=self.ta1)
        Section.objects.create(course=self.course351, sectionCode=1,
                               instructor=self.instructor, ta=self.ta2)

        self.ts_tue = Timeslot.objects.create(
            start_time="14:00", end_time="15:00", tuesday=True)
        self.ts_thu = Timeslot.objects.create(
            start_time="10:00", end_time="11:00", thursday=True)

        self.oh_361_inst = OfficeHour.objects.create(
            staff=self.instructor, course=self.course361,
            timeslot=self.ts_tue, approved=True)
        self.oh_361_ta1 = OfficeHour.objects.create(
            staff=self.ta1, course=self.course361,
            timeslot=self.ts_thu, approved=True)
        self.oh_351_ta2_approved = OfficeHour.objects.create(
            staff=self.ta2, course=self.course351,
            timeslot=self.ts_tue, approved=True)
        self.oh_351_ta2_pending = OfficeHour.objects.create(
            staff=self.ta2, course=self.course351,
            timeslot=self.ts_thu, approved=False)


class TestGetApprovedOfficeHours(ScheduleDatabaseTestSetup):

    # no filters
    def test_returns_only_approved_hours(self):
        result = getApprovedOfficeHours()
        ids = [oh.getId() for oh in result]
        self.assertIn(self.oh_361_inst.id, ids)
        self.assertIn(self.oh_361_ta1.id, ids)
        self.assertIn(self.oh_351_ta2_approved.id, ids)
        self.assertNotIn(self.oh_351_ta2_pending.id, ids)

    def test_returns_three_approved_hours_total(self):
        self.assertEqual(len(getApprovedOfficeHours()), 3)

    def test_includes_instructor_hours_not_just_ta_hours(self):
        emails = [oh.getStaff().getEmail() for oh in getApprovedOfficeHours()]
        self.assertIn("prof@uwm.edu", emails)
        self.assertIn("ta1@uwm.edu", emails)

    def test_returns_empty_list_when_nothing_approved(self):
        OfficeHour.objects.filter(approved=True).update(approved=False)
        self.assertEqual(getApprovedOfficeHours(), [])

    def test_returns_wrapper_class_instances(self):
        for oh in getApprovedOfficeHours():
            self.assertIsInstance(oh, OfficeHoursClass)

    def test_results_are_ordered_by_course_code(self):
        codes = [oh.getCourse().getCourseCode()
                 for oh in getApprovedOfficeHours()]
        self.assertEqual(codes, sorted(codes))

        # filter by course

    def test_course_filter_returns_only_that_course(self):
        for oh in getApprovedOfficeHours(course_filter=361):
            self.assertEqual(oh.getCourse().getCourseCode(), 361)

    def test_course_filter_returns_both_instructor_and_ta(self):
        ids = [oh.getId() for oh in getApprovedOfficeHours(course_filter=361)]
        self.assertIn(self.oh_361_inst.id, ids)
        self.assertIn(self.oh_361_ta1.id, ids)
        self.assertEqual(len(ids), 2)

    def test_course_filter_excludes_pending(self):
        ids = [oh.getId() for oh in getApprovedOfficeHours(course_filter=351)]
        self.assertIn(self.oh_351_ta2_approved.id, ids)
        self.assertNotIn(self.oh_351_ta2_pending.id, ids)

    def test_course_filter_with_no_matches_returns_empty(self):
        self.assertEqual(getApprovedOfficeHours(course_filter=999), [])

        # filter by staff

    def test_staff_filter_returns_only_that_staff(self):
        result = getApprovedOfficeHours(staff_filter="ta1@uwm.edu")
        for oh in result:
            self.assertEqual(oh.getStaff().getEmail(), "ta1@uwm.edu")
        self.assertEqual(len(result), 1)

    def test_staff_filter_excludes_pending(self):
        ids = [oh.getId() for oh in
               getApprovedOfficeHours(staff_filter="ta2@uwm.edu")]
        self.assertIn(self.oh_351_ta2_approved.id, ids)
        self.assertNotIn(self.oh_351_ta2_pending.id, ids)

    def test_staff_filter_with_unknown_email_returns_empty(self):
        self.assertEqual(
            getApprovedOfficeHours(staff_filter="nope@uwm.edu"), [])

        # combined filters

    def test_combined_filters_intersect(self):
        result = getApprovedOfficeHours(
            course_filter=361, staff_filter="ta1@uwm.edu")
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].getId(), self.oh_361_ta1.id)

    def test_combined_filters_can_yield_zero(self):
        self.assertEqual(
            getApprovedOfficeHours(
                course_filter=351, staff_filter="ta1@uwm.edu"),
            [])
