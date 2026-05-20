from datetime import datetime, timedelta
from scheduler_app.models import (
    User, OfficeHour, OfficeHourReservation, Timeslot,
)
from classes.ReservedOfficeHours import ReservedOfficeHoursClass
from datetime import date as _date_type
from classes.SlotGeneration import generate_slots


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

# Maps Python's weekday() (Monday=0) to the boolean field on Timeslot.
_DAY_FIELDS = {
    0: "monday",
    1: "tuesday",
    2: "wednesday",
    3: "thursday",
    4: "friday",
}


def _slot_datetime(reservation):
    """Combine a reservation's date and timeslot start into a datetime."""
    return datetime.combine(
        reservation.reservationDate, reservation.timeslot.start_time,
    )


# ---------------------------------------------------------------------------
# createReservation
# ---------------------------------------------------------------------------

def createReservation(student_email, office_hour_id, slot_start):
    """
    Create a 15-minute reservation for `student_email` inside `office_hour_id`
    starting at `slot_start` (a datetime).

    Returns a ReservedOfficeHoursClass.
    Raises ValueError if the student or office hour doesn't exist.
    """
    try:
        student = User.objects.get(email=student_email)
    except User.DoesNotExist:
        raise ValueError("Student does not exist")

    try:
        office_hour = OfficeHour.objects.get(id=office_hour_id)
    except OfficeHour.DoesNotExist:
        raise ValueError("Office hour does not exist")

    weekday = slot_start.weekday()
    if weekday not in _DAY_FIELDS:
        raise ValueError("Slot must fall on a weekday")

    slot_end = (slot_start + timedelta(minutes=15)).time()

    timeslot_kwargs = {field: False for field in _DAY_FIELDS.values()}
    timeslot_kwargs[_DAY_FIELDS[weekday]] = True

    slot_timeslot = Timeslot.objects.create(
        start_time=slot_start.time(),
        end_time=slot_end,
        **timeslot_kwargs,
    )

    reservation = OfficeHourReservation.objects.create(
        student=student,
        staff=office_hour.staff,
        course=office_hour.course,
        timeslot=slot_timeslot,
        reservationDate=slot_start.date(),
    )

    return ReservedOfficeHoursClass(reservation.id)


# ---------------------------------------------------------------------------
# validateReservation
# ---------------------------------------------------------------------------

def validateReservation(student_email, office_hour_id, slot_start, now):
    """
    Verify a reservation request is allowed. Returns None on success,
    raises ValueError with a descriptive message on any failure.

    Rules enforced:
      - Student must exist
      - Office hour must exist
      - Slot must be in the future
      - Slot must be at least 24 hours from `now`  (PBI #137)
      - Slot must not already be taken in this office hour
    """
    try:
        User.objects.get(email=student_email)
    except User.DoesNotExist:
        raise ValueError("Student does not exist")

    try:
        OfficeHour.objects.get(id=office_hour_id)
    except OfficeHour.DoesNotExist:
        raise ValueError("Office hour does not exist")

    if slot_start <= now:
        raise ValueError("Slot is in the past")

    if slot_start - now < timedelta(hours=24):
        raise ValueError("Reservations must be made at least 24 hours in advance")

    # Slot already taken? Compare same date + same start time within this OH's staff/course.
    existing = OfficeHourReservation.objects.filter(
        staff=OfficeHour.objects.get(id=office_hour_id).staff,
        course=OfficeHour.objects.get(id=office_hour_id).course,
        reservationDate=slot_start.date(),
        timeslot__start_time=slot_start.time(),
    )
    if existing.exists():
        raise ValueError("That slot is already taken")

    return None


# ---------------------------------------------------------------------------
# getReservation
# ---------------------------------------------------------------------------

def getReservation(reservation_id):
    """Return the wrapper for a reservation, or None if not found."""
    try:
        return ReservedOfficeHoursClass(reservation_id)
    except ValueError:
        return None


# ---------------------------------------------------------------------------
# Query helpers
# ---------------------------------------------------------------------------

def _upcoming_filter(queryset, now=None):
    """Filter a queryset of OfficeHourReservation rows down to future ones."""
    if now is None:
        now = datetime.now()
    return [r for r in queryset if _slot_datetime(r) > now]


def getUpcomingReservationsForStudent(student_email):
    rows = OfficeHourReservation.objects.filter(student__email=student_email)
    upcoming = _upcoming_filter(rows)
    return [ReservedOfficeHoursClass(r.id) for r in upcoming]


def getUpcomingReservationsForStaff(staff_email):
    rows = OfficeHourReservation.objects.filter(staff__email=staff_email)
    upcoming = _upcoming_filter(rows)
    return [ReservedOfficeHoursClass(r.id) for r in upcoming]


def getReservationsForOfficeHour(office_hour_id):
    """
    Returns reservations that fall inside this office hour block.
    Used by #135 to know which 15-min slots are already taken.

    A reservation "belongs" to an office hour if its staff + course match,
    and its timeslot is a sub-slice of the office hour's timeslot.
    Since we filter staff + course, false matches are essentially impossible
    in this app's workflow.
    """
    try:
        oh = OfficeHour.objects.get(id=office_hour_id)
    except OfficeHour.DoesNotExist:
        return []

    rows = OfficeHourReservation.objects.filter(
        staff=oh.staff, course=oh.course,
    )
    return [ReservedOfficeHoursClass(r.id) for r in rows]

# ---------------------------------------------------------------------------
# Available slots view (PBI #135)
# ---------------------------------------------------------------------------

# Map Python weekday() (Mon=0..Fri=4) to the matching Timeslot boolean field
_WEEKDAY_FIELDS = {
    0: "monday",
    1: "tuesday",
    2: "wednesday",
    3: "thursday",
    4: "friday",
}


def getAvailableSlotsForCourse(department_name, course_code, now, days_ahead=30):
    """
    Build the bookable-slots view for one course.

    Returns a list of (date, [datetime, ...]) tuples, sorted by date, where
    each datetime is the start of a 15-minute slot a student could reserve.

    A slot is included only if:
      - It belongs to an approved office hour for this course
      - The slot's weekday matches the office hour's timeslot
      - The slot starts at least 24 hours from `now`  (PBI #137)
      - The slot is not already reserved

    Dates with no available slots are omitted.
    """
    # Pull all approved OHs for this course up front; one query.
    approved_ohs = OfficeHour.objects.filter(
        approved=True,
        course__department__departmentName=department_name,
        course__courseCode=course_code,
    )

    if not approved_ohs.exists():
        return []

    # Build a quick lookup: which OHs run on each weekday?
    ohs_by_weekday = {wd: [] for wd in _WEEKDAY_FIELDS}
    for oh in approved_ohs:
        for wd, field in _WEEKDAY_FIELDS.items():
            if getattr(oh.timeslot, field):
                ohs_by_weekday[wd].append(oh)

    # Collect taken (date, start_time) tuples across all these OHs so we can
    # filter without N extra DB hits per day.
    taken = set()
    oh_ids = [oh.id for oh in approved_ohs]
    existing = OfficeHourReservation.objects.filter(
        staff__in=[oh.staff for oh in approved_ohs],
        course__department__departmentName=department_name,
        course__courseCode=course_code,
    )
    for r in existing:
        taken.add((r.staff_id, r.reservationDate, r.timeslot.start_time))

    cutoff = now + timedelta(hours=24)
    today = now.date()
    results = []

    for offset in range(days_ahead + 1):
        day = today + timedelta(days=offset)
        weekday = day.weekday()
        if weekday not in ohs_by_weekday:
            continue

        day_slots = []
        seen_keys = set()
        for oh in ohs_by_weekday[weekday]:
            ts = oh.timeslot
            for slot in generate_slots(day, ts.start_time, ts.end_time):
                if slot < cutoff:
                    continue
                # Per-OH "taken" check: same staff at same datetime.
                if (oh.staff_id, day, slot.time()) in taken:
                    continue
                key = (oh.id, slot)
                if key in seen_keys:
                    continue
                seen_keys.add(key)
                day_slots.append({
                    "start": slot,
                    "staff_name": oh.staff.name,
                    "staff_type": oh.staff.user_type,
                    "office_hour_id": oh.id,
                })

        if day_slots:
            day_slots.sort(key=lambda s: (s["start"], s["staff_name"]))
            results.append((day, day_slots))

    return results