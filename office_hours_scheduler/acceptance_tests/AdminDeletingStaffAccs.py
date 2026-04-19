from django.test import TestCase, Client
from django.contrib.auth.models import User
from .models import Instructor, TA, Student, Lecture


class ManageUsersViewTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.admin_user = User.objects.create_user(
            username = 'admin1', password = 'adminpass'
        )
        Instructor.objects.create(user=self.admin_user)
        self.client.login(username = 'admin1', password = 'adminpass')

        self.ta_user = User.objects.create_user(
            username = 'ta1', password = 'tapass'
        )
        self.ta = TA.objects.create(user=self.ta_user)
    class Meta:
        app_label = 'scheduler_app'

    #  Staff roster shows all staff alphabetically
    def test_staff_roster(self):
        response = self.client.get('/admin/users/')

        self.assertEqual(response.status_code, 200)
        ta_list = list(response.context['ta_list'].values_list('user__username', flat = True))
        instructor_list = list(response.context['instructor_list'].values_list('user__username',  flat=True))
        self.assertEqual(ta_list, sorted(ta_list))
        self.assertEqual(instructor_list, sorted(instructor_list))


    #  Clicking a staff member shows their info and a delete button
    def test_clicking_staff(self):
        response = self.client.get('/admin/users/', {'selected': self.ta.id})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.ta_user.username)
        self.assertContains(response, 'delete account')

    # Confirming deletion removes the account
    def test_confirmed_deletion(self):
        response = self.client.post('/admin/users/', {
            'staff_id': self.ta.id,
            'action': 'delete'
        })

        self.assertRedirects(response, '/admin/users/')
        self.assertFalse(TA.objects.filter(id=self.ta.id).exists())