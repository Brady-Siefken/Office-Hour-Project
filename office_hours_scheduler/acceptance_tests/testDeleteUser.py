from django.test import TestCase, Client
from scheduler_app.models import User
from classes.UserDatabase import getUser, createUser


class TestDeleteUser(TestCase):
    monkey = None

    def setUp(self):
        self.monkey = Client()

        createUser("admin@gmail.com", "Test", "Admin Doe", "ADMIN")
        createUser("instruct@gmail.com", "Test", "Instruct Doe", "INSTRUCTOR")
        createUser("ta@gmail.com", "Test", "TA Doe", "TA")

        session = self.monkey.session
        session['user_id'] = "admin@gmail.com"
        session.save()

    def test_delete_ta_success(self):
        self.monkey.post("/admin/users/", {
            'action': 'delete',
            'email': 'ta@gmail.com',
        })
        self.assertFalse(User.objects.filter(email="ta@gmail.com").exists(), "TA was not deleted")

    def test_delete_instructor_success(self):
        self.monkey.post("/admin/users/", {
            'action': 'delete',
            'email': 'instruct@gmail.com',
        })
        self.assertFalse(User.objects.filter(email="instruct@gmail.com").exists(), "Instructor was not deleted")

    def test_delete_nonexistent_user(self):
        self.monkey.post("/admin/users/", {
            'action': 'delete',
            'email': 'nonexistent@gmail.com',
        })
        # DB should be unchanged — all 3 original users still present
        self.assertEqual(User.objects.count(), 3, "DB changed when deleting nonexistent user")

    """def test_delete_admin_not_allowed(self):
        self.monkey.post("/admin/users/", {
            'action': 'delete',
            'email': 'admin@gmail.com',
        })
        # Admin should still exist after attempting to delete themselves
        self.assertTrue(User.objects.filter(email="admin@gmail.com").exists(), "Admin was incorrectly deleted")
        """
    def test_delete_student_success(self):
        createUser("student@gmail.com", "Test", "Student Doe", "STUDENT")

        self.monkey.post("/admin/users/", {
            'action': 'delete',
            'email': 'student@gmail.com',
        })

        self.assertFalse(User.objects.filter(email="student@gmail.com").exists(), "Student was not deleted")