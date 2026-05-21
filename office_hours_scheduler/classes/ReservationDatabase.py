from datetime import datetime, timedelta
from scheduler_app.models import Reservation, OfficeHour, User
from classes.Reservation import ReservationClass

"""
def _getOfficeHourRecord(staff_email, department_name, course_code):
    try:
        return OfficeHour.objects.get(
            staff__email=staff_email,
            course__department__departmentName=department_name,
            course__courseCode=course_code,
            approved=True
        )
    except OfficeHour.DoesNotExist:
        raise ValueError("Office hour does not exist or is not approved")


def _slotNumberToTime(start_time, end_time, date, slot_number):
    start = datetime.combine(date, start_time)
    end = datetime.combine(date, end_time)

    slot_start = start + timedelta(minutes=15 * (slot_number - 1))
    slot_end = slot_start + timedelta(minutes=15)

    if slot_start >= end:
        raise ValueError("Slot number out of range")

    return slot_start.time(), slot_end.time()


def isSlotTaken(staff_email, department_name, course_code, date, slot_number):
    try:
        oh = _getOfficeHourRecord(staff_email, department_name, course_code)
    except ValueError:
        return False

    try:
        slot_start, _ = _slotNumberToTime(
            oh.timeslot.start_time,
            oh.timeslot.end_time,
            date,
            slot_number
        )
    except ValueError:
        return False

    return Reservation.objects.filter(
        office_hour=oh,
        date=date,
        chunk_start_time=slot_start
    ).exists()


def getAvailableSlots(staff_email, department_name, course_code, date):
    oh = _getOfficeHourRecord(staff_email, department_name, course_code)

    start = datetime.combine(date, oh.timeslot.start_time)
    end = datetime.combine(date, oh.timeslot.end_time)
    total_slots = int((end - start).total_seconds() / 60 / 15)

    available = []
    for slot_number in range(1, total_slots + 1):
        if not isSlotTaken(staff_email, department_name, course_code, date, slot_number):
            slot_start = start + timedelta(minutes=15 * (slot_number - 1))
            slot_end = slot_start + timedelta(minutes=15)
            available.append({
                'slot_number': slot_number,
                'start_time': slot_start.strftime("%I:%M %p"),
                'end_time': slot_end.strftime("%I:%M %p"),
            })

    return available


def getReservation(student_email, staff_email, department_name, course_code, date, slot_number):
    oh = _getOfficeHourRecord(staff_email, department_name, course_code)

    slot_start, _ = _slotNumberToTime(
        oh.timeslot.start_time,
        oh.timeslot.end_time,
        date,
        slot_number
    )

    try:
        reservation = Reservation.objects.get(
            student__email=student_email,
            office_hour=oh,
            date=date,
            chunk_start_time=slot_start
        )
    except Reservation.DoesNotExist:
        return None

    return ReservationClass(reservation.id)


def getReservationsByStudent(student_email):
    return [
        ReservationClass(r.id)
        for r in Reservation.objects.filter(student__email=student_email)
    ]


def getReservationsByOfficeHour(staff_email, department_name, course_code, date):
    oh = _getOfficeHourRecord(staff_email, department_name, course_code)
    return [
        ReservationClass(r.id)
        for r in Reservation.objects.filter(office_hour=oh, date=date)
    ]


def createReservation(student_email, staff_email, department_name, course_code, date, slot_number):
    oh = _getOfficeHourRecord(staff_email, department_name, course_code)

    slot_start, _ = _slotNumberToTime(
        oh.timeslot.start_time,
        oh.timeslot.end_time,
        date,
        slot_number
    )

    reservation_datetime = datetime.combine(date, slot_start)
    if reservation_datetime - datetime.now() < timedelta(hours=24):
        raise ValueError("Reservations must be made at least 24 hours in advance")

    try:
        student = User.objects.get(email=student_email)
    except User.DoesNotExist:
        raise ValueError("Student does not exist")

    if student.user_type != "STUDENT":
        raise ValueError("User is not a student")

    if isSlotTaken(staff_email, department_name, course_code, date, slot_number):
        raise ValueError("This slot is already taken")

    reservation = Reservation.objects.create(
        student=student,
        office_hour=oh,
        date=date,
        chunk_start_time=slot_start,
        status="PENDING"
    )

    return ReservationClass(reservation.id)
"""