from scheduler_app.models import Reservation

class ReservationClass:

    def __init__(self, reservation_id):
        try:
            self.reservation = Reservation.objects.get(id=reservation_id)
        except Reservation.DoesNotExist:
            raise ValueError("Reservation does not exist")

    # ----------------------------
    # Getters (NO side effects)
    # ----------------------------

    def getStudent(self):
        from classes.Users import UserClass
        return UserClass(self.reservation.student.email)

    def getOfficeHour(self):
        from classes.OfficeHours import OfficeHoursClass
        return OfficeHoursClass(self.reservation.office_hour.id)

    def getDate(self):
        return self.reservation.date

    def getChunkStartTime(self):
        return self.reservation.chunk_start_time

    def getChunkEndTime(self):
        from datetime import datetime, timedelta
        end = datetime.combine(self.reservation.date, self.reservation.chunk_start_time)
        end += timedelta(minutes=15)
        return end.time()

    def getStatus(self):
        return self.reservation.status

    # ----------------------------
    # Setters (side effects)
    # ----------------------------

    def setStatus(self, status):
        if status not in ("PENDING", "SUCCESSFUL", "TARDY"):
            raise ValueError(f"Invalid status '{status}'")
        self.reservation.status = status
        self.reservation.save()

    def cancel(self):
        self.reservation.delete()

    # ----------------------------
    # String representation
    # ----------------------------

    def __str__(self):
        return (
            f"{self.reservation.student.name} - "
            f"{self.reservation.office_hour.course.department.departmentName} "
            f"{self.reservation.office_hour.course.courseCode} "
            f"{self.reservation.date} {self.reservation.chunk_start_time} "
            f"({self.reservation.status})"
        )