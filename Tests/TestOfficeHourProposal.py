from django.test import TestCase, Client
from .models import Administrators, Instructors, TAs, Lectures, OfficeHours


class TestOfficeHourProposal(TestCase):
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