import unittest
from scheduler_app.models import User
from classes.Users import UserClass
from classes.UserDatabase import (
    doesUserWithEmailExist,
    getUser,
    validatePassword,
    getAllUsers,
    getUsersByType,
    countByType,
    createUser,
    deleteUser
)


class TestUserDatabase(unittest.TestCase):

    def setUp(self):
        User.objects.all().delete()

        self.user = User.objects.create(
            email="test@test.com",
            password="pass",
            name="Test User",
            user_type="INSTRUCTOR"
        )

    # ----------------------------
    # doesUserWithEmailExist tests
    # ----------------------------

    def test_does_user_exist_returns_true(self):
        self.assertTrue(doesUserWithEmailExist("test@test.com"))

    def test_does_user_exist_returns_false(self):
        self.assertFalse(doesUserWithEmailExist("missing@test.com"))

    # ----------------------------
    # getUser tests
    # ----------------------------

    def test_get_user_returns_user_class(self):
        user = getUser("test@test.com")
        self.assertIsInstance(user, UserClass)

    def test_get_user_returns_correct_user(self):
        user = getUser("test@test.com")
        self.assertEqual(user.getEmail(), "test@test.com")
        self.assertEqual(user.getName(), "Test User")

    def test_get_user_returns_none_for_missing_user(self):
        user = getUser("missing@test.com")
        self.assertIsNone(user)

    # ----------------------------
    # validatePassword tests
    # ----------------------------

    def test_validate_password_returns_true(self):
        self.assertTrue(validatePassword("test@test.com", "pass"))

    def test_validate_password_returns_false_wrong_password(self):
        self.assertFalse(validatePassword("test@test.com", "wrongpass"))

    def test_validate_password_returns_false_missing_user(self):
        self.assertFalse(validatePassword("missing@test.com", "pass"))

    # ----------------------------
    # getAllUsers tests
    # ----------------------------

    def test_get_all_users_returns_list(self):
        result = getAllUsers()
        self.assertIsInstance(result, list)

    def test_get_all_users_returns_one_user(self):
        result = getAllUsers()
        self.assertEqual(len(result), 1)

    def test_get_all_users_returns_multiple_users(self):
        User.objects.create(
            email="other@test.com",
            password="pass",
            name="Other User",
            user_type="TA"
        )
        result = getAllUsers()
        self.assertEqual(len(result), 2)

    def test_get_all_users_empty(self):
        User.objects.all().delete()
        result = getAllUsers()
        self.assertEqual(len(result), 0)

    def test_get_all_users_returns_user_class_instances(self):
        result = getAllUsers()
        self.assertIsInstance(result[0], UserClass)

    # ----------------------------
    # getUsersByType tests
    # ----------------------------

    def test_get_users_by_type_returns_correct_users(self):
        result = getUsersByType("INSTRUCTOR")
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].getType(), "INSTRUCTOR")

    def test_get_users_by_type_returns_empty_for_missing_type(self):
        result = getUsersByType("TA")
        self.assertEqual(len(result), 0)

    def test_get_users_by_type_filters_correctly(self):
        User.objects.create(
            email="ta@test.com",
            password="pass",
            name="TA User",
            user_type="TA"
        )
        instructors = getUsersByType("INSTRUCTOR")
        tas = getUsersByType("TA")
        self.assertEqual(len(instructors), 1)
        self.assertEqual(len(tas), 1)

    def test_get_users_by_type_raises_for_invalid_type(self):
        with self.assertRaises(ValueError):
            getUsersByType("INVALID")

    # ----------------------------
    # countByType tests
    # ----------------------------

    def test_count_by_type_returns_correct_count(self):
        self.assertEqual(countByType("INSTRUCTOR"), 1)

    def test_count_by_type_returns_zero_for_empty_type(self):
        self.assertEqual(countByType("TA"), 0)

    def test_count_by_type_raises_for_invalid_type(self):
        with self.assertRaises(ValueError):
            countByType("INVALID")

    def test_count_by_type_returns_correct_count_multiple(self):
        User.objects.create(
            email="ta1@test.com",
            password="pass",
            name="TA One",
            user_type="TA"
        )
        User.objects.create(
            email="ta2@test.com",
            password="pass",
            name="TA Two",
            user_type="TA"
        )
        self.assertEqual(countByType("TA"), 2)

    # ----------------------------
    # createUser tests
    # ----------------------------

    def test_create_user_creates_new_user(self):
        createUser("new@test.com", "pass", "New User", "TA")
        self.assertTrue(doesUserWithEmailExist("new@test.com"))

    def test_create_user_raises_if_already_exists(self):
        with self.assertRaises(ValueError):
            createUser("test@test.com", "pass", "Test User", "INSTRUCTOR")

    def test_create_user_raises_for_invalid_type(self):
        with self.assertRaises(ValueError):
            createUser("new@test.com", "pass", "New User", "INVALID")

    def test_create_user_does_not_duplicate(self):
        with self.assertRaises(ValueError):
            createUser("test@test.com", "pass", "Test User", "INSTRUCTOR")
        self.assertEqual(User.objects.filter(email="test@test.com").count(), 1)

    def test_create_user_correct_name(self):
        createUser("new@test.com", "pass", "New User", "TA")
        user = getUser("new@test.com")
        self.assertEqual(user.getName(), "New User")

    def test_create_user_correct_type(self):
        createUser("new@test.com", "pass", "New User", "TA")
        user = getUser("new@test.com")
        self.assertEqual(user.getType(), "TA")

    def test_create_user_all_valid_types(self):
        for i, user_type in enumerate(["INSTRUCTOR", "TA", "STUDENT", "ADMIN"]):
            createUser(f"user{i}@test.com", "pass", f"User {i}", user_type)
            self.assertTrue(doesUserWithEmailExist(f"user{i}@test.com"))

    # ----------------------------
    # deleteUser tests
    # ----------------------------

    def test_delete_user_removes_user(self):
        deleteUser("test@test.com")
        self.assertFalse(doesUserWithEmailExist("test@test.com"))

    def test_delete_user_raises_if_not_exists(self):
        with self.assertRaises(ValueError):
            deleteUser("missing@test.com")

    def test_delete_user_only_deletes_correct_user(self):
        User.objects.create(
            email="other@test.com",
            password="pass",
            name="Other User",
            user_type="TA"
        )
        deleteUser("test@test.com")
        self.assertFalse(doesUserWithEmailExist("test@test.com"))
        self.assertTrue(doesUserWithEmailExist("other@test.com"))