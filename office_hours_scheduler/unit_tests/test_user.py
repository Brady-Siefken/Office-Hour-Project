import unittest
from scheduler_app.models import User
from classes.Users import UserClass


class TestUserClass(unittest.TestCase):

    def setUp(self):
        User.objects.all().delete()

        self.user = User.objects.create(
            email="test@test.com",
            password="pass",
            name="Test User",
            user_type="INSTRUCTOR"
        )

    # ----------------------------
    # Constructor tests
    # ----------------------------

    def test_constructor_wraps_existing_user(self):
        user = UserClass("test@test.com")
        self.assertEqual(user.getEmail(), "test@test.com")

    def test_constructor_raises_for_missing_user(self):
        with self.assertRaises(ValueError):
            UserClass("missing@test.com")

    def test_constructor_does_not_create_new_user(self):
        with self.assertRaises(ValueError):
            UserClass("missing@test.com")
        self.assertEqual(User.objects.count(), 1)

    # ----------------------------
    # Getter tests
    # ----------------------------

    def test_get_email(self):
        user = UserClass("test@test.com")
        self.assertEqual(user.getEmail(), "test@test.com")

    def test_get_password(self):
        user = UserClass("test@test.com")
        self.assertEqual(user.getPassword(), "pass")

    def test_get_name(self):
        user = UserClass("test@test.com")
        self.assertEqual(user.getName(), "Test User")

    def test_get_type(self):
        user = UserClass("test@test.com")
        self.assertEqual(user.getType(), "INSTRUCTOR")

    # ----------------------------
    # setName tests
    # ----------------------------

    def test_set_name_updates_name(self):
        user = UserClass("test@test.com")
        user.setName("New Name")
        self.assertEqual(user.getName(), "New Name")

    def test_set_name_persists_to_db(self):
        user = UserClass("test@test.com")
        user.setName("New Name")
        user2 = UserClass("test@test.com")
        self.assertEqual(user2.getName(), "New Name")

    # ----------------------------
    # setPassword tests
    # ----------------------------

    def test_set_password_updates_password(self):
        user = UserClass("test@test.com")
        user.setPassword("newpass")
        self.assertEqual(user.getPassword(), "newpass")

    def test_set_password_persists_to_db(self):
        user = UserClass("test@test.com")
        user.setPassword("newpass")
        user2 = UserClass("test@test.com")
        self.assertEqual(user2.getPassword(), "newpass")

    # ----------------------------
    # setEmail tests
    # ----------------------------

    def test_set_email_updates_email(self):
        user = UserClass("test@test.com")
        user.setEmail("new@test.com")
        self.assertEqual(user.getEmail(), "new@test.com")

    def test_set_email_persists_to_db(self):
        user = UserClass("test@test.com")
        user.setEmail("new@test.com")
        user2 = UserClass("new@test.com")
        self.assertEqual(user2.getEmail(), "new@test.com")

    def test_set_email_raises_if_email_already_in_use(self):
        User.objects.create(
            email="other@test.com",
            password="pass",
            name="Other User",
            user_type="TA"
        )
        user = UserClass("test@test.com")
        with self.assertRaises(ValueError):
            user.setEmail("other@test.com")

    def test_set_email_does_not_change_if_already_in_use(self):
        User.objects.create(
            email="other@test.com",
            password="pass",
            name="Other User",
            user_type="TA"
        )
        user = UserClass("test@test.com")
        with self.assertRaises(ValueError):
            user.setEmail("other@test.com")
        self.assertEqual(user.getEmail(), "test@test.com")

    # ----------------------------
    # setType tests
    # ----------------------------

    def test_set_type_updates_type(self):
        user = UserClass("test@test.com")
        user.setType("TA")
        self.assertEqual(user.getType(), "TA")

    def test_set_type_persists_to_db(self):
        user = UserClass("test@test.com")
        user.setType("TA")
        user2 = UserClass("test@test.com")
        self.assertEqual(user2.getType(), "TA")

    def test_set_type_raises_for_invalid_type(self):
        user = UserClass("test@test.com")
        with self.assertRaises(ValueError):
            user.setType("INVALID")

    def test_set_type_does_not_change_if_invalid(self):
        user = UserClass("test@test.com")
        with self.assertRaises(ValueError):
            user.setType("INVALID")
        self.assertEqual(user.getType(), "INSTRUCTOR")

    def test_all_valid_types(self):
        user = UserClass("test@test.com")
        for user_type in ["INSTRUCTOR", "TA", "STUDENT", "ADMIN"]:
            user.setType(user_type)
            self.assertEqual(user.getType(), user_type)

    # ----------------------------
    # String representation
    # ----------------------------

    def test_str_representation(self):
        user = UserClass("test@test.com")
        self.assertEqual(str(user), "Test User")