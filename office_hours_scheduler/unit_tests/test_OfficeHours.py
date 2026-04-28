from django.test import TestCase
from scheduler_app.models import (User, Course, Department, Section, Timeslot, OfficeHour)
from classes.OfficeHours import OfficeHoursClass

class OfficeHoursClassTestSetup(TestCase):

    #Creates a department, course, section, instructor, TA, timeslot, and a single OfficeHour to wrap.

    def setUp(self):
        self.department = Department.objects.create(departmentName = "COMPSCI")
        self.course = Course.objects.create(
            department = self.department,
            courseCode = 361,
            courseName = "Intro to Software Engineering",
        )
        self.instructor = User.objects.create(
            email = "instructor@uwm.edu",
            password = "inst123",
            name = "test instructor",
            user_type = "INSTRUCTOR",
        )
        self.ta = User.objects.create(
            email = "ta@uwm.edu",
            password = "ta123",
            name = "test ta",
            user_type = "TA",
        )
        self.section = Section.objects.create(
            course = self.course,
            sectionCode = 101,
            instructor = self.instructor,
            ta = self.ta,
        )
        self.timeslot = Timeslot.objects.create(
            start_time = "14:00",
            end_time = "15:00",
            tuesday = True,
            thursday = True,
        )
        self.office_hour = OfficeHour.objects.create(
            staff = self.ta,
            course = self.course,
            timeslot = self.timeslot,
            approved = False,
        )


class TestOfficeHoursClassConstruction(OfficeHoursClassTestSetup):
    #Tests for OfficeHoursClass's constructor

    def test_construct_with_valid_id(self):
        wrapper = OfficeHoursClass(self.office_hour.id)
        self.assertEqual(wrapper.getId(), self.office_hour.id)

    def test_construct_with_invalid_id_raises(self):
        with self.assertRaises(ValueError):
            OfficeHoursClass(999999)


class TestOfficeHoursClassGetters(OfficeHoursClassTestSetup):
    #Tests for the getters.

    def setUp(self):
        super().setUp()
        self.wrapper = OfficeHoursClass(self.office_hour.id)

    def test_getId(self):
        self.assertEqual(self.wrapper.getId(), self.office_hour.id)

    def test_getStaff(self):
        staff = self.wrapper.getStaff()
        self.assertEqual(staff.getEmail(), "ta@uwm.edu")

    def test_getCourse(self):
        course = self.wrapper.getCourse()
        self.assertEqual(course.getCourseDepartment(), "COMPSCI")
        self.assertEqual(course.getCourseCode(), 361)

    def test_getTimeslot(self):
        ts = self.wrapper.getTimeslot()
        self.assertEqual(ts.id, self.timeslot.id)

    def test_isApproved_pending(self):
        self.assertFalse(self.wrapper.isApproved())

    def test_isApproved_approved(self):
        self.office_hour.approved = True
        self.office_hour.save()
        wrapper = OfficeHoursClass(self.office_hour.id)
        self.assertTrue(wrapper.isApproved())


class TestOfficeHoursClassSetApproved(OfficeHoursClassTestSetup):
    #Tests for setApproved (the only setter).

    def test_setApproved(self):
        wrapper = OfficeHoursClass(self.office_hour.id)
        wrapper.setApproved(True)

        # Re-fetch from DB to verify persistence
        refreshed = OfficeHour.objects.get(id=self.office_hour.id)
        self.assertTrue(refreshed.approved)

    def test_setApproved_false(self):
        # Start as approved, then set back to False
        self.office_hour.approved = True
        self.office_hour.save()

        wrapper = OfficeHoursClass(self.office_hour.id)
        wrapper.setApproved(False)

        refreshed = OfficeHour.objects.get(id = self.office_hour.id)
        self.assertFalse(refreshed.approved)


class TestOfficeHoursClassStr(OfficeHoursClassTestSetup):
    #Tests for tostring.

    def test_str_includes_pending_when_unapproved(self):
        wrapper = OfficeHoursClass(self.office_hour.id)
        result = str(wrapper)
        self.assertIn("Pending", result)
        self.assertIn("test ta", result)
        self.assertIn("COMPSCI", result)

    def test_str_includes_approved_when_approved(self):
        self.office_hour.approved = True
        self.office_hour.save()
        wrapper = OfficeHoursClass(self.office_hour.id)
        self.assertIn("Approved", str(wrapper))