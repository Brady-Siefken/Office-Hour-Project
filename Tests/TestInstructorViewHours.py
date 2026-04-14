import unittest

class TestInstructorViewOfficeHours(unittest.TestCase):

    def setUp(self):
        self.lecture_list = [{"lecture": "CS361", "ta": "Rock"},
                             {"lecture": "CS351", "ta": "Boyland"}]

        self.ta_office_hours_list = [
            {"lecture": "CS361", "ta": "Rock", "start_time": "10:00", "day_of_week": "Monday"},
            {"lecture": "CS361", "ta": "Rock", "start_time": "12: 15", "day_of_week": "Tuesday"},
            {"lecture": "CS351", "ta": "Boyland", "start_time": "9: 30", "day_of_week": "Friday"}]

    def test_filter_by_course(self):
        result = []
        for meeting in self.ta_office_hours_list:
            if meeting.lecture == "CS361":
                result.append(meeting)
        self.assertEqual(len(result), 2) #checks that 2 meetings appear
        for meeting in result: # checks that only filtered results show
            self.assertEqual(meeting.lecture, "CS361")

    def test_invalid_course(self):
        result = []
        for meeting in self.ta_office_hours_list:
            if meeting.lecture == "CS411":
                result.append(meeting)
        self.assertEqual(result, []) # checks for an empty search

