from django.test import TestCase, Client
from scheduler_app.models import User
from classes.UserDatabase import getUser, createUser


class TestEditUser(TestCase):
    monkey = None

    def setUp(self):
        self.monkey = Client()

        createUser("admin@gmail.com", "Test", "Admin Doe", "ADMIN")
        createUser("instruct@gmail.com", "Test", "Instruct Doe", "INSTRUCTOR")
        createUser("ta@gmail.com", "Test", "TA Doe", "TA")

        session = self.monkey.session
        session['user_id'] = "admin@gmail.com"
        session.save()

    # --- Edit Name ---

    def test_edit_name_success(self):
        self.monkey.post("/admin/users/", {
            'action': 'edit',
            'email': 'instruct@gmail.com',
            'name': 'New Instructor Name',
        })
        user = User.objects.filter(email="instruct@gmail.com").first()
        self.assertEqual(user.name, "New Instructor Name", "Name was not updated")

    def test_edit_name_empty_no_change(self):
        self.monkey.post("/admin/users/", {
            'action': 'edit',
            'email': 'instruct@gmail.com',
            'name': '',
        })
        user = User.objects.filter(email="instruct@gmail.com").first()
        self.assertEqual(user.name, "Instruct Doe", "Name should not change when empty string is submitted")

    # --- Edit Password ---

    def test_edit_password_success(self):
        self.monkey.post("/admin/users/", {
            'action': 'edit',
            'email': 'ta@gmail.com',
            'password': 'NewPassword123',
        })
        user = User.objects.filter(email="ta@gmail.com").first()
        self.assertEqual(user.password, "NewPassword123", "Password was not updated")

    def test_edit_password_empty_no_change(self):
        self.monkey.post("/admin/users/", {
            'action': 'edit',
            'email': 'ta@gmail.com',
            'password': '',
        })
        user = User.objects.filter(email="ta@gmail.com").first()
        self.assertEqual(user.password, "Test", "Password should not change when empty string is submitted")

    # --- Edit User Type ---

    def test_edit_user_type_success(self):
        self.monkey.post("/admin/users/", {
            'action': 'edit',
            'email': 'ta@gmail.com',
            'user_type': 'INSTRUCTOR',
        })
        user = User.objects.filter(email="ta@gmail.com").first()
        self.assertEqual(user.user_type, "INSTRUCTOR", "User type was not updated")

    def test_edit_user_type_empty_no_change(self):
        self.monkey.post("/admin/users/", {
            'action': 'edit',
            'email': 'ta@gmail.com',
            'user_type': '',
        })
        user = User.objects.filter(email="ta@gmail.com").first()
        self.assertEqual(user.user_type, "TA", "User type should not change when empty string is submitted")

    # --- Edit All Fields Together ---

    def test_edit_all_fields_success(self):
        self.monkey.post("/admin/users/", {
            'action': 'edit',
            'email': 'instruct@gmail.com',
            'name': 'Updated Name',
            'password': 'UpdatedPass',
            'user_type': 'TA',
        })
        user = User.objects.filter(email="instruct@gmail.com").first()
        self.assertEqual(user.name, "Updated Name", "Name was not updated")
        self.assertEqual(user.password, "UpdatedPass", "Password was not updated")
        self.assertEqual(user.user_type, "TA", "User type was not updated")

    # --- Edit Nonexistent User ---

    def test_edit_nonexistent_user_no_crash(self):
        response = self.monkey.post("/admin/users/", {
            'action': 'edit',
            'email': 'ghost@gmail.com',
            'name': 'Ghost',
        })
        self.assertRedirects(response, "/admin/users/", msg_prefix="Should redirect when editing a nonexistent user")

    # --- Permission Check ---

    def test_edit_as_non_admin_redirects(self):
        session = self.monkey.session
        session['user_id'] = "ta@gmail.com"
        session.save()

        response = self.monkey.post("/admin/users/", {
            'action': 'edit',
            'email': 'instruct@gmail.com',
            'name': 'Hacked Name',
        })
        self.assertRedirects(response, "/", msg_prefix="Non-admin should be redirected away")
        user = User.objects.filter(email="instruct@gmail.com").first()
        self.assertEqual(user.name, "Instruct Doe", "Non-admin should not be able to edit users")