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
        return 0
    def getLengthMinutes(self)->int:
        return 0
    def __str__(self)->str:
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