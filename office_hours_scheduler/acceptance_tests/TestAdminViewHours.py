from django.test import TestCase, Client
from classes.UserDatabase import createUser
from classes.CourseDatabase import createCourse
from classes.SectionsDatabase import createSection, getSectionsByTA
from classes.OfficeHoursDatabase import createOfficeHour


class TestAdminViewHours(TestCase):
    # Acceptance tests for admin viewing office hours by course or staff member.

    def setUp(self):
        self.client = Client()

        createUser("admin@uwm.edu", "adminpass", "Admin One", "ADMIN")
        createUser("prof@uwm.edu",  "profpass",  "Prof One",  "INSTRUCTOR")
        createUser("ta1@uwm.edu",   "ta1pass",   "TA One",    "TA")
        createUser("ta2@uwm.edu",   "ta2pass",   "TA Two",    "TA")

        createCourse("CS", 361, "Intro to Software Engineering")
        createSection("CS", 361, 1, instructor_email = "prof@uwm.edu", ta_email = "ta1@uwm.edu")

        createCourse("CS", 351, "Data Structures")
        createSection("CS", 351, 1, instructor_email = "prof@uwm.edu", ta_email = "ta2@uwm.edu")

        self.approved_361 = self.create_approved_hour("ta1@uwm.edu", 361)
        self.approved_351 = self.create_approved_hour("ta2@uwm.edu", 351)

    def login_as(self, email):
        session = self.client.session
        session["user_id"] = email
        session.save()

    def create_approved_hour(self, ta_email, course_code):
        sections = getSectionsByTA(ta_email)
        section = next(
            s for s in sections
            if str(s.getCourse().getCourseCode()) == str(course_code)
        )
        days = {"monday": True, "tuesday": False, "wednesday": False,
                "thursday": False, "friday": False}
        oh = createOfficeHour(ta_email, section, "10:00", "11:00", days)
        oh.setApproved(True)
        return oh

    def test_admin_sees_all_office_hours(self):
        self.login_as("admin@uwm.edu")

        response = self.client.get("/office-hours/")
        listed_ids = [h.getId() for h in response.context["ta_office_hours_list"]]

        self.assertIn(self.approved_361.getId(), listed_ids)
        self.assertIn(self.approved_351.getId(), listed_ids)

    def test_filter_by_course(self):
        self.login_as("admin@uwm.edu")

        response = self.client.get("/office-hours/?lecture=361")
        listed_ids = [h.getId() for h in response.context["ta_office_hours_list"]]

        self.assertIn(self.approved_361.getId(), listed_ids)
        self.assertNotIn(self.approved_351.getId(), listed_ids)

    def test_filter_by_staff(self):
        self.login_as("admin@uwm.edu")

        response = self.client.get("/office-hours/?ta=ta2@uwm.edu")
        listed_ids = [h.getId() for h in response.context["ta_office_hours_list"]]

        self.assertIn(self.approved_351.getId(), listed_ids)
        self.assertNotIn(self.approved_361.getId(), listed_ids)