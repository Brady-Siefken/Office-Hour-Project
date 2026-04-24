import unittest


from classes.TimeSlot import TimeSlot
class TestStudentLogin(unittest.TestCase):
    slot:TimeSlot = TimeSlot()
    def setUp(self):
        self.slot.data = 0b110101100111110000000
    def test_Sunday(self):
        self.assertFalse(self.slot.getSunday())
    def test_Monday(self):
        self.assertFalse(self.slot.getMonday())
    def testTuesday(self):
        self.assertFalse(self.slot.getTuesday())
    def testWednesday(self):
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

# for i in TestStudentLogin.__dict__:
#     if i.startswith("Test"):
#         print("test "+i)
#         test = TestStudentLogin(i)
#         test.setUpTestData()
#         test.setUpClass()
#         test.setUp()
#         test.run()
#         test.tearDown()
#         test.tearDownClass()