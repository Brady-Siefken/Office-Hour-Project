from django.test import TestCase, Client
from scheduler_app.models import *
from classes import UserDatabase


#As an administrator, I want to be able to create new staff accounts so they than reliably meet with
#students
class TestCreateStaff(TestCase):
    monkey = None

    def setUp(self):
        self.monkey = Client()

        # Create admin user and add them to the Administrators table
        UserDatabase.createUser("admin@gmail.com","Test","Admin Doe", "ADMIN")
        UserDatabase.createUser("instruct@gmail.com","Test","Instruct Doe", "INSTRUCTOR")
        UserDatabase.createUser("ta@gmail.com","Test","TA Doe", "TA")

        # Log in as admin
        self.monkey.post("/", {
            'email': 'admin@gmail.com',
            'password': 'Test',
        },follow=True)

    def test_new_ta_success(self):
        self.monkey.post("/admin/users/", {
            'email': 'new@gmail.com',
            'password': 'New',
            'name': 'TA Doe',
            'user_role': 'TA'
        })

        self.assertIsNotNone(UserDatabase.getUser("new@gmail.com"), "Valid TA not created")

    def test_duplicate_ta(self):
        self.monkey.post("/admin/users/", {
            'email': 'ta@gmail.com',
            'password': 'Test',
            'name': 'TA Doe',
            'user_role': 'TA'
        })

        self.assertEqual(len(User.objects.filter(user_role="TA")), 1, "Added duplicate TA to database")

    def test_new_instrucctor_success(self):
        self.monkey.post("/admin/users/", {
            'email': 'new@gmail.com',
            'password': 'New',
            'name': 'Instructor Doe',
            'user_role': 'INSTRUCCTOR'
        })

        self.assertIsNotNone(UserDatabase.getUser("new@gmail.com"), "Valid Instructor not created")

    def test_duplicate_instructor(self):
        self.monkey.post("/admin/users/", {
            'email': 'instruct@gmail.com',
            'password': 'Test',
            'name': 'TA Doe',
            'user_role': 'INSTRUCTOR'
        })

        self.assertEqual(len(User.objects.filter(user_role="INSTRUCTOR")), 1, "Added duplicate TA to database")
