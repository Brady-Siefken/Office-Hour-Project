import unittest

from scheduler_app.models import User, Department, Course, Section
from classes.Sections import SectionClass
from classes.Course import CourseClass


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