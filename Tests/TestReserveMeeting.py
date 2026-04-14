import unittest

class TestReserveOfficeHours(unittest.TestCase):

    def setUp(self):
        self.error_msg = ""
        self.lecture_list = [{"lecture": "CS361", "ta": "Rock"},
                             {"lecture": "CS351", "ta": "Boyland"}]
        self.available_course_office_hours = [
                {"lecture": "CS361", "ta": "Rock", "start_time": "12:00", "day_of_week":  "Tuesday", "office_hours_id": "1"},
                {"lecture": "CS361", "ta": "Rock", "start_time": "12: 15", "day_of_week":  "Tuesday", "office_hours_id": "2"},
                {"lecture": "CS351", "ta": "Boyland", "start_time": "9: 30","day_of_week":  "Wednesday", "office_hours_id": "3"},
                {"lecture": "CS351", "ta": "Boyland", "start_time": "9: 30", "day_of_week": "Friday", "office_hours_id": "4"}]

    def test_valid_reservation(self):
        for meeting in self.available_course_office_hours:
            self.reserve(meeting)

            self.assertEqual(self.error_msg, "") # no error message
            #checks that meetings are no longer available
            self.assertEqual(len(self.available_course_office_hours), 0)

    def test_invalid_reservation(self):

        #assume it's Monday, add a time for a previous date
        self.available_course_office_hours.append(
            {"lecture": "CS361", "ta": "Rock", "start_time": "12: 00", "day_of_week":  "Sunday", "office_hours_id": 5})

        self.reserve(office_hours_id=5)
        self.assertEqual(self.error_msg, "Time slot invalid, please select new time")

    def test_valid_after_invalid_reservation_(self):
        # assume it's Monday, add a time for a previous date
        self.available_course_office_hours.append(
            {"lecture": "CS361", "ta": "Rock", "start_time": "12: 00", "day_of_week": "Sunday", "office_hours_id": 5})

        self.reserve(office_hours_id=5)
        self.assertEqual(self.error_msg, "Time slot invalid, please select new time")
        self.reserve(office_hours_id=4)
        self.assertEqual(self.error_msg, "") # reserves a time after the error
