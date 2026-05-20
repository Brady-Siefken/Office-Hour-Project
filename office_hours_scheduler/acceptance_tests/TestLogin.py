from django.test import TestCase, Client
from scheduler_app.models import User

class TestAdminLogin(TestCase):
    # tests for admin login .

    def setUp(self):
        self.client = Client()
        self.admin = User.objects.create(
            email = "admin@uwm.edu",
            password = "adminpass",
            name = "Admin",
            user_type = "ADMIN",
        )

    def test_login_redirects_to_admin_dashboard(self):
        response = self.client.post("/", {
            "email": self.admin.email,
            "password": self.admin.password,
        })
        self.assertRedirects(response, "/admin/dashboard/")

    def test_login_sets_session_keys(self):
        self.client.post("/", {
            "email": self.admin.email,
            "password": self.admin.password,
        })
        self.assertEqual(self.client.session["user_id"], self.admin.email)
        self.assertEqual(self.client.session["user_type"], "ADMIN")

    def test_login_unknown_email(self):
        response = self.client.post("/", {
            "email": "nobody@uwm.edu",
            "password": "doesntmatter",
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No such user")

    def test_login_wrong_password(self):
        response = self.client.post("/", {
            "email": self.admin.email,
            "password": "wrongpassword",
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Incorrect password")


class TestInstructorLogin(TestCase):
    # Acceptance tests for instructor login

    def setUp(self):
        self.client = Client()
        self.instructor = User.objects.create(
            email = "instructor@uwm.edu",
            password = "instpass",
            name =  "Instructor One",
            user_type = "INSTRUCTOR",
        )

    def test_login_redirects_to_instructor_dashboard(self):
        response = self.client.post("/", {
            "email": self.instructor.email,
            "password": self.instructor.password,
        })
        self.assertRedirects(response, "/instructor/dashboard/")

    def test_login_sets_session_keys(self):
        self.client.post("/", {
            "email": self.instructor.email,
            "password": self.instructor.password,
        })
        self.assertEqual(self.client.session["user_id"], self.instructor.email)
        self.assertEqual(self.client.session["user_type"], "INSTRUCTOR")

    def test_login_unknown_email(self):
        response = self.client.post("/", {
            "email": "nobody@uwm.edu",
            "password": "doesntmatter",
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No such user")

    def test_login_wrong_password(self):
        response = self.client.post("/", {
            "email": self.instructor.email,
            "password": "wrongpassword",
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Incorrect password")


class TestTALogin(TestCase):
    # Acceptance tests for TA login.

    def setUp(self):
        self.client = Client()
        self.ta = User.objects.create(
            email = "ta@uwm.edu",
            password = "tapass",
            name = "TA One",
            user_type = "TA",
        )

    def test_login_redirects_to_ta_dashboard(self):
        response = self.client.post("/", {
            "email": self.ta.email,
            "password": self.ta.password,
        })
        self.assertRedirects(response, "/ta/dashboard/")

    def test_login_sets_session_keys(self):
        self.client.post("/", {
            "email": self.ta.email,
            "password": self.ta.password,
        })
        self.assertEqual(self.client.session["user_id"], self.ta.email)
        self.assertEqual(self.client.session["user_type"], "TA")

    def test_login_unknown_email(self):
        response = self.client.post("/", {
            "email": "nobody@uwm.edu",
            "password": "doesntmatter",
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No such user")

    def test_login_wrong_password(self):
        response = self.client.post("/", {
            "email": self.ta.email,
            "password": "wrongpassword",
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Incorrect password")
