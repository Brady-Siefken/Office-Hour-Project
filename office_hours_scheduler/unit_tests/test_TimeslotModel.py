from django.test import TestCase
from datetime import time
from scheduler_app.models import Timeslot

#Just a couple tests for the toString method in the TimeSlot model

class TestTimeslotStr(TestCase):

    def test_mwf_format(self):
        ts = Timeslot.objects.create(
            start_time=time(17, 30), end_time=time(17, 40),
            monday=True, wednesday=True, friday=True,
        )
        self.assertEqual(str(ts), "MWF 17:30-17:40")

    def test_tuesday_thursday_uses_TTh(self):
        ts = Timeslot.objects.create(
            start_time=time(14, 5), end_time=time(15, 5),
            tuesday=True, thursday=True,
        )
        self.assertEqual(str(ts), "TTh 14:05-15:05")

    def test_only_tuesday_uses_T(self):
        ts = Timeslot.objects.create(
            start_time=time(10, 0), end_time=time(10, 30),
            tuesday=True,
        )
        self.assertEqual(str(ts), "T 10:00-10:30")

    def test_only_thursday_uses_Th(self):
        ts = Timeslot.objects.create(
            start_time=time(10, 0), end_time=time(10, 30),
            thursday=True,
        )
        self.assertEqual(str(ts), "Th 10:00-10:30")

    def test_zero_padded_times(self):
        ts = Timeslot.objects.create(
            start_time=time(9, 5), end_time=time(9, 10),
            monday=True,
        )
        self.assertEqual(str(ts), "M 09:05-09:10")

    def test_no_days_set(self):
        ts = Timeslot.objects.create(
            start_time=time(10, 0), end_time=time(11, 0),
        )
        self.assertEqual(str(ts), "10:00-11:00")