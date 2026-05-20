import unittest
from datetime import date, datetime, time
from classes.SlotGeneration import generate_slots


class TestGenerateSlots(unittest.TestCase):
    """
    generate_slots takes:
      - a date
      - a start_time (time)
      - an end_time (time)
      - slot_minutes (int, default 15)
      """
    #Returns a list of datetime objects, each one representing the start
    #of a slot. No DB access, no side effects.

    def setUp(self):
        self.test_date = date(2026, 6, 2)  # an arbitrary Tuesday

    def test_one_hour_block_produces_four_15min_slots(self):
        result = generate_slots(self.test_date, time(14, 0), time(15, 0))
        self.assertEqual(len(result), 4)

    def test_slots_start_at_correct_times(self):
        result = generate_slots(self.test_date, time(14, 0), time(15, 0))
        expected = [
            datetime(2026, 6, 2, 14, 0),
            datetime(2026, 6, 2, 14, 15),
            datetime(2026, 6, 2, 14, 30),
            datetime(2026, 6, 2, 14, 45),
        ]
        self.assertEqual(result, expected)

    def test_returns_datetimes_not_times(self):
        result = generate_slots(self.test_date, time(14, 0), time(15, 0))
        for slot in result:
            self.assertIsInstance(slot, datetime)

    def test_two_hour_block_produces_eight_slots(self):
        result = generate_slots(self.test_date, time(14, 0), time(16, 0))
        self.assertEqual(len(result), 8)

    def test_30min_block_produces_two_slots(self):
        result = generate_slots(self.test_date, time(9, 0), time(9, 30))
        self.assertEqual(len(result), 2)

    def test_15min_block_produces_one_slot(self):
        result = generate_slots(self.test_date, time(9, 0), time(9, 15))
        self.assertEqual(len(result), 1)

    def test_last_slot_ends_at_block_end(self):
        #The final slot's end (start + 15min) must not exceed block end.
        result = generate_slots(self.test_date, time(14, 0), time(15, 0))
        last_slot_end = datetime.combine(self.test_date, time(15, 0))
        self.assertLessEqual(result[-1], last_slot_end)

    def test_non_aligned_block_truncates_to_nearest_full_slot(self):
        #A 2:00-2:40 block produces 2 slots (2:00, 2:15). 2:30 doesn't
        #fit because 2:30-2:45 would overflow 2:40.
        result = generate_slots(self.test_date, time(14, 0), time(14, 40))
        self.assertEqual(len(result), 2)
        self.assertEqual(result[-1], datetime(2026, 6, 2, 14, 15))

    def test_empty_block_produces_no_slots(self):
        result = generate_slots(self.test_date, time(14, 0), time(14, 0))
        self.assertEqual(result, [])

    def test_end_before_start_returns_empty(self):
        result = generate_slots(self.test_date, time(15, 0), time(14, 0))
        self.assertEqual(result, [])

    def test_custom_slot_length(self):
        #Passing slot_minutes=30 should give 30-min slots.
        result = generate_slots(self.test_date, time(14, 0), time(15, 0), slot_minutes=30)
        self.assertEqual(len(result), 2)
        self.assertEqual(result, [
            datetime(2026, 6, 2, 14, 0),
            datetime(2026, 6, 2, 14, 30),
        ])