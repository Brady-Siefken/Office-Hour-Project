from django.test import TestCase, Client
from classes.UserDatabase import createUser
from classes.CourseDatabase import createCourse
from classes.SectionsDatabase import createSection, getSectionsByTA
from classes.OfficeHoursDatabase import createOfficeHour, getOfficeHour
from scheduler_app.models import OfficeHour

class TestApproveTAOfficeHours(TestCase):
    # Acceptance tests for instructor approving TA-proposed office hours.

    def setUp(self):
        self.client = Client()

        createUser("prof1@uwm.edu", "prof1pass", "Prof One", "INSTRUCTOR")
        createUser("prof2@uwm.edu", "prof2pass", "Prof Two", "INSTRUCTOR")
        createUser("ta@uwm.edu",    "tapass",    "TA One",   "TA")

        createCourse("CS", 101, "Intro to CS")
        createSection("CS", 101, 1, instructor_email = "prof1@uwm.edu", ta_email = "ta@uwm.edu")

        createCourse("CS", 202, "Other Course")
        createSection("CS", 202, 1, instructor_email = "prof2@uwm.edu", ta_email = "ta@uwm.edu")

    def login_as(self, email):
        session = self.client.session
        session["user_id"] = email
        session.save()

    def propose_ta_hour(self, ta_email, course_code):
        sections = getSectionsByTA(ta_email)
        section = next(
            s for s in sections
            if str(s.getCourse().getCourseCode()) == str(course_code)
        )
        days = {
            "monday":    True,
            "tuesday":   False,
            "wednesday": False,
            "thursday":  False,
            "friday":    False,
        }
        return createOfficeHour(ta_email, section, "10:00", "11:00", days)

    def test_instructor_sees_pending_ta_office_hours(self):
        oh = self.propose_ta_hour("ta@uwm.edu", 101)
        self.login_as("prof1@uwm.edu")

        response = self.client.get("/instructor/office-hours/approve/")
        pending_ids = [p.getId() for p in response.context["pending_office_hours"]]

        self.assertIn(oh.getId(), pending_ids)

    def test_instructor_does_not_see_other_instructors_pending_office_hours(self):
        my_oh    = self.propose_ta_hour("ta@uwm.edu", 101)
        other_oh = self.propose_ta_hour("ta@uwm.edu", 202)
        self.login_as("prof1@uwm.edu")

        response = self.client.get("/instructor/office-hours/approve/")
        pending_ids = [p.getId() for p in response.context["pending_office_hours"]]

        self.assertIn(my_oh.getId(), pending_ids)
        self.assertNotIn(other_oh.getId(), pending_ids)

    def test_approve_marks_office_hour_approved(self):
        oh = self.propose_ta_hour("ta@uwm.edu", 101)
        self.login_as("prof1@uwm.edu")

        self.client.post("/instructor/office-hours/approve/", {
            "office_hours_id": oh.getId(),
            "action": "approve",
        })

        refreshed = getOfficeHour(oh.getId())
        self.assertTrue(refreshed.isApproved())

    def test_reject_deletes_office_hour(self):
        oh = self.propose_ta_hour("ta@uwm.edu", 101)
        oh_id = oh.getId()
        self.login_as("prof1@uwm.edu")

        self.client.post("/instructor/office-hours/approve/", {
            "office_hours_id": oh_id,
            "action": "reject",
        })

        self.assertFalse(OfficeHour.objects.filter(id=oh_id).exists())