import unittest

from scheduler_app.models import User, Department, Course, Section
from classes.Sections import SectionClass
from classes.Course import CourseClass
from classes.constants import PLACEHOLDER_PASSWORD


class TestSectionClass(unittest.TestCase):

    def setUp(self):
        Section.objects.all().delete()
        Course.objects.all().delete()
        Department.objects.all().delete()
        User.objects.all().delete()

        self.department = Department.objects.create(departmentName="EE")
        self.course = Course.objects.create(
            department=self.department,
            courseCode=140,
            courseName="Embedded"
        )

    # ----------------------------
    # Constructor tests
    # ----------------------------

    def test_constructor_wraps_existing_section(self):
        Section.objects.create(course=self.course, sectionCode=101)
        section = SectionClass("EE", 140, 101)
        self.assertEqual(section.getSectionCode(), "101")

    def test_constructor_raises_for_missing_section(self):
        with self.assertRaises(ValueError):
            SectionClass("EE", 140, 999)

    def test_constructor_raises_for_missing_course(self):
        with self.assertRaises(ValueError):
            SectionClass("EE", 999, 101)

    def test_constructor_raises_for_missing_department(self):
        with self.assertRaises(ValueError):
            SectionClass("CS", 140, 101)

    def test_constructor_does_not_create_new_section(self):
        with self.assertRaises(ValueError):
            SectionClass("EE", 140, 101)
        self.assertEqual(Section.objects.count(), 0)

    # ----------------------------
    # Getter tests (no users)
    # ----------------------------

    def test_get_instructor_returns_none_when_not_assigned(self):
        Section.objects.create(course=self.course, sectionCode=101)
        section = SectionClass("EE", 140, 101)
        self.assertIsNone(section.getInstructor())

    def test_get_ta_returns_none_when_not_assigned(self):
        Section.objects.create(course=self.course, sectionCode=101)
        section = SectionClass("EE", 140, 101)
        self.assertIsNone(section.getTA())

    def test_get_section_code(self):
        Section.objects.create(course=self.course, sectionCode=101)
        section = SectionClass("EE", 140, 101)
        self.assertEqual(section.getSectionCode(), "101")

    def test_get_time_slot_returns_none(self):
        Section.objects.create(course=self.course, sectionCode=101)
        section = SectionClass("EE", 140, 101)
        self.assertIsNone(section.getTimeSlot())

    def test_get_section_type_default_is_lecture(self):
        Section.objects.create(course=self.course, sectionCode=101)
        section = SectionClass("EE", 140, 101)
        self.assertEqual(section.getSectionType(), "LECTURE")

    # ----------------------------
    # Getter tests (with users)
    # ----------------------------

    def test_get_instructor_returns_name(self):
        instructor = User.objects.create(
            email="instructor@test.com",
            password="pass",
            name="Dr. Smith",
            user_type="INSTRUCTOR"
        )
        Section.objects.create(course=self.course, sectionCode=101, instructor=instructor)
        section = SectionClass("EE", 140, 101)
        self.assertEqual(section.getInstructor(), "Dr. Smith")

    def test_get_ta_returns_name(self):
        ta = User.objects.create(
            email="ta@test.com",
            password="pass",
            name="TA John",
            user_type="TA"
        )
        Section.objects.create(course=self.course, sectionCode=101, ta=ta)
        section = SectionClass("EE", 140, 101)
        self.assertEqual(section.getTA(), "TA John")

    # ----------------------------
    # getCourse tests
    # ----------------------------

    def test_get_course_returns_course_wrapper(self):
        Section.objects.create(course=self.course, sectionCode=101)
        section = SectionClass("EE", 140, 101)
        course_wrapper = section.getCourse()
        self.assertIsInstance(course_wrapper, CourseClass)
        self.assertEqual(course_wrapper.getCourseDepartment(), "EE")
        self.assertEqual(course_wrapper.getCourseCode(), 140)
        self.assertEqual(course_wrapper.getCourseName(), "Embedded")

    def test_get_course_does_not_create_new_course_or_department(self):
        Section.objects.create(course=self.course, sectionCode=101)
        section = SectionClass("EE", 140, 101)

        course_count_before = Course.objects.count()
        department_count_before = Department.objects.count()

        section.getCourse()

        self.assertEqual(Course.objects.count(), course_count_before)
        self.assertEqual(Department.objects.count(), department_count_before)

    # ----------------------------
    # Multi-section tests
    # ----------------------------

    def test_two_sections_same_course_different_codes(self):
        Section.objects.create(course=self.course, sectionCode=101)
        Section.objects.create(course=self.course, sectionCode=102)
        self.assertEqual(Section.objects.count(), 2)
        SectionClass("EE", 140, 101)
        SectionClass("EE", 140, 102)

    def test_same_section_code_different_courses(self):
        course2 = Course.objects.create(
            department=self.department,
            courseCode=141,
            courseName="Signals"
        )
        Section.objects.create(course=self.course, sectionCode=101)
        Section.objects.create(course=course2, sectionCode=101)
        self.assertEqual(Section.objects.count(), 2)
        SectionClass("EE", 140, 101)
        SectionClass("EE", 141, 101)

    # ----------------------------
    # String representation
    # ----------------------------

    def test_string_representation_contains_section_code(self):
        Section.objects.create(course=self.course, sectionCode=101)
        section = SectionClass("EE", 140, 101)
        self.assertIn("101", str(section))



    #----------------------------
    # this is for the new tests
    #----------------------------
    # ----------------------------
    # getStudents tests
    # ----------------------------

    def test_get_students_returns_empty_when_no_students(self):
        Section.objects.create(course=self.course, sectionCode=101)
        section = SectionClass("EE", 140, 101)
        self.assertEqual(section.getStudents(), [])

    def test_get_students_returns_user_class_objects(self):
        from classes.Users import UserClass
        student = User.objects.create(
            email="student@test.com",
            password="pass",
            name="Test Student",
            user_type="STUDENT"
        )
        s = Section.objects.create(course=self.course, sectionCode=101)
        s.students.add(student)
        section = SectionClass("EE", 140, 101)
        students = section.getStudents()
        self.assertEqual(len(students), 1)
        self.assertIsInstance(students[0], UserClass)

    def test_get_students_returns_correct_student(self):
        student = User.objects.create(
            email="student@test.com",
            password="pass",
            name="Test Student",
            user_type="STUDENT"
        )
        s = Section.objects.create(course=self.course, sectionCode=101)
        s.students.add(student)
        section = SectionClass("EE", 140, 101)
        self.assertEqual(section.getStudents()[0].getEmail(), "student@test.com")

    def test_get_students_returns_multiple_students(self):
        student1 = User.objects.create(email="s1@test.com", password="pass", name="Student One", user_type="STUDENT")
        student2 = User.objects.create(email="s2@test.com", password="pass", name="Student Two", user_type="STUDENT")
        s = Section.objects.create(course=self.course, sectionCode=101)
        s.students.add(student1, student2)
        section = SectionClass("EE", 140, 101)
        self.assertEqual(len(section.getStudents()), 2)

    # ----------------------------
    # addStudentsFromText tests
    # ----------------------------

    def test_add_students_creates_new_user(self):
        Section.objects.create(course=self.course, sectionCode=101)
        section = SectionClass("EE", 140, 101)
        section.addStudentsFromText("newstudent@test.com, New Student")
        self.assertTrue(User.objects.filter(email="newstudent@test.com").exists())

    def test_add_students_new_user_type_is_student(self):
        Section.objects.create(course=self.course, sectionCode=101)
        section = SectionClass("EE", 140, 101)
        section.addStudentsFromText("newstudent@test.com, New Student")
        user = User.objects.get(email="newstudent@test.com")
        self.assertEqual(user.user_type, "STUDENT")

    def test_add_students_new_user_password_is_email(self):
        Section.objects.create(course=self.course, sectionCode=101)
        section = SectionClass("EE", 140, 101)
        section.addStudentsFromText("newstudent@test.com, New Student")
        user = User.objects.get(email="newstudent@test.com")
        self.assertEqual(user.password, PLACEHOLDER_PASSWORD)

    def test_add_students_existing_student_is_added(self):
        student = User.objects.create(
            email="existing@test.com",
            password="pass",
            name="Existing Student",
            user_type="STUDENT"
        )
        Section.objects.create(course=self.course, sectionCode=101)
        section = SectionClass("EE", 140, 101)
        section.addStudentsFromText("existing@test.com, Existing Student")
        self.assertIn(student, section.section.students.all())

    def test_add_students_existing_user_not_overwritten(self):
        User.objects.create(
            email="existing@test.com",
            password="oldpassword",
            name="Old Name",
            user_type="STUDENT"
        )
        Section.objects.create(course=self.course, sectionCode=101)
        section = SectionClass("EE", 140, 101)
        section.addStudentsFromText("existing@test.com, New Name")
        user = User.objects.get(email="existing@test.com")
        self.assertEqual(user.name, "Old Name")
        self.assertEqual(user.password, "oldpassword")

    def test_add_students_non_student_user_is_skipped(self):
        User.objects.create(
            email="instructor@test.com",
            password="pass",
            name="An Instructor",
            user_type="INSTRUCTOR"
        )
        Section.objects.create(course=self.course, sectionCode=101)
        section = SectionClass("EE", 140, 101)
        section.addStudentsFromText("instructor@test.com, An Instructor")
        self.assertEqual(len(section.getStudents()), 0)

    def test_add_students_skips_malformed_lines(self):
        Section.objects.create(course=self.course, sectionCode=101)
        section = SectionClass("EE", 140, 101)
        section.addStudentsFromText("bademail\nnoemail")
        self.assertEqual(len(section.getStudents()), 0)

    def test_add_students_skips_blank_lines(self):
        Section.objects.create(course=self.course, sectionCode=101)
        section = SectionClass("EE", 140, 101)
        section.addStudentsFromText("\n\n\n")
        self.assertEqual(len(section.getStudents()), 0)

    def test_add_students_multiple_lines(self):
        Section.objects.create(course=self.course, sectionCode=101)
        section = SectionClass("EE", 140, 101)
        section.addStudentsFromText("s1@test.com, Student One\ns2@test.com, Student Two\ns3@test.com, Student Three")
        self.assertEqual(len(section.getStudents()), 3)