from classes.UserDB import *
from scheduler_app.models import *
import unittest

class testUserDBEmailExists(unittest.TestCase):
    def setUp(self):
        User.objects.create(name="", email="test@gmail.com", password="")

    def emailExists(self):
        self.assertTrue(self,UserDB.doesUserWithEmailExist("test@gmail.com"))

    def emailDoesntExist(self):
        self.assertFalse(self,UserDB.doesUserWithEmailExist("incorrect@gmail.com"))