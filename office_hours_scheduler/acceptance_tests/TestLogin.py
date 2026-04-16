from django.test import TestCase, Client
from office_hours_scheduler.scheduler_app.models import InstructorUser as Instructor
from office_hours_scheduler.scheduler_app.models import AssistantUser as Assistant
from office_hours_scheduler.scheduler_app.models import AdminUser as Admin
from office_hours_scheduler.scheduler_app.models import StudentUser as Student
# Create your tests here.

# Name of user story here, also its description can go here while working on it

class TestStudentLogin(TestCase):
    monkey=None
    students=[]

    def setUp(self):
        #completed
        self.monkey = Client()
        self.students = [ # Initial contents of DB
            {"name": "nova", "password": "randompasssword", "username": "liminalmushroom", "email": "nova@example.com"},
            {"name": "leo", "password": "differentpassword", "username": "ogaboga", "email": "leo@example.com"},
            {"name": "ben", "password": "anotherpassword", "username": "benjamin", "email": "ben@example.com"}
        ]

        #fill test database with students
        for i in self.students:
            temp = Student(name=i["name"],password=i["password"],username=i["username"],email=i["email"])
            temp.save()

    def test_login_via_email(self):
        for i in self.students:
            resp = self.monkey.post("/",{"username":i["email"],"password":i["password"]},follow=True)
            self.assertEqual(resp.context["name"],i["name"],"Name should be passed as part of successful login via email")

    def test_login_via_username(self):
        for i in self.students:
            resp = self.monkey.post("/",{"username":i["username"],"password":i["password"]},follow=True)
            self.assertEqual(resp.context["name"],i["name"],"Name should be passed as part of successful login via username")

    def test_login_incorrect_uname(self):
        for i in self.students:
            resp = self.monkey.post("/",{"username":"not a valid username","password":i["password"]},follow=True)
            self.assertEqual(resp.context["error_msg"],"Username or password not correct","No error message")
    
    def test_login__via_email_incorrect_password(self):
        for i in self.students:
            resp = self.monkey.post("/",{"username":i["email"],"password":"not a valid password"},follow=True)
            self.assertEqual(resp.context["error_msg"],"Username or password not correct","No error message")

    def test_login__via_uname_incorrect_password(self):
        for i in self.students:
            resp = self.monkey.post("/",{"username":i["username"],"password":"not a valid password"},follow=True)
            self.assertEqual(resp.context["error_msg"],"Username or password not correct","No error message")


class TestAssistantLogin(TestCase):
    monkey=None
    assistants=[]

    def setUp(self):
        #completed
        self.monkey = Client()
        self.assistants = [ # Initial contents of DB
            {"name": "nova", "password": "randompasssword", "username": "liminalmushroom", "email": "nova@example.com"},
            {"name": "leo", "password": "differentpassword", "username": "ogaboga", "email": "leo@example.com"},
            {"name": "ben", "password": "anotherpassword", "username": "benjamin", "email": "ben@example.com"}
        ]

        #fill test database with the TAs
        for i in self.assistants:
            temp = Assistant(name=i["name"],password=i["password"],username=i["username"],email=i["email"])
            temp.save()

    def test_login_via_email(self):
        for i in self.assistants:
            resp = self.monkey.post("/",{"username":i["email"],"password":i["password"]},follow=True)
            self.assertEqual(resp.context["name"],i["name"],"Name should be passed as part of successful login via email")

    def test_login_via_username(self):
        for i in self.assistants:
            resp = self.monkey.post("/",{"username":i["username"],"password":i["password"]},follow=True)
            self.assertEqual(resp.context["name"],i["name"],"Name should be passed as part of successful login via username")

    def test_login_incorrect_uname(self):
        for i in self.assistants:
            resp = self.monkey.post("/",{"username":"not a valid username","password":i["password"]},follow=True)
            self.assertEqual(resp.context["error_msg"],"Username or password not correct","No error message")
    
    def test_login__via_email_incorrect_password(self):
        for i in self.assistants:
            resp = self.monkey.post("/",{"username":i["email"],"password":"not a valid password"},follow=True)
            self.assertEqual(resp.context["error_msg"],"Username or password not correct","No error message")

    def test_login__via_uname_incorrect_password(self):
        for i in self.assistants:
            resp = self.monkey.post("/",{"username":i["username"],"password":"not a valid password"},follow=True)
            self.assertEqual(resp.context["error_msg"],"Username or password not correct","No error message")

class TestAdminLogin(TestCase):
    monkey=None
    admins=[]

    def setUp(self):
        #completed
        self.monkey = Client()
        self.admins = [ # Initial contents of DB
            {"name": "nova", "password": "randompasssword", "username": "liminalmushroom", "email": "nova@example.com"},
            {"name": "leo", "password": "differentpassword", "username": "ogaboga", "email": "leo@example.com"},
            {"name": "ben", "password": "anotherpassword", "username": "benjamin", "email": "ben@example.com"}
        ]

        #fill test database with the TAs
        for i in self.admins:
            temp = Admin(name=i["name"],password=i["password"],username=i["username"],email=i["email"])
            temp.save()

    def test_login_via_email(self):
        for i in self.admins:
            resp = self.monkey.post("/",{"username":i["email"],"password":i["password"]},follow=True)
            self.assertEqual(resp.context["name"],i["name"],"Name should be passed as part of successful login via email")

    def test_login_via_username(self):
        for i in self.admins:
            resp = self.monkey.post("/",{"username":i["username"],"password":i["password"]},follow=True)
            self.assertEqual(resp.context["name"],i["name"],"Name should be passed as part of successful login via username")

    def test_login_incorrect_uname(self):
        for i in self.admins:
            resp = self.monkey.post("/",{"username":"not a valid username","password":i["password"]},follow=True)
            self.assertEqual(resp.context["error_msg"],"Username or password not correct","No error message")
    
    def test_login__via_email_incorrect_password(self):
        for i in self.admins:
            resp = self.monkey.post("/",{"username":i["email"],"password":"not a valid password"},follow=True)
            self.assertEqual(resp.context["error_msg"],"Username or password not correct","No error message")

    def test_login__via_uname_incorrect_password(self):
        for i in self.admins:
            resp = self.monkey.post("/",{"username":i["username"],"password":"not a valid password"},follow=True)
            self.assertEqual(resp.context["error_msg"],"Username or password not correct","No error message")

class TestInstructorLogin(TestCase):
    monkey=None
    instructors=[]

    def setUp(self):
        #completed
        self.monkey = Client()
        self.instructors = [ # Initial contents of DB
            {"name": "nova", "password": "randompasssword", "username": "liminalmushroom", "email": "nova@example.com"},
            {"name": "leo", "password": "differentpassword", "username": "ogaboga", "email": "leo@example.com"},
            {"name": "ben", "password": "anotherpassword", "username": "benjamin", "email": "ben@example.com"}
        ]

        #fill test database with the TAs
        for i in self.instructors:
            temp = Instructor(name=i["name"],password=i["password"],username=i["username"],email=i["email"])
            temp.save()

    def test_login_via_email(self):
        for i in self.instructors:
            resp = self.monkey.post("/",{"username":i["email"],"password":i["password"]},follow=True)
            self.assertEqual(resp.context["name"],i["name"],"Name should be passed as part of successful login via email")

    def test_login_via_username(self):
        for i in self.instructors:
            resp = self.monkey.post("/",{"username":i["username"],"password":i["password"]},follow=True)
            self.assertEqual(resp.context["name"],i["name"],"Name should be passed as part of successful login via username")

    def test_login_incorrect_uname(self):
        for i in self.instructors:
            resp = self.monkey.post("/",{"username":"not a valid username","password":i["password"]},follow=True)
            self.assertEqual(resp.context["error_msg"],"Username or password not correct","No error message")
    
    def test_login__via_email_incorrect_password(self):
        for i in self.instructors:
            resp = self.monkey.post("/",{"username":i["email"],"password":"not a valid password"},follow=True)
            self.assertEqual(resp.context["error_msg"],"Username or password not correct","No error message")

    def test_login__via_uname_incorrect_password(self):
        for i in self.instructors:
            resp = self.monkey.post("/",{"username":i["username"],"password":"not a valid password"},follow=True)
            self.assertEqual(resp.context["error_msg"],"Username or password not correct","No error message")