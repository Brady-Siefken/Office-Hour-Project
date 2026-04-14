from django.test import TestCase, Client
from .models import Administrators, Instructors, TAs, Lectures, OfficeHours


#As an administrator, I want to be able to create new staff accounts so they than reliably meet with
#students
class TestCreateStaff(TestCase):
    monkey = None
    admins = []
    instructors = []
    TAs = []
    def setUp(self):
        self.monkey = Client()

        # Create admin user and add them to the Administrators table
        self.admins[{
            'id':'0',
            'name':'Admin',
            'username':'admin1',
            'password':'password123',
            'email':'admin@test.com'
        }]

        # Log in as admin
        self.monkey.post("/login/", {
            'username': 'admin1',
            'password': 'password123',
        },follow=True)


    def test_new_ta_success(self):
        response = self.monkey.post("/admin/users/", {
            'id': '0',
            'username': 'new_ta',
            'email': 'ta@test.com',
            'password': 'pass123',
            'name': 'TA'
        })

        self.assertEquals([{
            'id': '0',
            'username': 'new_ta',
            'email': 'ta@test.com',
            'password': 'pass123',
            'name': 'TA'
        }],response.context["TAs"],"TA not added to TA database")

    def test_duplicate_ta(self):
        response = self.monkey.post("/admin/users/", {
            'id': '0',
            'username': 'new_ta',
            'email': 'ta@test.com',
            'password': 'pass123',
            'name': 'TA'
        })

        response = self.monkey.post("/admin/users/", {
            'id': '0',
            'username': 'new_ta',
            'email': 'ta@test.com',
            'password': 'pass123',
            'name': 'TA'
        })

        self.assertEqual(len(TAs), 1, "Added duplicate TA to database")

    def test_new_instructor_success(self):
        response = self.monkey.post("/admin/users/", {
            'id': '0',
            'username': 'new_instructor',
            'email': 'instructor@test.com',
            'password': 'pass123',
            'name': 'Instructor'
        })

        self.assertEquals([{
            'id': '0',
            'username': 'new_instructor',
            'email': 'instructor@test.com',
            'password': 'pass123',
            'name': 'Instructor'
        }], response.context["Instructors"], "Instructor not added to TA database")

    def test_duplicate_instructor(self):
        response = self.monkey.post("/admin/users/", {
            'id': '0',
            'username': 'new_instructor',
            'email': 'instructor@test.com',
            'password': 'pass123',
            'name': 'Instructor'
        })

        response = self.monkey.post("/admin/users/", {
            'id': '0',
            'username': 'new_instructor',
            'email': 'instructor@test.com',
            'password': 'pass123',
            'name': 'Instructor'
        })

        self.assertEqual(len(Instructors), 1, "Added duplicate instructor to database")

