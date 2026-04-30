"""from django.test import TestCase
from classes import CourseDatabase

class TestCourseDatabaseAcceptance(TestCase):
    def setUp(self):
        CourseDatabase.createCourse("CS", 361, "Software Engineering")

    def test_course_exists_after_creation(self):
        result = CourseDatabase.doesCourseExist("CS", 361)
        self.assertTrue(result)

    def test_course_does_not_exist_if_never_created(self):
        result = CourseDatabase.doesCourseExist("CS", 999)
        self.assertFalse(result)

    def test_get_existing_course_returns_course_object(self):
        course = CourseDatabase.getCourse("CS", 361)
        self.assertIsNotNone(course)

    def test_get_nonexistent_course_returns_none(self):
        course = CourseDatabase.getCourse("CS", 999)
        self.assertIsNone(course)

    def test_get_all_courses_includes_created_course(self):
        courses = CourseDatabase.getAllCourses()
        course_codes = [c.getCourseCode() for c in courses]
        self.assertIn(361, course_codes)

    def test_get_courses_by_department_returns_correct_courses(self):
        CourseDatabase.createCourse("CS", 351, "Data Structures")
        courses = CourseDatabase.getCoursesByDepartment("CS")
        course_codes = [c.getCourseCode() for c in courses]
        self.assertIn(361, course_codes)
        self.assertIn(351, course_codes)

    def test_get_courses_by_wrong_department_returns_empty(self):
        courses = CourseDatabase.getCoursesByDepartment("MATH")
        self.assertEqual(courses, [])

    def test_create_duplicate_course_raises_error(self):
        with self.assertRaises(ValueError):
            CourseDatabase.createCourse("CS", 361, "Software Engineering")

    def test_delete_existing_course_removes_it(self):
        CourseDatabase.deleteCourse("CS", 361)
        self.assertFalse(CourseDatabase.doesCourseExist("CS", 361))

    def test_delete_nonexistent_course_raises_error(self):
        with self.assertRaises(ValueError):
            CourseDatabase.deleteCourse("CS", 999) """

from django.test import TestCase
from classes.TimeSlot import TimeSlot
from classes import UserDatabase, CourseDatabase, SectionsDatabase, OfficeHoursDatabase


class TestInstructorViewOfficeHours(TestCase):
    def setUp(self):
        # Given: An instructor, a TA, a course, a section linking them,
        # and pending office hours awaiting approval
        UserDatabase.createUser(
            email="instructor@uwm.edu",
            password="password123",
            name="Smith",
            user_type="INSTRUCTOR"
        )
        UserDatabase.createUser(
            email="rock@uwm.edu",
            password="password123",
            name="Rock",
            user_type="TA"
        )

        CourseDatabase.createCourse("CS", 361, "Software Engineering")

        SectionsDatabase.createSection(
            department_name="CS",
            course_code=361,
            section_code=401,
            instructor_email="instructor@uwm.edu",
            ta_email="rock@uwm.edu",
            section_type="LECTURE"
        )

        tuesday_1200 = TimeSlot.DAY_BITS["Tuesday"] | (720 << TimeSlot.MINUTES_SHIFT) | (60 << TimeSlot.LENGTH_SHIFT)
        tuesday_1215 = TimeSlot.DAY_BITS["Tuesday"] | (735 << TimeSlot.MINUTES_SHIFT) | (60 << TimeSlot.LENGTH_SHIFT)

        self.oh1_id = OfficeHoursDatabase.createOfficeHour("rock@uwm.edu", 361, tuesday_1200, approved=False)
        self.oh2_id = OfficeHoursDatabase.createOfficeHour("rock@uwm.edu", 361, tuesday_1215, approved=False)

    def test_instructor_sees_all_pending_office_hours_for_their_course(self):
        pending = OfficeHoursDatabase.getPendingOfficeHoursForInstructor("instructor@uwm.edu")

        self.assertEqual(
            len(pending), 2,
            "Instructor should see exactly 2 pending office hour sessions for CS 361"
        )

    def test_instructor_sees_no_pending_hours_for_a_course_they_do_not_teach(self):
        UserDatabase.createUser(
            email="other@uwm.edu",
            password="password123",
            name="Jones",
            user_type="INSTRUCTOR"
        )

        pending = OfficeHoursDatabase.getPendingOfficeHoursForInstructor("other@uwm.edu")

        self.assertEqual(
            pending, [],
            "Instructor should see no pending office hours for courses they do not teach"
        )

    def test_instructor_can_approve_a_pending_office_hour(self):
        OfficeHoursDatabase.approveOfficeHour(self.oh1_id)

        approved = OfficeHoursDatabase.getApprovedOfficeHours(course_filter=361)
        approved_ids = [oh.getId() for oh in approved]
        self.assertIn(
            self.oh1_id, approved_ids,
            "Approved office hour should appear in the approved list"
        )

        pending = OfficeHoursDatabase.getPendingOfficeHoursForInstructor("instructor@uwm.edu")
        self.assertEqual(
            len(pending), 1,
            "Only 1 pending session should remain after approving one"
        )

    def test_instructor_can_reject_a_pending_office_hour(self):
        OfficeHoursDatabase.rejectOfficeHour(self.oh1_id)

        pending = OfficeHoursDatabase.getPendingOfficeHoursForInstructor("instructor@uwm.edu")
        pending_ids = [oh.getId() for oh in pending]
        self.assertNotIn(
            self.oh1_id, pending_ids,
            "Rejected office hour should not appear in pending list"
        )

        approved = OfficeHoursDatabase.getApprovedOfficeHours(course_filter=361)
        approved_ids = [oh.getId() for oh in approved]
        self.assertNotIn(
            self.oh1_id, approved_ids,
            "Rejected office hour should not appear in approved list"
        )

    def test_approve_nonexistent_office_hour_raises_error(self):
        with self.assertRaises(ValueError,
            msg="Approving a nonexistent office hour should raise ValueError"
        ):
            OfficeHoursDatabase.approveOfficeHour(99999)

    def test_reject_nonexistent_office_hour_raises_error(self):
        with self.assertRaises(ValueError,
            msg="Rejecting a nonexistent office hour should raise ValueError"
        ):
            OfficeHoursDatabase.rejectOfficeHour(99999)