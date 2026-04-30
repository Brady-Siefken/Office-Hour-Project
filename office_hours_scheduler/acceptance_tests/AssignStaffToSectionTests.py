from django.test import TestCase, Client
from classes.UserDatabase import createUser
from classes.CourseDatabase import createCourse
from classes.SectionsDatabase import createSection, getSection


class AssignStaffToSectionTest(TestCase):
    # Acceptance tests for admin assigning staff to sections.

    def setUp(self):
        self.client = Client()

        createUser("admin@uwm.edu", "adminpass", "Admin One",  "ADMIN")
        createUser("prof@uwm.edu",  "profpass",  "Prof One",   "INSTRUCTOR")
        createUser("ta@uwm.edu",    "tapass",    "TA One",     "TA")

        createCourse("CS", 361, "Intro to Software Engineering")
        createSection("CS", 361, 1)

    def login_as(self, email):
        session = self.client.session
        session["user_id"] = email
        session["user_type"] = "ADMIN"
        session.save()

    def test_manage_courses_page_renders(self):
        self.login_as("admin@uwm.edu")

        response = self.client.get("/admin/courses/")

        self.assertEqual(response.status_code, 200)
        self.assertIn("course_list", response.context)
        self.assertIn("instructor_list", response.context)
        self.assertIn("ta_list", response.context)
        self.assertContains(response, "CS")
        self.assertContains(response, "361")

    def test_assigning_instructor_to_section(self):
        self.login_as("admin@uwm.edu")

        self.client.post("/admin/courses/", {
            "action": "assign_instructor",
            "department_name": "CS",
            "course_code": 361,
            "section_code": 1,
            "instructor_email": "prof@uwm.edu",
        })

        section = getSection("CS", 361, 1)
        self.assertEqual(section.getInstructor(), "Prof One")

    def test_assigning_ta_to_section(self):
        self.login_as("admin@uwm.edu")

        self.client.post("/admin/courses/", {
            "action": "assign_ta",
            "department_name": "CS",
            "course_code": 361,
            "section_code": 1,
            "ta_email": "ta@uwm.edu",
        })

        section = getSection("CS", 361, 1)
        self.assertEqual(section.getTA(), "TA One")