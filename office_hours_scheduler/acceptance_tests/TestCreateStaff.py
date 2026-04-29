from django.test import TestCase, Client
from scheduler_app.models import User
from classes.UserDatabase import  getUser, createUser


class TestCreateStaff(TestCase):
    monkey = None

    def setUp(self):
        self.monkey = Client()

        createUser("admin@gmail.com", "Test", "Admin Doe", "ADMIN")
        createUser("instruct@gmail.com", "Test", "Instruct Doe", "INSTRUCTOR")
        createUser("ta@gmail.com", "Test", "TA Doe", "TA")

        session = self.monkey.session
        session['user_id'] = "admin@gmail.com"
        session.save()

    def test_new_ta_success(self):
        self.monkey.post("/admin/users/", {
            'action': 'create',  # ← this is critical
            'email': 'new@gmail.com',
            'password': 'New',
            'name': 'TA Doe',
            'user_type': 'TA'
        })
        new_user = User.objects.filter(email="new@gmail.com").first()
        self.assertIsNotNone(new_user, "Valid TA not created")
        self.assertEqual(new_user.user_type, "TA", "User was not created as a TA")

    def test_duplicate_ta(self):
        self.monkey.post("/admin/users/", {
            'email': 'ta@gmail.com',
            'password': 'Test',
            'name': 'TA Doe',
            'user_type': 'TA'  # changed from user_role
        })
        self.assertEqual(len(User.objects.filter(user_type="TA")), 1, "Added duplicate TA to database")

    def test_new_instructor_success(self):
        self.monkey.post("/admin/users/", {
            'action': 'create',
            'email': 'new@gmail.com',
            'password': 'New',
            'name': 'Instructor Doe',
            'user_type': 'INSTRUCTOR'
        })
        new_user = User.objects.filter(email="new@gmail.com").first()
        self.assertIsNotNone(new_user, "Valid Instructor not created")
        self.assertEqual(new_user.user_type, "INSTRUCTOR", "User was not created as an Instructor")

    def test_duplicate_instructor(self):
        self.monkey.post("/admin/users/", {
            'email': 'instruct@gmail.com',
            'password': 'Test',
            'name': 'Instructor Doe',
            'user_type': 'INSTRUCTOR'  # changed from user_role
        })
        self.assertEqual(len(User.objects.filter(user_type="INSTRUCTOR")), 1, "Added duplicate Instructor to database")