# classes/TimeslotClass.py

from datetime import datetime
from scheduler_app.models import Timeslot


class TimeslotClass:

    def __init__(
        self,
        start_time,
        end_time,
        monday=False,
        tuesday=False,
        wednesday=False,
        thursday=False,
        friday=False
    ):
        # --- Convert strings → time objects ---
        if isinstance(start_time, str):
            start_time = datetime.strptime(start_time, "%H:%M").time()

        if isinstance(end_time, str):
            end_time = datetime.strptime(end_time, "%H:%M").time()

        # --- get or create ---
        self.timeslot, _ = Timeslot.objects.get_or_create(
            start_time=start_time,
            end_time=end_time,
            monday=monday,
            tuesday=tuesday,
            wednesday=wednesday,
            thursday=thursday,
            friday=friday
        )

    # ----------------------------
    # Day getters
    # ----------------------------

    def getMonday(self):
        return self.timeslot.monday

    def getTuesday(self):
        return self.timeslot.tuesday

    def getWednesday(self):
        return self.timeslot.wednesday

    def getThursday(self):
        return self.timeslot.thursday

    def getFriday(self):
        return self.timeslot.friday

    # ----------------------------
    # Time calculations
    # ----------------------------

    def getMinutesIntoDay(self):
        t = self.timeslot.start_time
        return t.hour * 60 + t.minute

    def getLengthMinutes(self):
        start = self.getMinutesIntoDay()
        end = self.timeslot.end_time.hour * 60 + self.timeslot.end_time.minute
        return end - start

    # ----------------------------
    # String representation
    # ----------------------------

    def __str__(self):
        days = ""

        if self.getMonday():
            days += "M"
        if self.getTuesday():
            days += "T"
        if self.getWednesday():
            days += "W"
        if self.getThursday():
            days += "Th"
        if self.getFriday():
            days += "F"

        start = self.timeslot.start_time.strftime("%H:%M")
        end = self.timeslot.end_time.strftime("%H:%M")

        return f"{days} {start}-{end}"