class TimeSlot:
    data:int = 0
    def getSunday(self)->bool:
        return self.data&0b1!=0
    def getMonday(self)->bool:
        return self.data&0b10!=0
    def getTuesday(self)->bool:
        return self.data&0b100!=0
    def getWednesday(self)->bool:
        return self.data&0b1000!=0
    def getThursday(self)->bool:
        return self.data&0b10000!=0
    def getFriday(self)->bool:
        return self.data&0b100000!=0
    def getSaturday(self)->bool:
        return self.data&0b1000000!=0
    def getMinutesIntoDay(self)->int:
        # shifts the relevant bits into front position, then excludes everything else with a bitmask
        # may need to switch bitshift direction << to >> and/or change the number of bits shifted
        # same for length
        return (self.data<<14)&0b11111111111
    def getLengthMinutes(self)->int:
        return (self.data<<7)&0b11111111111
    def __str__(self)->str:
        # TODO
        return ""
DayOfWeek = {
    0:"Sunday",
    1:"Monday",
    2:"Tuesday",
    3:"Wednesday",
    4:"Thursday",
    5:"Friday",
    6:"Saturday"
}