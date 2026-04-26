import unittest
from scheduler_app.models import Course, Department, Section, User
from classes.Course import CourseClass


class TestCourseClass(unittest.TestCase):

    def setUp(self):
        Section.objects.all().delete()
        Course.objects.all().delete()
        Department.objects.all().delete()
        User.objects.all().delete()

        self.department = Department.objects.create(departmentName="EE")
        self.course = Course.objects.create(
            department=self.department,
            courseCode=101,
            courseName="Circuits"
        )

    # ----------------------------
    # Constructor tests
    # ----------------------------

    def test_constructor_wraps_existing_course(self):
        course = CourseClass("EE", 101)
        self.assertEqual(course.getCourseCode(), 101)

    def test_constructor_raises_for_missing_course(self):
        with self.assertRaises(ValueError):
            CourseClass("EE", 999)

    def test_constructor_raises_for_missing_department(self):
        with self.assertRaises(ValueError):
            CourseClass("CS", 101)

    def test_constructor_does_not_create_new_course(self):
        with self.assertRaises(ValueError):
            CourseClass("EE", 202)
        self.assertEqual(Course.objects.count(), 1)

    def test_constructor_does_not_create_new_department(self):
        with self.assertRaises(ValueError):
            CourseClass("CS", 101)
        self.assertEqual(Department.objects.count(), 1)

    # ----------------------------
    # Getter tests
    # ----------------------------

    def test_get_course_department(self):
        course = CourseClass("EE", 101)
        self.assertEqual(course.getCourseDepartment(), "EE")

    def test_get_course_code(self):
        course = CourseClass("EE", 101)
        self.assertEqual(course.getCourseCode(), 101)

    def test_get_course_name(self):
        course = CourseClass("EE", 101)
        self.assertEqual(course.getCourseName(), "Circuits")

    # ----------------------------
    # Section tests (no users)
    # ----------------------------

    def test_get_sections_empty(self):
        course = CourseClass("EE", 101)
        self.assertEqual(course.getSections(), [])

    def test_get_sections_returns_one_section(self):
        Section.objects.create(course=self.course, sectionCode=1)
        course = CourseClass("EE", 101)
        self.assertEqual(len(course.getSections()), 1)

    def test_get_sections_returns_multiple_sections(self):
        Section.objects.create(course=self.course, sectionCode=1)
        Section.objects.create(course=self.course, sectionCode=2)
        Section.objects.create(course=self.course, sectionCode=3)
        course = CourseClass("EE", 101)
        self.assertEqual(len(course.getSections()), 3)

    def test_get_sections_returns_section_class_instances(self):
        from classes.Sections import SectionClass
        Section.objects.create(course=self.course, sectionCode=1)
        course = CourseClass("EE", 101)
        self.assertIsInstance(course.getSections()[0], SectionClass)

    def test_get_sections_with_instructor_and_ta(self):
        instructor = User.objects.create(
            email="instructor@test.com",
            password="pass",
            name="Dr. Smith",
            user_type="INSTRUCTOR"
        )
        ta = User.objects.create(
            email="ta@test.com",
            password="pass",
            name="TA John",
            user_type="TA"
        )
        Section.objects.create(
            course=self.course,
            sectionCode=1,
            instructor=instructor,
            ta=ta
        )
        course = CourseClass("EE", 101)
        self.assertEqual(len(course.getSections()), 1)

    # ----------------------------
    # Multi-course/department tests
    # ----------------------------

    def test_two_courses_same_code_different_departments(self):
        dept2 = Department.objects.create(departmentName="ME")
        Course.objects.create(department=dept2, courseCode=101, courseName="Statics")
        ee_course = CourseClass("EE", 101)
        me_course = CourseClass("ME", 101)
        self.assertEqual(ee_course.getCourseDepartment(), "EE")
        self.assertEqual(me_course.getCourseDepartment(), "ME")

    def test_two_courses_same_code_different_departments_different_names(self):
        dept2 = Department.objects.create(departmentName="ME")
        Course.objects.create(department=dept2, courseCode=101, courseName="Statics")
        ee_course = CourseClass("EE", 101)
        me_course = CourseClass("ME", 101)
        self.assertNotEqual(ee_course.getCourseName(), me_course.getCourseName())

    def test_different_course_same_department(self):
        Course.objects.create(
            department=self.department,
            courseCode=102,
            courseName="Electronics"
        )
        course1 = CourseClass("EE", 101)
        course2 = CourseClass("EE", 102)
        self.assertEqual(course1.getCourseName(), "Circuits")
        self.assertEqual(course2.getCourseName(), "Electronics")

    # ----------------------------
    # String representation
    # ----------------------------

    def test_str_representation(self):
        course = CourseClass("EE", 101)
        self.assertIn("EE", str(course))
        self.assertIn("101", str(course))
        self.assertIn("Circuits", str(course))