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

    #  Staff roster shows all staff alphabetically
# Clicking a staff member shows their info and an edit button
def test_clicking_staff(self):
    response = self.client.get('/admin/users/', {'selected': self.ta.id})

    self.assertEqual(response.status_code, 200)
    self.assertContains(response, self.ta_user.username)
    self.assertContains(response, 'edit account')


# Clicking edit shows editable fields and a confirm button
def test_edit_account(self):
    response = self.client.get('/admin/users/', {
        'selected': self.ta.id,
        'action': 'edit'
    })

    self.assertEqual(response.status_code, 200)
    self.assertContains(response, 'name = "username"')
    self.assertContains(response, 'name = "email"')
    self.assertContains(response, 'confirm')


# Confirming updates the staff account with new info
def test_confirm_updates_staff_account(self):
    response = self.client.post('/admin/users/', {
        'staff_id': self.ta.id,
        'action': 'edit',
        'username': 'updated_ta',
        'email': 'updated@example.com',
        'password': 'newpass123',
        'user_type': 'ta'
    })

    self.assertRedirects(response, '/admin/users/')
    self.ta_user.refresh_from_db()
    self.assertEqual(self.ta_user.username, 'updated_ta')
    self.assertEqual(self.ta_user.email, 'updated@wtv.com')