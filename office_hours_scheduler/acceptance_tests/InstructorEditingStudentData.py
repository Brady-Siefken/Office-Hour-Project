from django.test import TestCase, Client
from django.contrib.auth.models import User
from .models import Instructor, TA, Student, Lecture

# OUT OF SCOPE
class InstructorEditStudentTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.instructor_user = User.objects.create_user(
            username = 'instructor1', password = 'instrpass'
        )
        self.instructor = Instructor.objects.create(user=self.instructor_user)
        self.client.login(username = 'instructor1', password = 'instrpass')

        self.lecture = Lecture.objects.create(
            course_name = 'CS361', semester = 'Spring 26',
            instructor = self.instructor
        )
        self.student_user = User.objects.create_user(
            username = 'student1', password = 'studpass',
            email = 'student1@wtv.com'
        )
        self.student = Student.objects.create(
            user = self.student_user, lecture = self.lecture
        )

# Instructor sees list of their classes and sections
def test_instructor_sees_list(self):
    response = self.client.get('/admin/lectures/')
    self.assertEqual(response.status_code, 200)
    lecture_list = list(response.context['lecture_list'].values_list('course_name', flat = True))
    self.assertIn('CS361', lecture_list)

# Clicking a class section shows additional info and view student roster button
def test_clicking_class_section(self):
    response = self.client.get('/admin/lectures/', {'selected': self.lecture.id})
    self.assertEqual(response.status_code, 200)
    self.assertContains(response, 'CS361')
    self.assertContains(response, 'view student roster')


# Clicking view student roster shows all students alphabetically
def test_view_student_roster(self):
    response = self.client.get('/admin/lectures/', {
        'selected': self.lecture.id,
        'action': 'roster'
    })
    self.assertEqual(response.status_code, 200)
    student_list = list(response.context['student_list'].values_list('user_username', flat = True))
    self.assertEqual(student_list, sorted(student_list))


# Clicking a student shows their info and an edit student info button
def test_clicking_student(self):
    response = self.client.get('/admin/lectures/', {
        'selected_student': self.student.id
    })
    self.assertEqual(response.status_code, 200)
    self.assertContains(response, 'student1')
    self.assertContains(response, 'edit student info')


# Clicking edit student info shows all editable fields and confirm button
def test_edit_student_info_shows_fields_and_confirm(self):
    response = self.client.get('/admin/lectures/', {
        'selected_student': self.student.id,
        'action': 'edit'
    })
    self.assertEqual(response.status_code, 200)
    self.assertContains(response, 'name="username"')
    self.assertContains(response, 'name="email"')


self.assertContains(response, 'confirm')


# Confirming updates the student account with new info
def test_confirm_updates_student_info(self):
    response = self.client.post('/admin/lectures/', {
        'selected_student': self.student.id,
        'action': 'edit',
        'username': 'updated_student',
        'email': 'update@wtv.com',
    })


self.assertRedirects(response, '/admin/lectures/')
self.student_user.refresh_from_db()
self.assertEqual(self.student_user.username, 'updated_student')
self.assertEqual(self.student_user.email, 'updated@wtv.com')