from django.test import TestCase, Client
import sys
sys.path.append(__file__.split("/unit_tests")[0])
from classes.TimeSlot import TimeSlot
class TestStudentLogin(TestCase):
    slot:TimeSlot = TimeSlot()
    def setUp(self):
        self.slot.data = 0b110101100111110000000
    def TestSunday(self):
        self.assertFalse(self.slot.getSunday())
    def TestMonday(self):
        self.assertFalse(self.slot.getMonday())
    def TestTuesday(self):
        self.assertFalse(self.slot.getTuesday())
    def TestWednesday(self):
        self.assertFalse(self.slot.getWednesday())
    def TestThursday(self):
        self.assertFalse(self.slot.getThursday())
    def TestFriday(self):
        self.assertFalse(self.slot.getFriday())
    def TestSaturday(self):
        self.assertFalse(self.slot.getSaturday())
    
    def TestSundayTrue(self):
        self.slot.data = 0b1111111
        self.assertTrue(self.slot.getSunday())
    def TestMondayTrue(self):
        self.slot.data = 0b1111111
        self.assertTrue(self.slot.getMonday())
    def TestTuesdayTrue(self):
        self.slot.data = 0b1111111
        self.assertTrue(self.slot.getTuesday())
    def TestWednesdayTrue(self):
        self.slot.data = 0b1111111
        self.assertTrue(self.slot.getWednesday())
    def TestThursdayTrue(self):
        self.slot.data = 0b1111111
        self.assertTrue(self.slot.getThursday())
    def TestFridayTrue(self):
        self.slot.data = 0b1111111
        self.assertTrue(self.slot.getFriday())
    def TestSaturdayTrue(self):
        self.slot.data = 0b1111111
        self.assertTrue(self.slot.getSaturday())

for i in TestStudentLogin.__dict__:
    if i.startswith("Test"):
        print("test "+i)
        test = TestStudentLogin(i)
        test.setUpTestData()
        test.setUpClass()
        test.setUp()
        test.run()
        test.tearDown()
        test.tearDownClass()