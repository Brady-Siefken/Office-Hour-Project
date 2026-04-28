from django.test import TestCase, Client
from scheduler_app.models import User

class AdminDeletingStaffTest(TestCase):

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
            name="TA One",
            user_type="TA",
        )
        self.instructor = User.objects.create(
            email="instructor@uwm.edu",
            password="instpass",
            name="Instructor One",
            user_type="INSTRUCTOR",
        )

        # Set the session keys the Home view sets after a real login.
        # The app uses email as user_id, not the auto-generated User.id.
        session = self.client.session
        session["user_id"] = self.admin.email
        session["user_type"] = "ADMIN"
        session.save()

    def test_staff_lists_render(self):
        response = self.client.get("/admin/users/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "TA One")
        self.assertContains(response, "Instructor One")

    def test_staff_member_appears(self):
        response = self.client.get("/admin/users/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.ta.email)
        self.assertContains(response, self.ta.name)

    def test_delete_removes_user(self):
        response = self.client.post("/admin/users/", {
            "action": "delete",
            "email": self.ta.email,
        })

        self.assertRedirects(response, "/admin/users/")
        self.assertFalse(User.objects.filter(email=self.ta.email).exists())