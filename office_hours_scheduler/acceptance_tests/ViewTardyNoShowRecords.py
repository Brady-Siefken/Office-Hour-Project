from django.test import TestCase, Client
from .models import Stuff, MyUser


# Create your tests here.

# User Story: View Tardy/No-Show Records
# GIVEN: The user has logged in as an instructor
# WHEN:  The user selects "view courses"
# THEN:  The system shows a list of every course that
#         instructor teaches and their sections
# WHEN:  The user selects a given section
# THEN:  The system displays an alphabetically sorted list of
#         every student in that section, with number of tardies
#         and number of no shows alongside names
# WHEN:  The user selects a given student
# THEN:  The system shows all tardy and no show reports for
#         that student for that section

class ViewTardyNoShowRecordsTests(TestCase):

    def setUp(self):
        self.client = Client()

        self.instructor_user = User.objects.create_user(username='instructor2', password='password123')

        Instructor.objects.create(user=self.instructor_user)

        self.lecture = Lecture.objects.create(course_name='CS361', instructor=self.instructor_user)

        for name in ['Charlie', 'Alice', 'Bob']:
            u = User.objects.create_user(username=name.lower(), password='password123')
            s = Student.objects.create(user=u, name=name)
            Reservation.objects.create(student=s, course=self.lecture, status='completed', tardy=True, no_show=False)

# Test 2a: Instructor sees the student list on the report page
def test_instructor_sees_course_list(self):
    self.client.login(username='instructor2', password='password123')

    response = self.client.get(reverse('tardy-noshow'))

    self.assertEqual(response.status_code, 200)
    self.assertIn('tardy_noshow_student_list', response.context)

# Test 2b: Student list within a section is alphabetically sorted
def test_student_list_is_alphabetically_sorted(self):
    self.client.login(username='instructor2', password='password123')

    response = self.client.get(
        reverse('tardy-noshow'),
        {'lecture_filter': self.lecture.pk}
    )

    self.assertEqual(response.status_code, 200)
    names = [s.name for s in response.context['tardy_noshow_student_list']]
    self.assertEqual(names, sorted(names))

# Test 2c: Tardy and no-show counts appear for each student
def test_tardy_counts_present_for_each_student(self):
    self.client.login(username='instructor2', password='password123')

    response = self.client.get(
        reverse('tardy-noshow'),
        {'lecture_filter': self.lecture.pk}
    )

    self.assertEqual(response.status_code, 200)
    for student in response.context['tardy_noshow_student_list']:
        self.assertIn('tardy_count', student)
        self.assertIn('noshow_count', student)