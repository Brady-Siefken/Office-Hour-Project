def test_view_office_hours_filters_by_course(self):
    admin = Administrator.objects.create(name="admin1")
    instructor1 = Instructor.objects.create(name="prof1")
    instructor2 = Instructor.objects.create(name="prof2")
    ta1 = TA.objects.create(name="ta1")
    ta2 = TA.objects.create(name="ta2")

    Lecture.objects.create(
        course_name="course1",
        instructor=instructor1,
        times="MWF 8-9AM",
        instructor_office_hours="W 1-2 PM",
        ta=ta1,
        ta_office_hours="W 2-3 PM",
        approved=True,
    )

    Lecture.objects.create(
        course_name="course2",
        instructor=instructor2,
        times="TTh 2-3PM",
        instructor_office_hours="T 1-2 PM",
        ta=ta2,
        ta_office_hours="T 3-4 PM",
        approved=True,
    )

    session = self.client.session
    session["name"] = "admin1"
    session.save()

    resp = self.client.get("/office-hours/", {
        "course": "course1"
    })

    office_hours_list = resp.context["office_hours_list"]

    self.assertIn({
        "course_name": "course1",
        "staff_name": "prof1",
        "role": "instructor",
        "office_hours": "W 1-2 PM",
    }, office_hours_list)

    self.assertIn({
        "course_name": "course1",
        "staff_name": "ta1",
        "role": "ta",
        "office_hours": "W 2-3 PM",
    }, office_hours_list)

def test_view_office_hours_filters_by_ta(self):
    admin = Administrator.objects.create(name="admin1")
    instructor1 = Instructor.objects.create(name="prof1")
    instructor2 = Instructor.objects.create(name="prof2")
    ta1 = TA.objects.create(name="ta1")
    ta2 = TA.objects.create(name="ta2")

    Lecture.objects.create(
        course_name="course1",
        instructor=instructor1,
        times="MWF 8-9AM",
        instructor_office_hours="W 1-2 PM",
        ta=ta1,
        ta_office_hours="W 2-3 PM",
        approved=True,
    )

    Lecture.objects.create(
        course_name="course2",
        instructor=instructor2,
        times="TTh 2-3PM",
        instructor_office_hours="T 1-2 PM",
        ta=ta2,
        ta_office_hours="T 3-4 PM",
        approved=True,
    )

    session = self.client.session
    session["name"] = "admin1"
    session.save()

    resp = self.client.get("/office-hours/", {
        "staff": "ta1"
    })

    office_hours_list = resp.context["office_hours_list"]

    self.assertIn({
        "course_name": "course1",
        "staff_name": "ta1",
        "role": "ta",
        "office_hours": "W 2-3 PM",
    }, office_hours_list)

    self.assertNotIn({
        "course_name": "course1",
        "staff_name": "prof1",
        "role": "instructor",
        "office_hours": "W 1-2 PM",
    }, office_hours_list)

def test_view_office_hours_filters_by_instructor(self):
    admin = Administrator.objects.create(name="admin1")
    instructor1 = Instructor.objects.create(name="prof1")
    instructor2 = Instructor.objects.create(name="prof2")
    ta1 = TA.objects.create(name="ta1")
    ta2 = TA.objects.create(name="ta2")

    Lecture.objects.create(
        course_name="course1",
        instructor=instructor1,
        times="MWF 8-9AM",
        instructor_office_hours="W 1-2 PM",
        ta=ta1,
        ta_office_hours="W 2-3 PM",
        approved=True,
    )

    Lecture.objects.create(
        course_name="course2",
        instructor=instructor2,
        times="TTh 2-3PM",
        instructor_office_hours="T 1-2 PM",
        ta=ta2,
        ta_office_hours="T 3-4 PM",
        approved=True,
    )

    session = self.client.session
    session["name"] = "admin1"
    session.save()

    resp = self.client.get("/office-hours/", {
        "staff": "prof1"
    })

    office_hours_list = resp.context["office_hours_list"]

    self.assertIn({
        "course_name": "course1",
        "staff_name": "prof1",
        "role": "instructor",
        "office_hours": "W 1-2 PM",
    }, office_hours_list)

    self.assertNotIn({
        "course_name": "course1",
        "staff_name": "ta1",
        "role": "ta",
        "office_hours": "W 2-3 PM",
    }, office_hours_list)
