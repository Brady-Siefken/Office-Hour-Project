# classes/OfficeHoursDatabase.py
from scheduler_app.models import OfficeHour
from classes.OfficeHours import OfficeHoursClass

def getPendingOfficeHoursForInstructor(instructor_email):

    # Return wrapper instances for all unapproved TA-proposed office hours where the course has a section taught by the given instructor.
    # Only TA office hours go through approval; instructor office hours
    # don't need approval and are excluded from this list.

    pending = OfficeHour.objects.filter(
        approved=False,
        staff__user_type="TA",
        course__sections__instructor__email=instructor_email,
    ).distinct().order_by('course__courseCode', 'staff__name')

    return [OfficeHoursClass(oh.id) for oh in pending]

def getOfficeHour(office_hour_id):

    #return the OfficeHoursClass wrapper for the given id, or None if not found.

    try:
        return OfficeHoursClass(office_hour_id)
    except ValueError:
        return None

def approveOfficeHour(office_hour_id):

    #mark the given office hour as approved. Raises ValueError if not found.

    office_hour = getOfficeHour(office_hour_id)
    if office_hour is None:
        raise ValueError("There are currently no proposed office hours")
    office_hour.setApproved(True)


def rejectOfficeHour(office_hour_id):

    #Reject (delete) the office hour. Raises ValueError if not found.

    if not OfficeHour.objects.filter(id = office_hour_id).exists():
        raise ValueError("There are currently no proposed office hours")
    OfficeHour.objects.filter(id = office_hour_id).delete()