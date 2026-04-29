from django.test import TestCase, Client
from scheduler_app.models import User
from classes.UserDatabase import getUser, createUser
from classes.CourseDatabase import createCourse
from classes.SectionsDatabase import createSection
from classes.OfficeHoursDatabase import getApprovedOfficeHours


class TestOfficeHourProposal(TestCase):
    monkey = None

    def setUp(self):
        self.monkey = Client()

        createUser("admin@gmail.com",    "Test", "Admin Doe",    "ADMIN")
        createUser("instruct@gmail.com", "Test", "Instruct Doe", "INSTRUCTOR")
        createUser("ta@gmail.com",       "Test", "TA Doe",       "TA")

        createCourse("CS", 101, "Intro to CS")
        createSection("CS", 101, 1, instructor_email="instruct@gmail.com", ta_email="ta@gmail.com")

    def _login_as(self, email):
        session = self.monkey.session
        session['user_id'] = email
        session.save()

    # ------------------------------------------------------------------ #
    #  GET – access control                                               #
    # ------------------------------------------------------------------ #

    def test_get_as_instructor_renders_page(self):
        self._login_as("instruct@gmail.com")
        response = self.monkey.get("/staff/office-hours/propose/")
        self.assertEqual(response.status_code, 200,
            "Instructor should be able to reach the proposal page")

    def test_get_as_ta_renders_page(self):
        self._login_as("ta@gmail.com")
        response = self.monkey.get("/staff/office-hours/propose/")
        self.assertEqual(response.status_code, 200,
            "TA should be able to reach the proposal page")

    def test_get_as_admin_redirects(self):
        self._login_as("admin@gmail.com")
        response = self.monkey.get("/staff/office-hours/propose/")
        self.assertRedirects(response, "/",
            msg_prefix="Admin should be redirected away from the proposal page")

    def test_get_unauthenticated_redirects(self):
        response = self.monkey.get("/staff/office-hours/propose/")
        self.assertRedirects(response, "/",
            msg_prefix="Unauthenticated user should be redirected away")

    # ------------------------------------------------------------------ #
    #  POST – success paths                                               #
    # ------------------------------------------------------------------ #

    def test_ta_proposal_success_redirects_to_office_hours(self):
        self._login_as("ta@gmail.com")
        response = self.monkey.post("/staff/office-hours/propose/", {
            'section_selection': 1,
            'monday': 'on',
            'start_hour':    '10',
            'start_minutes': '00',
            'end_hour':      '11',
            'end_minutes':   '00',
        })
        self.assertRedirects(response, "/office-hours/",
            msg_prefix="TA proposal should redirect to /office-hours/")

    def test_instructor_proposal_success_redirects_to_approve(self):
        self._login_as("instruct@gmail.com")
        response = self.monkey.post("/staff/office-hours/propose/", {
            'section_selection': 1,
            'wednesday': 'on',
            'start_hour':    '14',
            'start_minutes': '30',
            'end_hour':      '15',
            'end_minutes':   '30',
        })
        self.assertRedirects(response, "/instructor/office-hours/approve/",
            msg_prefix="Instructor proposal should redirect to approve page")

    def test_office_hour_created_in_database(self):
        self._login_as("ta@gmail.com")
        self.monkey.post("/staff/office-hours/propose/", {
            'section_selection': 1,
            'friday': 'on',
            'start_hour': '09',
            'start_minutes': '00',
            'end_hour': '10',
            'end_minutes': '00',
        })
        from scheduler_app.models import OfficeHour
        self.assertTrue(OfficeHour.objects.filter(staff__email="ta@gmail.com").exists(),
                        "Office hour should have been created in the database")

    def test_multiple_days_accepted(self):
        self._login_as("ta@gmail.com")
        self.monkey.post("/staff/office-hours/propose/", {
            'section_selection': 1,
            'monday': 'on',
            'wednesday': 'on',
            'friday': 'on',
            'start_hour': '10',
            'start_minutes': '00',
            'end_hour': '11',
            'end_minutes': '00',
        })
        from scheduler_app.models import OfficeHour
        self.assertTrue(OfficeHour.objects.filter(staff__email="ta@gmail.com").exists(),
                        "Office hour with multiple days should be created")

    # ------------------------------------------------------------------ #
    #  POST – access control                                              #
    # ------------------------------------------------------------------ #

    def test_post_as_admin_redirects(self):
        self._login_as("admin@gmail.com")
        response = self.monkey.post("/staff/office-hours/propose/", {
            'section_selection': 1,
            'monday': 'on',
            'start_hour': '10', 'start_minutes': '00',
            'end_hour':   '11', 'end_minutes':   '00',
        })
        self.assertRedirects(response, "/",
            msg_prefix="Admin POST should be redirected away")

    def test_post_unauthenticated_redirects(self):
        response = self.monkey.post("/staff/office-hours/propose/", {
            'section_selection': 1,
            'monday': 'on',
            'start_hour': '10', 'start_minutes': '00',
            'end_hour':   '11', 'end_minutes':   '00',
        })
        self.assertRedirects(response, "/",
            msg_prefix="Unauthenticated POST should be redirected away")

    # ------------------------------------------------------------------ #
    #  POST – missing / invalid section                                   #
    # ------------------------------------------------------------------ #

    def test_missing_section_redirects(self):
        self._login_as("ta@gmail.com")
        response = self.monkey.post("/staff/office-hours/propose/", {
            'monday': 'on',
            'start_hour': '10', 'start_minutes': '00',
            'end_hour':   '11', 'end_minutes':   '00',
        })
        self.assertRedirects(response, "/staff/office-hours/propose/",
            msg_prefix="Missing section_selection should redirect back")

    def test_section_not_belonging_to_user_redirects(self):
        self._login_as("ta@gmail.com")
        response = self.monkey.post("/staff/office-hours/propose/", {
            'section_selection': 999,
            'monday': 'on',
            'start_hour': '10', 'start_minutes': '00',
            'end_hour':   '11', 'end_minutes':   '00',
        })
        self.assertRedirects(response, "/staff/office-hours/propose/",
            msg_prefix="Unrecognised section should redirect back")

    # ------------------------------------------------------------------ #
    #  POST – day selection validation                                    #
    # ------------------------------------------------------------------ #

    def test_no_days_selected_redirects(self):
        self._login_as("ta@gmail.com")
        response = self.monkey.post("/staff/office-hours/propose/", {
            'section_selection': 1,
            'start_hour': '10', 'start_minutes': '00',
            'end_hour':   '11', 'end_minutes':   '00',
        })
        self.assertRedirects(response, "/staff/office-hours/propose/",
            msg_prefix="Submitting with no days selected should redirect back")

    # ------------------------------------------------------------------ #
    #  POST – time field validation                                       #
    # ------------------------------------------------------------------ #

    def test_non_numeric_time_redirects(self):
        self._login_as("ta@gmail.com")
        response = self.monkey.post("/staff/office-hours/propose/", {
            'section_selection': 1,
            'monday': 'on',
            'start_hour': 'abc', 'start_minutes': '00',
            'end_hour':   '11',  'end_minutes':   '00',
        })
        self.assertRedirects(response, "/staff/office-hours/propose/",
            msg_prefix="Non-numeric time fields should redirect back")

    def test_missing_time_field_redirects(self):
        self._login_as("ta@gmail.com")
        response = self.monkey.post("/staff/office-hours/propose/", {
            'section_selection': 1,
            'monday': 'on',
            'start_hour': '10', 'start_minutes': '00',
        })
        self.assertRedirects(response, "/staff/office-hours/propose/",
            msg_prefix="Missing time fields should redirect back")

    def test_hour_out_of_range_redirects(self):
        self._login_as("ta@gmail.com")
        response = self.monkey.post("/staff/office-hours/propose/", {
            'section_selection': 1,
            'monday': 'on',
            'start_hour': '25', 'start_minutes': '00',
            'end_hour':   '26', 'end_minutes':   '00',
        })
        self.assertRedirects(response, "/staff/office-hours/propose/",
            msg_prefix="Hour values outside 0-23 should redirect back")

    def test_minutes_out_of_range_redirects(self):
        self._login_as("ta@gmail.com")
        response = self.monkey.post("/staff/office-hours/propose/", {
            'section_selection': 1,
            'monday': 'on',
            'start_hour': '10', 'start_minutes': '60',
            'end_hour':   '11', 'end_minutes':   '61',
        })
        self.assertRedirects(response, "/staff/office-hours/propose/",
            msg_prefix="Minute values outside 0-59 should redirect back")

    def test_end_time_before_start_time_redirects(self):
        self._login_as("ta@gmail.com")
        response = self.monkey.post("/staff/office-hours/propose/", {
            'section_selection': 1,
            'monday': 'on',
            'start_hour': '11', 'start_minutes': '00',
            'end_hour':   '10', 'end_minutes':   '00',
        })
        self.assertRedirects(response, "/staff/office-hours/propose/",
            msg_prefix="End time before start time should redirect back")

    def test_end_time_equal_to_start_time_redirects(self):
        self._login_as("ta@gmail.com")
        response = self.monkey.post("/staff/office-hours/propose/", {
            'section_selection': 1,
            'monday': 'on',
            'start_hour': '10', 'start_minutes': '00',
            'end_hour':   '10', 'end_minutes':   '00',
        })
        self.assertRedirects(response, "/staff/office-hours/propose/",
            msg_prefix="Equal start and end time should redirect back")