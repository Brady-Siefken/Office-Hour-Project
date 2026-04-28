import unittest
from classes.TimeSlot import TimeSlot

class TestTimeSlotDayGetters(unittest.TestCase):
    # Tests for the seven day-of-week getter methods

    def setUp(self):
        self.slot = TimeSlot(0b110101100111110000000)
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
        slot = TimeSlot(0b1111111)
        self.assertTrue(slot.getSunday())

    def test_MondayTrue(self):
        slot = TimeSlot(0b1111111)
        self.assertTrue(slot.getMonday())

    def test_TuesdayTrue(self):
        slot = TimeSlot(0b1111111)
        self.assertTrue(slot.getTuesday())

    def test_WednesdayTrue(self):
        slot = TimeSlot(0b1111111)
        self.assertTrue(slot.getWednesday())

    def test_ThursdayTrue(self):
        slot = TimeSlot(0b1111111)
        self.assertTrue(slot.getThursday())

    def test_FridayTrue(self):
        slot = TimeSlot(0b1111111)
        self.assertTrue(slot.getFriday())

    def test_SaturdayTrue(self):
        slot = TimeSlot(0b1111111)
        self.assertTrue(slot.getSaturday())

class TestTimeSlotMinutesIntoDay(unittest.TestCase):
    # Tests for getMinutesIntoDay (bits 7-17).

    def test_zero_minutes_when_data_is_zero(self):
        self.assertEqual(TimeSlot(0).getMinutesIntoDay(), 0)

    def test_minutes_extracted_correctly(self):
        slot = TimeSlot(1050 << 7)
        self.assertEqual(slot.getMinutesIntoDay(), 1050)

    def test_day_bits_do_not_pollute_minutes(self):
        slot = TimeSlot(0b1111111)
        self.assertEqual(slot.getMinutesIntoDay(), 0)

    def test_length_bits_do_not_pollute_minutes(self):
        slot = TimeSlot(60 << 18)
        self.assertEqual(slot.getMinutesIntoDay(), 0)

    def test_max_value(self):
        slot = TimeSlot(2047 << 7)
        self.assertEqual(slot.getMinutesIntoDay(), 2047)


class TestTimeSlotLengthMinutes(unittest.TestCase):
    # Tests for getLengthMinutes (bits 18-28).

    def test_zero_length_when_data_is_zero(self):
        self.assertEqual(TimeSlot(0).getLengthMinutes(), 0)

    def test_length_extracted_correctly(self):
        slot = TimeSlot(50 << 18)
        self.assertEqual(slot.getLengthMinutes(), 50)

    def test_day_bits_do_not_pollute_length(self):
        slot = TimeSlot(0b1111111)
        self.assertEqual(slot.getLengthMinutes(), 0)

    def test_minutes_bits_do_not_pollute_length(self):
        slot = TimeSlot(1050 << 7)
        self.assertEqual(slot.getLengthMinutes(), 0)

    def test_max_value(self):
        slot = TimeSlot(2047 << 18)
        self.assertEqual(slot.getLengthMinutes(), 2047)


class TestTimeSlotBitsCompressed(unittest.TestCase):
    # Tests for getBitsCompressed (returns the raw stored int).

    def test_returns_zero_when_unset(self):
        self.assertEqual(TimeSlot(0).getBitsCompressed(), 0)

    def test_returns_raw_data(self):
        value = 0b110101100111110000000
        self.assertEqual(TimeSlot(value).getBitsCompressed(), value)


class TestTimeSlotToString(unittest.TestCase):
   # Tests for __str__ (formatted day + time string).

    @staticmethod
    def _build(days_mask: int, minutes_into_day: int, length_minutes: int) -> TimeSlot:
        data = days_mask | (minutes_into_day << 7) | (length_minutes << 18)
        return TimeSlot(data)

    def test_mwf_lecture_format(self):
        # Mon|Wed|Fri = bits 1,3,5 = 0b0101010
        # Start 17:30 = 1050 min. Length 10 min. End 17:40.
        slot = self._build(0b0101010, 1050, 10)
        self.assertEqual(str(slot), "MWF 17:30-17:40")

    def test_tuesday_thursday_lecture_format(self):
        # Tue|Thu = bits 2,4 = 0b0010100
        # Start 14:05 = 845 min. Length 60 min. End 15:05.
        slot = self._build(0b0010100, 845, 60)
        self.assertEqual(str(slot), "TTh 14:05-15:05")

    def test_only_tuesday_uses_T(self):
        slot = self._build(0b0000100, 600, 30)
        self.assertEqual(str(slot), "T 10:00-10:30")

    def test_only_thursday_uses_Th(self):
        slot = self._build(0b0010000, 600, 30)
        self.assertEqual(str(slot), "Th 10:00-10:30")

    def test_sunday_uses_S(self):
        slot = self._build(0b0000001, 540, 60)
        self.assertEqual(str(slot), "S 09:00-10:00")

    def test_saturday_uses_Sa(self):
        slot = self._build(0b1000000, 540, 60)
        self.assertEqual(str(slot), "Sa 09:00-10:00")

    def test_zero_padded_times(self):
        # Start 09:05 = 545 min. Length 5 min. End 09:10.
        slot = self._build(0b0000010, 545, 5)
        self.assertEqual(str(slot), "M 09:05-09:10")

    def test_no_days_set(self):
        slot = self._build(0, 600, 60)
        self.assertEqual(str(slot), "10:00-11:00")

    def test_all_days_set(self):
        slot = self._build(0b1111111, 600, 60)
        self.assertEqual(str(slot), "SMTWThFSa 10:00-11:00")