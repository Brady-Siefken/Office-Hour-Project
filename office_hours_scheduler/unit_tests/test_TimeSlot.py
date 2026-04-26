import unittest

from ..classes.TimeSlot import TimeSlot
class TestStudentLogin(unittest.TestCase):
    slot:TimeSlot = TimeSlot()
    def setUp(self):
        self.slot.data = 0b110101100111110000000
    def test_Sunday(self):
        self.assertFalse(self.slot.getSunday())
    def test_Monday(self):
        self.assertFalse(self.slot.getMonday())
    def test_Tuesday(self):
        self.assertFalse(self.slot.getTuesday())
    def test_Wednesday(self):
        self.assertFalse(self.slot.getWednesday())
    def test_Thursday(self):
        self.assertFalse(self.slot.getThursday())
    def test_Friday(self):
        self.assertFalse(self.slot.getFriday())
    def test_Saturday(self):
        self.assertFalse(self.slot.getSaturday())
    
    def test_SundayTrue(self):
        self.slot.data = 0b1111111
        self.assertTrue(self.slot.getSunday())
    def test_MondayTrue(self):
        self.slot.data = 0b1111111
        self.assertTrue(self.slot.getMonday())
    def test_TuesdayTrue(self):
        self.slot.data = 0b1111111
        self.assertTrue(self.slot.getTuesday())
    def test_WednesdayTrue(self):
        self.slot.data = 0b1111111
        self.assertTrue(self.slot.getWednesday())
    def test_ThursdayTrue(self):
        self.slot.data = 0b1111111
        self.assertTrue(self.slot.getThursday())
    def test_FridayTrue(self):
        self.slot.data = 0b1111111
        self.assertTrue(self.slot.getFriday())
    def test_SaturdayTrue(self):
        self.slot.data = 0b1111111
        self.assertTrue(self.slot.getSaturday())

test = unittest.main()
test.module = "test_TimeSlot"
unittest.main.runTests(test)