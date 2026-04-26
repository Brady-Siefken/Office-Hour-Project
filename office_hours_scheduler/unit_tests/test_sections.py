import unittest

from scheduler_app.models import User, Department, Course, Section
from classes.Sections import SectionClass
from classes.Course import CourseClass


class TestSectionClass(unittest.TestCase):

    def setUp(self):
        # Clear database tables so tests do not affect each other
        Section.objects.all().delete()
        Course.objects.all().delete()
        Department.objects.all().delete()
        User.objects.all().delete()

        self.department = Department.objects.create(
            departmentName="EE"
        )

        self.course = Course.objects.create(
            department=self.department,
            courseCode=140,
            courseName="Embedded"
        )

        self.instructor = User.objects.create(
            email="instructor@test.com",
            password="pass",
            name="Dr. Smith",
            user_type="INSTRUCTOR"
        )

        self.ta = User.objects.create(
            email="ta@test.com",
            password="pass",
            name="TA John",
            user_type="TA"
        )

        self.student = User.objects.create(
            email="student@test.com",
            password="pass",
            name="Student Bob",
            user_type="STUDENT"
        )

    def test_constructor_creates_section(self):
        section = SectionClass(
            140,
            101,
            "instructor@test.com",
            "ta@test.com"
        )

        self.assertEqual(Section.objects.count(), 1)
        self.assertEqual(section.getInstructor(), "Dr. Smith")
        self.assertEqual(section.getTA(), "TA John")
        self.assertEqual(section.getSectionCode(), "101")

    def test_constructor_sets_correct_model_fields(self):
        SectionClass(
            140,
            101,
            "instructor@test.com",
            "ta@test.com"
        )

        section_model = Section.objects.first()

        self.assertEqual(section_model.instructor, self.instructor)
        self.assertEqual(section_model.ta, self.ta)
        self.assertEqual(section_model.course, self.course)
        self.assertEqual(section_model.sectionCode, 101)

    def test_constructor_wraps_existing_section_without_duplicate(self):
        Section.objects.create(
            instructor=self.instructor,
            ta=self.ta,
            course=self.course,
            sectionCode=101
        )

        self.assertEqual(Section.objects.count(), 1)

        section = SectionClass(
            140,
            101,
            "instructor@test.com",
            "ta@test.com"
        )

        self.assertEqual(Section.objects.count(), 1)
        self.assertEqual(section.getSectionCode(), "101")
        self.assertEqual(section.getInstructor(), "Dr. Smith")
        self.assertEqual(section.getTA(), "TA John")

    def test_missing_instructor_raises_value_error(self):
        with self.assertRaises(ValueError):
            SectionClass(
                140,
                101,
                "missing@test.com",
                "ta@test.com"
            )

    def test_missing_ta_raises_value_error(self):
        with self.assertRaises(ValueError):
            SectionClass(
                140,
                101,
                "instructor@test.com",
                "missing@test.com"
            )

    def test_missing_course_raises_value_error(self):
        with self.assertRaises(ValueError):
            SectionClass(
                999,
                101,
                "instructor@test.com",
                "ta@test.com"
            )

    def test_student_cannot_be_instructor(self):
        with self.assertRaises(ValueError):
            SectionClass(
                140,
                101,
                "student@test.com",
                "ta@test.com"
            )

    def test_student_cannot_be_ta(self):
        with self.assertRaises(ValueError):
            SectionClass(
                140,
                101,
                "instructor@test.com",
                "student@test.com"
            )

    def test_get_course_returns_course_wrapper(self):
        section = SectionClass(
            140,
            101,
            "instructor@test.com",
            "ta@test.com"
        )

        course_wrapper = section.getCourse()

        self.assertIsInstance(course_wrapper, CourseClass)
        self.assertEqual(course_wrapper.getCourseDepartment(), "EE")
        self.assertEqual(course_wrapper.getCourseCode(), 140)
        self.assertEqual(course_wrapper.getCourseName(), "Embedded")

    def test_get_course_does_not_create_new_course_or_department(self):
        section = SectionClass(
            140,
            101,
            "instructor@test.com",
            "ta@test.com"
        )

        course_count_before = Course.objects.count()
        department_count_before = Department.objects.count()

        course_wrapper = section.getCourse()

        course_count_after = Course.objects.count()
        department_count_after = Department.objects.count()

        self.assertIsInstance(course_wrapper, CourseClass)
        self.assertEqual(course_count_before, course_count_after)
        self.assertEqual(department_count_before, department_count_after)

    def test_get_time_slot_returns_none_for_now(self):
        section = SectionClass(
            140,
            101,
            "instructor@test.com",
            "ta@test.com"
        )

        self.assertIsNone(section.getTimeSlot())

    def test_string_representation_contains_section_code(self):
        section = SectionClass(
            140,
            101,
            "instructor@test.com",
            "ta@test.com"
        )

        self.assertIn("101", str(section))

    def test_constructor_creates_section_no_instructor_no_ta(self):
        section = SectionClass(140, 101)
        self.assertEqual(Section.objects.count(), 1)
        self.assertIsNone(section.getInstructor())
        self.assertIsNone(section.getTA())

    def test_constructor_wraps_existing_section_no_instructor_no_ta(self):
        Section.objects.create(course=self.course, sectionCode=101)
        section = SectionClass(140, 101)
        self.assertEqual(Section.objects.count(), 1)
        self.assertEqual(section.getSectionCode(), "101")

    def test_missing_course_raises_value_error_no_users(self):
        with self.assertRaises(ValueError):
            SectionClass(999, 101)

    def test_get_course_returns_correct_wrapper_no_users(self):
        section = SectionClass(140, 101)
        course_wrapper = section.getCourse()
        self.assertIsInstance(course_wrapper, CourseClass)
        self.assertEqual(course_wrapper.getCourseDepartment(), "EE")
        self.assertEqual(course_wrapper.getCourseCode(), 140)
        self.assertEqual(course_wrapper.getCourseName(), "Embedded")

    def test_get_time_slot_returns_none_no_users(self):
        section = SectionClass(140, 101)
        self.assertIsNone(section.getTimeSlot())

    def test_string_representation_no_users(self):
        section = SectionClass(140, 101)
        self.assertIn("101", str(section))

    def test_two_sections_same_course_different_codes(self):
        SectionClass(140, 101)
        SectionClass(140, 102)
        self.assertEqual(Section.objects.count(), 2)

    def test_same_section_code_different_courses(self):
        course2 = Course.objects.create(
            department=self.department,
            courseCode=141,
            courseName="Signals"
        )
        SectionClass(140, 101)
        SectionClass(141, 101)
        self.assertEqual(Section.objects.count(), 2)

