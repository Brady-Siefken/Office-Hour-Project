from datetime import datetime
from scheduler_app.models import OfficeHourReservation

class ReservedOfficeHoursClass:

    def __init__(self, reservation_id):
        try:
            self.reservation = OfficeHourReservation.objects.get(id=reservation_id)
        except OfficeHourReservation.DoesNotExist:
            raise ValueError("Reservation does not exist")

    # Getters

    def getId(self):
        return self.reservation.id

    def getStudent(self):
        from classes.Users import UserClass
        return UserClass(self.reservation.student.email)

    def getStaff(self):
        from classes.Users import UserClass
        return UserClass(self.reservation.staff.email)

    def getCourse(self):
        from classes.Course import CourseClass
        return CourseClass(
            self.reservation.course.department.departmentName,
            self.reservation.course.courseCode,
        )

    def getTimeslot(self):
        return self.reservation.timeslot

    def getReservationDate(self):
        return self.reservation.reservationDate

    def getStartTime(self):
        return datetime.combine(
            self.reservation.reservationDate,
            self.reservation.timeslot.start_time,
        )

    def __str__(self):
        return (
            f"{self.reservation.student.name} with "
            f"{self.reservation.staff.name} - "
            f"{self.reservation.course.department.departmentName} "
            f"{self.reservation.course.courseCode}"
        )