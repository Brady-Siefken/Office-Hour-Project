from django.test import TestCase
from classes.TimeSlot import TimeSlot
from classes import UserDatabase, CourseDatabase, SectionsDatabase, OfficeHoursDatabase


class TestStudentViewOfficeHours(TestCase):
    def setUp(self):
        # Given: Two TAs, two courses, and approved office hours in the system
        UserDatabase.createUser(
            email="rock@uwm.edu",
            password="password123",
            name="Rock",
            user_type="TA"
        )
        UserDatabase.createUser(
            email="boyland@uwm.edu",
            password="password123",
            name="Boyland",
            user_type="TA"
        )

        CourseDatabase.createCourse("CS", 361, "Software Engineering")
        CourseDatabase.createCourse("CS", 351, "Data Structures")

        SectionsDatabase.createSection(
            department_name="CS",
            course_code=361,
            section_code=401,
            ta_email="rock@uwm.edu",
            section_type="LECTURE"
        )
        SectionsDatabase.createSection(
            department_name="CS",
            course_code=351,
            section_code=401,
            ta_email="boyland@uwm.edu",
            section_type="LECTURE"
        )

        tuesday_1200 = TimeSlot.DAY_BITS["Tuesday"] | (720 << TimeSlot.MINUTES_SHIFT) | (60 << TimeSlot.LENGTH_SHIFT)
        tuesday_1215 = TimeSlot.DAY_BITS["Tuesday"] | (735 << TimeSlot.MINUTES_SHIFT) | (60 << TimeSlot.LENGTH_SHIFT)
        friday_0930  = TimeSlot.DAY_BITS["Friday"]  | (570 << TimeSlot.MINUTES_SHIFT) | (60 << TimeSlot.LENGTH_SHIFT)

        self.oh1_id = OfficeHoursDatabase.createOfficeHour("rock@uwm.edu",    361, tuesday_1200, approved=True)
        self.oh2_id = OfficeHoursDatabase.createOfficeHour("rock@uwm.edu",    361, tuesday_1215, approved=True)
        self.oh3_id = OfficeHoursDatabase.createOfficeHour("boyland@uwm.edu", 351, friday_0930,  approved=True)

    def test_student_sees_approved_office_hours_for_a_specific_course(self):
        # When: The student filters approved office hours by course 361
        sessions = OfficeHoursDatabase.getApprovedOfficeHours(course_filter=361)

        # Then: Exactly 2 sessions are returned
        self.assertEqual(
            len(sessions), 2,
            "Student should see exactly 2 approved office hour sessions for CS 361"
        )

        # And: Every returned session belongs to CS 361
        for session in sessions:
            self.assertEqual(
                session.getCourse().getCourseCode(), 361,
                "All returned sessions should belong to CS 361"
            )

    def test_student_sees_approved_office_hours_for_a_specific_ta(self):
        # When: The student filters approved office hours by TA
        sessions = OfficeHoursDatabase.getApprovedOfficeHours(staff_filter="rock@uwm.edu")

        self.assertEqual(
            len(sessions), 2,
            "Student should see exactly 2 approved office hour sessions for Rock"
        )

        for session in sessions:
            self.assertEqual(
                session.getStaff().getEmail(), "rock@uwm.edu",
                "All returned sessions should belong to Rock"
            )

    def test_student_sees_all_approved_office_hours_with_no_filter(self):
        # When: The student retrieves all approved office hours
        sessions = OfficeHoursDatabase.getApprovedOfficeHours()

        # Then: All 3 sessions are returned
        self.assertEqual(
            len(sessions), 3,
            "Student should see all 3 approved office hour sessions"
        )

    def test_student_sees_no_results_for_a_course_with_no_office_hours(self):
        # When: The student filters by a course with no office hours
        sessions = OfficeHoursDatabase.getApprovedOfficeHours(course_filter=101)

        # Then: No sessions are returned
        self.assertEqual(
            sessions, [],
            "Student should see no office hour sessions for a course with none scheduled"
        )

    def test_student_sees_office_hours_on_a_specific_day(self):
        # When: The student retrieves all approved sessions and filters by Tuesday
        all_sessions = OfficeHoursDatabase.getApprovedOfficeHours()
        tuesday_sessions = [s for s in all_sessions if TimeSlot(s.getTimeslot()).getTuesday()]

        self.assertEqual(
            len(tuesday_sessions), 2,
            "Student should see exactly 2 approved office hour sessions on Tuesday"
        )

        for session in tuesday_sessions:
            self.assertTrue(
                TimeSlot(session.getTimeslot()).getTuesday(),
                "All returned sessions should be on Tuesday"
            )

    def test_student_sees_no_results_on_a_day_with_no_office_hours(self):
        # When: The student filters all approved sessions by Sunday
        all_sessions = OfficeHoursDatabase.getApprovedOfficeHours()
        sunday_sessions = [s for s in all_sessions if TimeSlot(s.getTimeslot()).getSunday()]

        self.assertEqual(
            sunday_sessions, [],
            "Student should see no approved office hour sessions on Sunday"
        )