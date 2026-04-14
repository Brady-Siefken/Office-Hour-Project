import unittest
from datetime import datetime

class TestCancelOfficeHours(unittest.TestCase):
    HOURS_TO_CANCEL = 2

    def setUp(self):
        self.past_list = []
        self.cancel_msg = ""
        self.lecture_list = [{"lecture": "CS361", "ta": "Rock"},
                             {"lecture": "CS351", "ta": "Boyland"}]

        self.now = datetime(2026, 4, 13, 11, 0) #sets the time to 11:00 on Monday
        self.reserved_list = [
                {"lecture": "CS361", "ta": "Rock", "start_time": "12:00", "day_of_week":  "Tuesday", "reserved_id": "1"},
                {"lecture": "CS361", "ta": "Rock", "start_time": "12: 15", "day_of_week":  "Tuesday", "reserved_id": "2"},
                {"lecture": "CS351", "ta": "Boyland", "start_time": "9: 30","day_of_week":  "Wednesday", "reserved_id": "3"}]

    def test_valid_cancellation(self):
        self.cancel(reserved_id=2)
        self.assertEqual(len(self.reserved_list), 2) #checks that canceled meeting was removed

        self.assertEqual(self.cancel_msg, "Meeting cancellation successful")

        self.assertEqual(len(self.past_list), 1) #adds to past_list



    def test_cancel_without_lead_time(self):
        self.cancel(reserved_id=1) #not in enough advance to cancel
        self.assertEqual(self.cancel_msg, "Cannot cancel within 2 hours")
        self.assertEqual(len(self.past_list), 0) #shouldn't add to past_list


