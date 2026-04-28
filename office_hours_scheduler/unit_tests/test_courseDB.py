import unittest
from scheduler_app.models import Course, Department, Section
from classes.Course import CourseClass
from classes.CourseDatabase import (
    doesCourseExist,
    getCourse,
    getAllCourses,
    getCoursesByDepartment,
    createCourse,
    deleteCourse
)


class TestCourseDatabase(unittest.TestCase):

    def setUp(self):
        Section.objects.all().delete()
        Course.objects.all().delete()
        Department.objects.all().delete()

        self.department = Department.objects.create(departmentName="EE")
        self.course = Course.objects.create(
            department=self.department,
            courseCode=101,
            courseName="Circuits"
        )

    # ----------------------------
    # doesCourseExist tests
    # ----------------------------

    def test_does_course_exist_returns_true(self):
        self.assertTrue(doesCourseExist("EE", 101))

    def test_does_course_exist_returns_false_wrong_code(self):
        self.assertFalse(doesCourseExist("EE", 999))

    def test_does_course_exist_returns_false_wrong_department(self):
        self.assertFalse(doesCourseExist("CS", 101))

    def test_does_course_exist_returns_false_both_wrong(self):
        self.assertFalse(doesCourseExist("CS", 999))

    # ----------------------------
    # getCourse tests
    # ----------------------------

    def test_get_course_returns_course_class(self):
        course = getCourse("EE", 101)
        self.assertIsInstance(course, CourseClass)

    def test_get_course_returns_correct_course(self):
        course = getCourse("EE", 101)
        self.assertEqual(course.getCourseCode(), 101)
        self.assertEqual(course.getCourseDepartment(), "EE")
        self.assertEqual(course.getCourseName(), "Circuits")

    def test_get_course_returns_none_for_missing_course(self):
        course = getCourse("EE", 999)
        self.assertIsNone(course)

    def test_get_course_returns_none_for_missing_department(self):
        course = getCourse("CS", 101)
        self.assertIsNone(course)

    # ----------------------------
    # getAllCourses tests
    # ----------------------------

    def test_get_all_courses_returns_list(self):
        result = getAllCourses()
        self.assertIsInstance(result, list)

    def test_get_all_courses_returns_one_course(self):
        result = getAllCourses()
        self.assertEqual(len(result), 1)

    def test_get_all_courses_returns_course_class_instances(self):
        result = getAllCourses()
        self.assertIsInstance(result[0], CourseClass)

    def test_get_all_courses_returns_multiple_courses(self):
        Course.objects.create(
            department=self.department,
            courseCode=102,
            courseName="Electronics"
        )
        result = getAllCourses()
        self.assertEqual(len(result), 2)

    def test_get_all_courses_empty(self):
        Course.objects.all().delete()
        result = getAllCourses()
        self.assertEqual(len(result), 0)

    # ----------------------------
    # getCoursesByDepartment tests
    # ----------------------------

    def test_get_courses_by_department_returns_correct_courses(self):
        result = getCoursesByDepartment("EE")
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].getCourseDepartment(), "EE")

    def test_get_courses_by_department_returns_empty_for_missing_department(self):
        result = getCoursesByDepartment("CS")
        self.assertEqual(len(result), 0)

    def test_get_courses_by_department_filters_correctly(self):
        dept2 = Department.objects.create(departmentName="ME")
        Course.objects.create(department=dept2, courseCode=101, courseName="Statics")
        ee_result = getCoursesByDepartment("EE")
        me_result = getCoursesByDepartment("ME")
        self.assertEqual(len(ee_result), 1)
        self.assertEqual(len(me_result), 1)
        self.assertEqual(ee_result[0].getCourseDepartment(), "EE")
        self.assertEqual(me_result[0].getCourseDepartment(), "ME")

    # ----------------------------
    # createCourse tests
    # ----------------------------

    def test_create_course_creates_new_course(self):
        createCourse("EE", 102, "Electronics")
        self.assertTrue(doesCourseExist("EE", 102))

    def test_create_course_creates_new_department_if_not_exists(self):
        createCourse("CS", 101, "Intro to CS")
        self.assertTrue(doesCourseExist("CS", 101))

    def test_create_course_raises_if_course_already_exists(self):
        with self.assertRaises(ValueError):
            createCourse("EE", 101, "Circuits")

    def test_create_course_does_not_duplicate(self):
        with self.assertRaises(ValueError):
            createCourse("EE", 101, "Circuits")
        self.assertEqual(Course.objects.filter(courseCode=101).count(), 1)

    def test_create_course_correct_name(self):
        createCourse("EE", 102, "Electronics")
        course = getCourse("EE", 102)
        self.assertEqual(course.getCourseName(), "Electronics")

    # ----------------------------
    # deleteCourse tests
    # ----------------------------

    def test_delete_course_removes_course(self):
        deleteCourse("EE", 101)
        self.assertFalse(doesCourseExist("EE", 101))

    def test_delete_course_raises_if_not_exists(self):
        with self.assertRaises(ValueError):
            deleteCourse("EE", 999)

    def test_delete_course_only_deletes_correct_course(self):
        Course.objects.create(
            department=self.department,
            courseCode=102,
            courseName="Electronics"
        )
        deleteCourse("EE", 101)
        self.assertFalse(doesCourseExist("EE", 101))
        self.assertTrue(doesCourseExist("EE", 102))

    def test_delete_course_does_not_delete_wrong_department(self):
        dept2 = Department.objects.create(departmentName="ME")
        Course.objects.create(department=dept2, courseCode=101, courseName="Statics")
        deleteCourse("EE", 101)
        self.assertFalse(doesCourseExist("EE", 101))
        self.assertTrue(doesCourseExist("ME", 101))