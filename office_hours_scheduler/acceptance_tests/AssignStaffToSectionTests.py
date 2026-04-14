from django.test import TestCase, Client
from django.contrib.auth.models import User
from .models import Instructor, TA, Student, Lecture

class AssignStaffToSectionTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.admin_user = User.objects.create_user(
            username='admin1', password= 'adminpass'
        )
        Instructor.objects.create(user=self.admin_user)
        self.client.login(username= 'admin1', password = 'adminpass')

        self.lecture = Lecture.objects.create(
            course_name='CS361', semester='Spring 26'
        )
        self.ta_user = User.objects.create_user(
            username='ta1', password='TApass'
        )
        self.ta = TA.objects.create(user=self.ta_user)
    # Admin sees list of all courses
    def test_view_courses(self):
        response = self.client.get('/admin/lectures/')
        self.assertEqual(response.status_code, 200)
        self.assertIn('lecture_list', response.context)
        self.assertContains(response, 'CS101')

    # : Selecting a course shows all sections and assigned staff
    def test_selecting_course(self):
        response = self.client.get('/admin/lectures/', {'selected': self.lecture.id})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'C361')
        self.assertIn('ta_list', response.context)
        self.assertIn('instructor_list', response.context)

    # Adding a non-duplicate non-conflicting staff adds them to the section
    def test_adding_valid_staff(self):
        response = self.client.post('/admin/lectures/', {
            'lecture_id': self.lecture.id,
            'ta_id': self.ta.id,
            'action': 'assign'
        })
        self.assertRedirects(response, '/admin/lectures/')
        self.assertTrue(
            self.lecture.tas.filter(id=self.ta.id).exists()
        )

    # Adding staff already in that section shows already present message
    def test_adding_duplicate_staff_shows_already_present_message(self):
        self.lecture.tas.add(self.ta)
        response = self.client.post('/admin/lectures/', {
            'lecture_id': self.lecture.id,
            'ta_id': self.ta.id,
            'action': 'assign'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'already')

    # Adding staff with conflicting assignment shows conflict message
    def test_adding_conflicting_staff_shows_conflict_message(self):
        conflicting_lecture = Lecture.objects.create(
            course_name='CS102', semester='Fall 2025',
            time='MWF 9-10AM'
        )
        conflicting_lecture.tas.add(self.ta)
        self.lecture.time = 'MWF 9-10AM'
        self.lecture.save()

        response = self.client.post('/admin/lectures/', {
            'lecture_id': self.lecture.id,
            'ta_id': self.ta.id,
            'action': 'assign'
        })

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'conflict')