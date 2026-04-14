import unittest


class TestViewOfficeHours(unittest.TestCase):
    def setUp(self):
        self.lecture_list = [{"lecture": "CS361", "ta": "Rock"},
        {"lecture": "CS351", "ta": "Boyland"}]

        self.ta_office_hours_list = [
            {"lecture": "CS361", "ta": "Rock", "start_time": "12:00", "day_of_week":  "Tuesday"},
            {"lecture": "CS361", "ta": "Rock", "start_time": "12: 15", "day_of_week":  "Tuesday"},
            {"lecture": "CS351", "ta": "Boyland", "start_time": "9: 30","day_of_week":  "Friday"}]

    def test_filter_by_day_with_available_time(self):
        result = []
        for meeting in self.ta_office_hours_list:
            if meeting.day_of_week == "Tuesday":
                result.append(meeting)

        self.assertEqual(len(result), 2) #checks that 2 meetings appear

        for meeting in result: #checks that only filtered results show
            self.assertEqual(meeting.day_of_week, "Tuesday")

def test_filter_by_day_without_available_time(self):
    result = []
    for meeting in self.ta_office_hours_list:
        if meeting.day_of_week == "Sunday":
            result.append(meeting)
    self.assertEqual(result, []) # checks for an empty search