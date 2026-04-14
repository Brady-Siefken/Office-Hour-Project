from django.test import TestCase, Client
from .models import Stuff, MyUser


# Create your tests here.

# User Story: Record Tardy/No-Show
# "As an instructor or TA, I want to be able to record
#  tardy/no show behavior from students so that I can ask
#  later what happened."
#
# GIVEN: The user has logged in as an instructor or TA
# WHEN:  The user selects "record tardy or no show for
#         current reserved time"
# THEN:  The system adds a record of that time and the
#         student's tardy/no show behavior to that student's
#         record

class RecordTardyNoShowTests(TestCase):

    def setUp(self):
        self.client = Client()

        self.ta_user = User.objects.create_user(username='ta_test', password='password123')

        TA.objects.create(user=self.ta_user)

        self.instructor_user = User.objects.create_user(username='instructor_test', password='password123')

        Instructor.objects.create(user=self.instructor_user)

        self.student_user = User.objects.create_user(username='student_test', password='password123')

        self.student = Student.objects.create(user=self.student_user)

        self.lecture = Lecture.objects.create(course_name='CS361', instructor=self.instructor_user)

        self.reservation = Reservation.objects.create(student=self.student, course=self.lecture, status='completed')

    # Test 1a: A TA can successfully record a tardy
    def test_ta_can_record_tardy(self):
        self.client.login(username='ta_test', password='password123')

        response = self.client.post(
            reverse('tardy-noshow'),
            {
                'reserved_id': self.reservation.pk,
                'tardy': True,
                'no_show': False,
            }
        )

        self.assertRedirects(response, '/staff/tardy-report/')
        self.reservation.refresh_from_db()
        self.assertTrue(self.reservation.tardy)
        self.assertFalse(self.reservation.no_show)

    # Test 1b: An instructor can successfully record a no-show
    def test_instructor_can_record_no_show(self):
        self.client.login(username='instructor_test', password='password123')

        response = self.client.post(
            reverse('tardy-noshow'),
            {
                'reserved_id': self.reservation.pk,
                'tardy': False,
                'no_show': True,
            }
        )

        self.assertRedirects(response, '/staff/tardy-report/')
        self.reservation.refresh_from_db()
        self.assertFalse(self.reservation.tardy)
        self.assertTrue(self.reservation.no_show)

    # Test 1c: A student cannot access the tardy recording page
    def test_student_cannot_record_tardy(self):
        self.client.login(username='student_test', password='password123')

        response = self.client.post(
            reverse('tardy-noshow'),
            {
                'reserved_id': self.reservation.pk,
                'tardy': True,
                'no_show': False,
            }
        )

        self.assertNotEqual(response.status_code, 200)

    # Test 1d: An unauthenticated user cannot record tardy
    def test_unauthenticated_user_cannot_record_tardy(self):
        response = self.client.post(
            reverse('tardy-noshow'),
            {
                'reserved_id': self.reservation.pk,
                'tardy': True,
                'no_show': False,
            }
        )

        self.assertRedirects(response, '/login/?next=/staff/tardy-report/')
