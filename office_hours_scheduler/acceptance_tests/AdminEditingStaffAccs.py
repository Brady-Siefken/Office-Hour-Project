from django.test import TestCase, Client
from scheduler_app.models import User

class AdminEditingStaffTest(TestCase):

    def setUp(self):
        self.client = Client()

        self.admin = User.objects.create(
            email="admin@uwm.edu",
            password="adminpass",
            name="Admin One",
            user_type="ADMIN",
        )
        self.ta = User.objects.create(
            email="ta1@uwm.edu",
            password="tapass",
            name="TA Original",
            user_type="TA",
        )

        # Log in as admin via the same session pattern Home.post uses
        session = self.client.session
        session["user_id"] = self.admin.email
        session["user_type"] = "ADMIN"
        session.save()

    # The manage users page renders for an admin
    def test_manage_users_page_renders(self):
        response = self.client.get("/admin/users/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.ta.email)
        self.assertContains(response, self.ta.name)

    # Editing a staff member updates their name
    def test_edit_updates_name(self):
        response = self.client.post("/admin/users/", {
            "action": "edit",
            "email": self.ta.email,
            "name": "TA Updated",
            "password": "",
            "user_type": "TA",
        })

        self.assertRedirects(response, "/admin/users/")

        self.ta.refresh_from_db()
        self.assertEqual(self.ta.name, "TA Updated")

    # Editing a staff member updates their password
    def test_edit_updates_password(self):
        response = self.client.post("/admin/users/", {
            "action": "edit",
            "email": self.ta.email,
            "name": "",
            "password": "newpass123",
            "user_type": "TA",
        })

        self.assertRedirects(response, "/admin/users/")

        self.ta.refresh_from_db()
        self.assertEqual(self.ta.password, "newpass123")

    # Editing a staff member updates their user type
    def test_edit_updates_user_type(self):
        response = self.client.post("/admin/users/", {
            "action": "edit",
            "email": self.ta.email,
            "name": "",
            "password": "",
            "user_type": "INSTRUCTOR",
        })

        self.assertRedirects(response, "/admin/users/")

        self.ta.refresh_from_db()
        self.assertEqual(self.ta.user_type, "INSTRUCTOR")

    # Editing with an unknown email redirects without crashing
    def test_edit_unknown_email_redirects(self):
        response = self.client.post("/admin/users/", {
            "action": "edit",
            "email": "doesntexist@uwm.edu",
            "name": "Whatever",
            "password": "whatever",
            "user_type": "TA",
        })

        self.assertRedirects(response, "/admin/users/")
        self.assertFalse(
            User.objects.filter(email="doesntexist@uwm.edu").exists()
        )