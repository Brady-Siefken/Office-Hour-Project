from django.test import TestCase, Client
from scheduler_app.models import (User, Department, Course, Section,)

class TestInstructorCreatingStudents(TestCase):

    def setUp(self):
        self.client = Client()

        self.department = Department.objects.create(departmentName="COMPSCI")
        self.course = Course.objects.create(
            department=self.department, courseCode=361, courseName="Intro SE",
        )
        self.instructor = User.objects.create(
            email="prof@uwm.edu", password="x",
            name="Dr Prof", user_type="INSTRUCTOR",
        )
        self.ta = User.objects.create(
            email="ta@uwm.edu", password="x",
            name="Test TA", user_type="TA",
        )
        self.section = Section.objects.create(
            course=self.course, sectionCode=101,
            instructor=self.instructor, ta=self.ta,
        )

        session = self.client.session
        session["user_id"] = self.instructor.email
        session["user_type"] = "INSTRUCTOR"
        session.save()

    def test_add_students_page_loads(self):
        response = self.client.get("/instructor/add-students/")
        self.assertEqual(response.status_code, 200)

    def test_adding_students_creates_users(self):
        self.client.post(
            "/instructor/add-students/",
            {
                "department_name": "COMPSCI",
                "course_code": "361",
                "section_code": "101",
                "students_text": "alice@uwm.edu, Alice Smith\nbob@uwm.edu, Bob Jones",
            },
        )
        self.assertTrue(User.objects.filter(email="alice@uwm.edu").exists())
        self.assertTrue(User.objects.filter(email="bob@uwm.edu").exists())

    def test_added_students_are_enrolled(self):
        self.client.post(
            "/instructor/add-students/",
            {
                "department_name": "COMPSCI",
                "course_code": "361",
                "section_code": "101",
                "students_text": "alice@uwm.edu, Alice Smith",
            },
        )
        alice = User.objects.get(email="alice@uwm.edu")
        self.assertIn(alice, self.section.students.all())

    def test_non_instructor_blocked(self):
        session = self.client.session
        session["user_id"] = self.ta.email
        session["user_type"] = "TA"
        session.save()
        response = self.client.get("/instructor/add-students/")
        self.assertRedirects(response, "/")