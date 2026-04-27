class TimeSlot:

    DAY_BITS = {
        "Sunday": 0b0000001,
        "Monday": 0b0000010,
        "Tuesday": 0b0000100,
        "Wednesday": 0b0001000,
        "Thursday": 0b0010000,
        "Friday": 0b0100000,
        "Saturday": 0b1000000,
    }

    MINUTES_SHIFT = 7
    LENGTH_SHIFT = 18
    ELEVEN_BIT_MASK = 0b11111111111  # 2047

    def __init__(self, data: int = 0):
        self.data = data

# Day getters

    def getSunday(self)->bool:
        return self.data & self.DAY_BITS["Sunday"] != 0
    def getMonday(self)->bool:
        return self.data & self.DAY_BITS["Monday"] != 0
    def getTuesday(self)->bool:
        return self.data & self.DAY_BITS["Tuesday"] != 0
    def getWednesday(self)->bool:
        return self.data & self.DAY_BITS["Wednesday"] != 0
    def getThursday(self)->bool:
        return self.data & self.DAY_BITS["Thursday"] != 0
    def getFriday(self)->bool:
        return self.data & self.DAY_BITS["Friday"] != 0
    def getSaturday(self)->bool:
        return self.data & self.DAY_BITS["Saturday"] != 0

# Time getters

    def getMinutesIntoDay(self)->int:
        return (self.data >> self.MINUTES_SHIFT) & self.ELEVEN_BIT_MASK
    def getLengthMinutes(self)->int:
        return (self.data >> self.LENGTH_SHIFT) & self.ELEVEN_BIT_MASK
    def getBitsCompressed(self) -> int:
        return self.data

# Nice printing

    def __str__(self) -> str:
        day_tokens = []
        if self.getSunday(): day_tokens.append("S")
        if self.getMonday(): day_tokens.append("M")
        if self.getTuesday(): day_tokens.append("T")
        if self.getWednesday(): day_tokens.append("W")
        if self.getThursday(): day_tokens.append("Th")
        if self.getFriday(): day_tokens.append("F")
        if self.getSaturday(): day_tokens.append("Sa")
        days_str = "".join(day_tokens)

        start = self.getMinutesIntoDay()
        length = self.getLengthMinutes()
        end = start + length

        start_h, start_m = divmod(start, 60)
        end_h, end_m = divmod(end, 60)

        time_str = f"{start_h:02d}:{start_m:02d}-{end_h:02d}:{end_m:02d}"

        if days_str:
            return f"{days_str} {time_str}"
        return time_str

DayOfWeek = {
    0:"Sunday",
    1:"Monday",
    2:"Tuesday",
    3:"Wednesday",
    4:"Thursday",
    5:"Friday",
    6:"Saturday"
}
