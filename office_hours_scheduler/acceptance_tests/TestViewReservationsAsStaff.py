from django.test import TestCase, Client
from .models import Reservation, Student as Reservation, Student
# Create your tests here.

# Name of user story here, also its description can go here while working on it

class TestViewReservationsAsStaff(TestCase):
    monkey=None
    students=[]
    reservations=[]
    instructors=[]

    def setUp(self):
        #completed
        self.monkey = Client()
        self.students = [ # Initial contents of DB
            {"name": "nova", "password": "randompasssword", "username": "liminalmushroom", "email": "nova@example.com"},
            {"name": "leo", "password": "differentpassword", "username": "ogaboga", "email": "leo@example.com"},
            {"name": "ben", "password": "anotherpassword", "username": "benjamin", "email": "ben@example.com"}
        ]
        self.reservations = [
            {"office_hours": "something idk", "student": "nova", "timestamp": "W 2:30"},
            {"office_hours": "something idk", "student": "leo", "timestamp": "W 3:00"}
        ]
        self.instructors = [ # Initial contents of DB
            {"name": "rock", "password": "i am rock", "username": "rock", "email": "rock@example.com"}
        ]

        #fill test database with students
        for i in self.students:
            temp = Student(name=i["name"],password=i["password"],username=i["username"],email=i["email"])
            temp.save()
        for i in self.reservations:
            temp = Student(office_hours=i["office_hours"],student=i["student"],timestamp=i["timestamp"])
            temp.save()

    def test_view_reservations(self):
        resp = self.monkey.post("/view_reservations",{"user":"rock"},follow=True)
        self.assertEqual(resp.context["error_msg"],"Success!","Reservations didn't show up")
        matches = 0;
        for i in resp.context["reservations"]:
            for j in self.reservations:
                if(j["student"]==i["student"]): matches+=1
        self.assertEqual(matches,len(self.reservations), "Missing reservations returned")

    
