from django.test import TestCase, Client
import classes.UserDatabase as Users
# Create your tests here.

# Name of user story here, also its description can go here while working on it

class TestStudentLogin(TestCase):
    monkey = Client()
    students=[]
    class Meta:
        app_label = 'scheduler_app'

    def setUp(self):
        #completed
        self.monkey = Client()
        self.students = [ # Initial contents of DB
            {"name": "nova", "password": "randompasssword", "email": "nova@example.com"},
            {"name": "leo", "password": "differentpassword", "email": "leo@example.com"},
            {"name": "ben", "password": "anotherpassword", "email": "ben@example.com"}
        ]

        #fill test database with students
        for i in self.students:
            Users.createUser(i["email"],i["password"],i["name"],"STUDENT")

    def test_login_via_email(self):
        for i in self.students:
            resp = self.monkey.post("/",{"email":i["email"],"password":i["password"]},follow=True)
            self.assertEqual(resp.context["user"].getName(),i["name"],"Name should be passed as part of successful login via email")

    def test_login_incorrect_uname(self):
        for i in self.students:
            resp = self.monkey.post("/",{"email":"not a valid email","password":i["password"]},follow=True)
            self.assertEqual(resp.context["message"],"Username or password not correct","No error message")
    
    def test_login__via_email_incorrect_password(self):
        for i in self.students:
            resp = self.monkey.post("/",{"email":i["email"],"password":"not a valid password"},follow=True)
            self.assertEqual(resp.context["message"],"Username or password not correct","No error message")

class TestAssistantLogin(TestCase):
    monkey=Client()
    assistants=[]

    def setUp(self):
        #completed
        self.monkey = Client()
        self.assistants = [ # Initial contents of DB
            {"name": "nova", "password": "randompasssword", "email": "nova@example.com"},
            {"name": "leo", "password": "differentpassword", "email": "leo@example.com"},
            {"name": "ben", "password": "anotherpassword", "email": "ben@example.com"}
        ]

        #fill test database with the TAs
        for i in self.assistants:
            Users.createUser(i["email"],i["password"],i["name"],"TA")

    def test_login_via_email(self):
        for i in self.assistants:
            resp = self.monkey.post("/home",{"email":i["email"],"password":i["password"]},follow=True)
            self.assertEqual(resp.context["user"].getName(),i["name"],"Name should be passed as part of successful login via email")

    def test_login_incorrect_uname(self):
        for i in self.assistants:
            resp = self.monkey.post("/home",{"email":"not a valid email","password":i["password"]},follow=True)
            self.assertEqual(resp.context["message"],"Username or password not correct","No error message")
    
    def test_login__via_email_incorrect_password(self):
        for i in self.assistants:
            resp = self.monkey.post("/home",{"email":i["email"],"password":"not a valid password"},follow=True)
            self.assertEqual(resp.context["message"],"Username or password not correct","No error message")

class TestAdminLogin(TestCase):
    monkey=Client()
    admins=[]

    def setUp(self):
        #completed
        self.monkey = Client()
        self.admins = [ # Initial contents of DB
            {"name": "nova", "password": "randompasssword", "email": "nova@example.com"},
            {"name": "leo", "password": "differentpassword", "email": "leo@example.com"},
            {"name": "ben", "password": "anotherpassword", "email": "ben@example.com"}
        ]

        #fill test database with the TAs
        for i in self.admins:
            Users.createUser(i["email"],i["password"],i["name"],"ADMIN")

    def test_login_via_email(self):
        for i in self.admins:
            resp = self.monkey.post("/",{"email":i["email"],"password":i["password"]},follow=True)
            self.assertEqual(resp.context["user"].getName(),i["name"],"Name should be passed as part of successful login via email")

    def test_login_incorrect_uname(self):
        for i in self.admins:
            resp = self.monkey.post("/",{"email":"not a valid email","password":i["password"]},follow=True)
            self.assertEqual(resp.context["message"],"Username or password not correct","No error message")
    
    def test_login__via_email_incorrect_password(self):
        for i in self.admins:
            resp = self.monkey.post("/",{"email":i["email"],"password":"not a valid password"},follow=True)
            self.assertEqual(resp.context["message"],"Username or password not correct","No error message")

class TestInstructorLogin(TestCase):
    monkey=Client()
    instructors=[]

    def setUp(self):
        #completed
        self.monkey = Client()
        self.instructors = [ # Initial contents of DB
            {"name": "nova", "password": "randompasssword", "email": "nova@example.com"},
            {"name": "leo", "password": "differentpassword", "email": "leo@example.com"},
            {"name": "ben", "password": "anotherpassword", "email": "ben@example.com"}
        ]

        #fill test database with the TAs
        for i in self.instructors:
            Users.createUser(i["email"],i["password"],i["name"],"INSTRUCTOR")

    def test_login_via_email(self):
        for i in self.instructors:
            resp = self.monkey.post("/",{"email":i["email"],"password":i["password"]},follow=True)
            self.assertEqual(resp.context["user"].getName(),i["name"],"Name should be passed as part of successful login via email")

    def test_login_incorrect_uname(self):
        for i in self.instructors:
            resp = self.monkey.post("/",{"email":"not a valid email","password":i["password"]},follow=True)
            self.assertEqual(resp.context["message"],"Username or password not correct","No error message")
    
    def test_login__via_email_incorrect_password(self):
        for i in self.instructors:
            resp = self.monkey.post("/",{"email":i["email"],"password":"not a valid password"},follow=True)
            self.assertEqual(resp.context["message"],"Username or password not correct","No error message")
