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

########################################################################################

class ProposeOfficeHoursTests(TestCase):
    monkey = None
    TAs = []
    OfficeHours = []
    Lectures = []
    def setUp(self):
        self.monkey = Client()

        # Create users using models.User
        self.TAs[{
            'id': '0',
            'name': 'TA',
            'username': 'ta1',
            'password': 'password123',
            'email': 'TA@test.com'
        }]

        # Create lecture
        self.lectures = [{
            'id': '0',
            'course_name': 'test_course',
            'instructors': '1',
            'time': '10:00-11:00AM',
            'instructor_office_hours': 'W 1:00-2:00PM',
            'TAs': '1',
            'TA_office_hours': 'NULL'
        }]

        self.monkey.post("/login/", {
            'username': 'ta1',
            'password': 'password123',
        }, follow=True)

    def test_successful_proposal(self):
        response = self.client.post("/ta/office-hours/propose/", {
            "lecture": 'lectures[0]',
            "day_of_week": "Mon",
            "start_time": "1:00PM",
            "end_time": "3:00PM",
            "location": "Room 101"
        })

        self.assertEqual([{
            'id': '0',
            'course_name': 'test_course',
            'instructors': '1',
            'time': '10:00-11:00AM',
            'instructor_office_hours': 'W 1:00-2:00PM',
            'TAs': '1',
            'TA_office_hours': 'NULL'
        }], response.context["OfficeHours"], "Unsuccessful Proposal added to OfficeHours database")


    def test_time_conflict(self):
        OfficeHours = [{
            "lecture": 'lectures[0]',
            "day_of_week": "Mon",
            "start_time": "1:00PM",
            "end_time": "3:00PM",
            "location": "Room 101"
        }]

        response = self.client.post("/ta/office-hours/propose/", {
            "lecture": 'lectures[0]',
            "day_of_week": "Mon",
            "start_time": "1:00PM",
            "end_time": "3:00PM",
            "location": "Room 101"
        })

        self.assertEqual(response.context["OfficeHours"].count(), 1)

    def test_invalid_form(self):
        response = self.client.post("/ta/office-hours/propose/", {
            "lecture": "",
            "day_of_week": "Mon",
            "start_time": "",
            "end_time": "11:00",
            "location": "Room 101"
        })

        self.assertEqual(response.context["OfficeHours"].count(), 0)