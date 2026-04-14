from django.test import TestCase, Client
from .models import Course as Course
# Create your tests here.

# Name of user story here, also its description can go here while working on it

class TestCreateCourse(TestCase):
    monkey=None
    lectures=[]

    def setUp(self):
        #completed
        self.monkey = Client()
        self.lectures = [ # Initial contents of DB
            {"course_name": "cs 361", "instructor": None, "times": "T Th 9:30-10:20", "instructor_office_hours": "some timeslot"}
        ]

        #fill test database with students
        for i in self.lectures:
            temp = Course(course_name=i["course_name"],instructor=i["instructor"],times=i["times"],instructor_office_hours=i["instructor_office_hours"])
            temp.save()

    def test_create_new_course(self):
        resp = self.monkey.post("/new_course",{"course_name":"cs 351","instructor":None,"times":self.lectures[0]["times"],"instructor_office_hours":"some time slot"},follow=True)
        self.assertEqual(resp.context["error_msg"],"Success!","Unique course couldn't be created")

    def test_create_existing_course(self):
        resp = self.monkey.post("/new_course",{"course_name":self.lectures[0]["course_name"],"instructor":None,"times":self.lectures[0]["times"],"instructor_office_hours":"some time slot"},follow=True)
        self.assertEqual(resp.context["error_msg"],"Class with that name already exists","New course with name already existing was created")
