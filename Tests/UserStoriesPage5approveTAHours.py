def test_reject_clears_ta_office_hours(self):
    instructor = Instructor.objects.create(name="prof1")
    ta = TA.objects.create(name="ta1")

    lecture = Lecture.objects.create(
        course_name="course1",
        instructor=instructor,
        times="MWF 8-9AM",
        instructor_office_hours="W 1-2 PM",
        ta=ta,
        ta_office_hours="W 2-3 PM",
        approved=False,
    )

    session = self.client.session
    session["name"] = "prof1"
    session.save()

    self.client.post("/instructor/office-hours/approve/", {
        "lecture_id": lecture.id,
        "action": "reject",
    })

    lecture.refresh_from_db()
    self.assertEqual(lecture.ta_office_hours, "")

def test_instructor_rejects_ta_office_hours(self):
    instructor = Instructor.objects.create(name="prof1")
    ta = TA.objects.create(name="ta1")

    lecture = Lecture.objects.create(
        course_name="course1",
        instructor=instructor,
        times="MWF 8-9AM",
        instructor_office_hours="W 1-2 PM",
        ta=ta,
        ta_office_hours="W 2-3 PM",
        approved=False,
    )

    session = self.client.session
    session["name"] = "prof1"
    session.save()

    self.client.post("/instructor/office-hours/approve/", {
        "lecture_id": lecture.id,
        "action": "reject",
    })

    lecture.refresh_from_db()
    self.assertFalse(lecture.approved)

def test_instructor_approves_ta_office_hours(self):
    instructor = Instructor.objects.create(name="prof1")
    ta = TA.objects.create(name="ta1")

    lecture = Lecture.objects.create(
        course_name="course1",
        instructor=instructor,
        times="MWF 8-9AM",
        instructor_office_hours="W 1-2 PM",
        ta=ta,
        ta_office_hours="W 2-3 PM",
        approved=False,
    )

    session = self.client.session
    session["name"] = "prof1"
    session.save()

    self.client.post("/instructor/office-hours/approve/", {
        "lecture_id": lecture.id,
        "action": "approve",
    })

    lecture.refresh_from_db()
    self.assertTrue(lecture.approved)

def test_instructor_does_not_see_other_instructors_pending_ta_office_hours(self):
    instructor1 = Instructor.objects.create(name="prof1")
    instructor2 = Instructor.objects.create(name="prof2")
    ta = TA.objects.create(name="ta1")

    my_lecture = Lecture.objects.create(
        course_name="course1",
        instructor=instructor1,
        times="MWF 8-9AM",
        instructor_office_hours="W 1-2 PM",
        ta=ta,
        ta_office_hours="W 2-3 PM",
        approved=False,
    )

    other_lecture = Lecture.objects.create(
        course_name="course2",
        instructor=instructor2,
        times="TTh 2-3PM",
        instructor_office_hours="T 1-2 PM",
        ta=ta,
        ta_office_hours="T 3-4 PM",
        approved=False,
    )

    session = self.client.session
    session["name"] = "prof1"
    session.save()

    resp = self.client.get("/instructor/office-hours/approve/")

    self.assertNotIn(other_lecture, resp.context["pending_ta_office_hours"])

def test_instructor_sees_pending_ta_office_hours(self):
    instructor = Instructor.objects.create(name="prof1")
    ta = TA.objects.create(name="ta1")

    lecture = Lecture.objects.create(
        course_name="course1",
        instructor=instructor,
        times="MWF 8-9AM",
        instructor_office_hours="W 1-2 PM",
        ta=ta,
        ta_office_hours="W 2-3 PM",
        approved=False,
    )

    session = self.client.session
    session["name"] = "prof1"
    session.save()

    resp = self.client.get("/instructor/office-hours/approve/")

    self.assertIn(lecture, resp.context["pending_ta_office_hours"])
