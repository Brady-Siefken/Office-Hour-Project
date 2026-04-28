from scheduler_app.models import OfficeHour

class OfficeHoursClass:

    def __init__(self, office_hour_id):
        try:
            self.office_hour = OfficeHour.objects.get(id=office_hour_id)
        except OfficeHour.DoesNotExist:
            raise ValueError("Office hour does not exist")

    # Getters/Accessors

    def getId(self):
        return self.office_hour.id

    def getStaff(self):
        from classes.Users import UserClass
        return UserClass(self.office_hour.staff.email)

    def getCourse(self):
        from classes.Course import CourseClass
        return CourseClass(
            self.office_hour.course.department.departmentName,
            self.office_hour.course.courseCode,
        )

    def getTimeslot(self):
        return self.office_hour.timeslot

    def isApproved(self):
        return self.office_hour.approved

    # Setters/Mutators (These have side effects)

    def setApproved(self, approved):
        self.office_hour.approved = approved
        self.office_hour.save()

    def __str__(self):
        status = "Approved" if self.office_hour.approved else "Pending"
        return (
            f"{self.office_hour.staff.name} - "
            f"{self.office_hour.course.department.departmentName} "
            f"{self.office_hour.course.courseCode} ({status})"
        )