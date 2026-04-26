import unittest
from scheduler_app.models import Course, Department, Section, User
from classes.Sections import SectionClass
from classes.SectionsDatabase import (
    doesSectionExist,
    getSection,
    getAllSections,
    getSectionsByCourse,
    getSectionsByType,
    getSectionsByInstructor,
    getSectionsByTA,
    assignInstructor,
    assignTA,
    createSection,
    deleteSection
)


class TestSectionDatabase(unittest.TestCase):

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
        self.section = Section.objects.create(
            course=self.course,
            sectionCode=1
        )

    # ----------------------------
    # doesSectionExist tests
    # ----------------------------

    def test_does_section_exist_returns_true(self):
        self.assertTrue(doesSectionExist("EE", 101, 1))

    def test_does_section_exist_returns_false_wrong_section_code(self):
        self.assertFalse(doesSectionExist("EE", 101, 999))

    def test_does_section_exist_returns_false_wrong_course_code(self):
        self.assertFalse(doesSectionExist("EE", 999, 1))

    def test_does_section_exist_returns_false_wrong_department(self):
        self.assertFalse(doesSectionExist("CS", 101, 1))

    # ----------------------------
    # getSection tests
    # ----------------------------

    def test_get_section_returns_section_class(self):
        result = getSection("EE", 101, 1)
        self.assertIsInstance(result, SectionClass)

    def test_get_section_returns_correct_section(self):
        result = getSection("EE", 101, 1)
        self.assertEqual(result.getSectionCode(), "1")

    def test_get_section_returns_none_for_missing_section(self):
        result = getSection("EE", 101, 999)
        self.assertIsNone(result)

    def test_get_section_returns_none_for_missing_course(self):
        result = getSection("EE", 999, 1)
        self.assertIsNone(result)

    # ----------------------------
    # getAllSections tests
    # ----------------------------

    def test_get_all_sections_returns_list(self):
        result = getAllSections()
        self.assertIsInstance(result, list)

    def test_get_all_sections_returns_one_section(self):
        result = getAllSections()
        self.assertEqual(len(result), 1)

    def test_get_all_sections_returns_multiple_sections(self):
        Section.objects.create(course=self.course, sectionCode=2)
        result = getAllSections()
        self.assertEqual(len(result), 2)

    def test_get_all_sections_empty(self):
        Section.objects.all().delete()
        result = getAllSections()
        self.assertEqual(len(result), 0)

    def test_get_all_sections_returns_section_class_instances(self):
        result = getAllSections()
        self.assertIsInstance(result[0], SectionClass)

    # ----------------------------
    # getSectionsByCourse tests
    # ----------------------------

    def test_get_sections_by_course_returns_correct_sections(self):
        result = getSectionsByCourse("EE", 101)
        self.assertEqual(len(result), 1)

    def test_get_sections_by_course_returns_empty_for_missing_course(self):
        result = getSectionsByCourse("EE", 999)
        self.assertEqual(len(result), 0)

    def test_get_sections_by_course_filters_correctly(self):
        course2 = Course.objects.create(
            department=self.department,
            courseCode=102,
            courseName="Electronics"
        )
        Section.objects.create(course=course2, sectionCode=1)
        result = getSectionsByCourse("EE", 101)
        self.assertEqual(len(result), 1)

    # ----------------------------
    # getSectionsByType tests
    # ----------------------------

    def test_get_sections_by_type_lecture(self):
        result = getSectionsByType("LECTURE")
        self.assertEqual(len(result), 1)

    def test_get_sections_by_type_lab_empty(self):
        result = getSectionsByType("LAB")
        self.assertEqual(len(result), 0)

    def test_get_sections_by_type_filters_correctly(self):
        Section.objects.create(course=self.course, sectionCode=2, section_type="LAB")
        lectures = getSectionsByType("LECTURE")
        labs = getSectionsByType("LAB")
        self.assertEqual(len(lectures), 1)
        self.assertEqual(len(labs), 1)

    def test_get_sections_by_type_raises_for_invalid_type(self):
        with self.assertRaises(ValueError):
            getSectionsByType("INVALID")

    # ----------------------------
    # getSectionsByInstructor tests
    # ----------------------------

    def test_get_sections_by_instructor_returns_correct_sections(self):
        instructor = User.objects.create(
            email="instructor@test.com",
            password="pass",
            name="Dr. Smith",
            user_type="INSTRUCTOR"
        )
        self.section.instructor = instructor
        self.section.save()
        result = getSectionsByInstructor("instructor@test.com")
        self.assertEqual(len(result), 1)

    def test_get_sections_by_instructor_returns_empty_for_missing_instructor(self):
        result = getSectionsByInstructor("missing@test.com")
        self.assertEqual(len(result), 0)

    def test_get_sections_by_instructor_returns_empty_when_no_sections_assigned(self):
        User.objects.create(
            email="instructor@test.com",
            password="pass",
            name="Dr. Smith",
            user_type="INSTRUCTOR"
        )
        result = getSectionsByInstructor("instructor@test.com")
        self.assertEqual(len(result), 0)

    # ----------------------------
    # getSectionsByTA tests
    # ----------------------------

    def test_get_sections_by_ta_returns_correct_sections(self):
        ta = User.objects.create(
            email="ta@test.com",
            password="pass",
            name="TA John",
            user_type="TA"
        )
        self.section.ta = ta
        self.section.save()
        result = getSectionsByTA("ta@test.com")
        self.assertEqual(len(result), 1)

    def test_get_sections_by_ta_returns_empty_for_missing_ta(self):
        result = getSectionsByTA("missing@test.com")
        self.assertEqual(len(result), 0)

    def test_get_sections_by_ta_returns_empty_when_no_sections_assigned(self):
        User.objects.create(
            email="ta@test.com",
            password="pass",
            name="TA John",
            user_type="TA"
        )
        result = getSectionsByTA("ta@test.com")
        self.assertEqual(len(result), 0)

    # ----------------------------
    # assignInstructor tests
    # ----------------------------

    def test_assign_instructor_assigns_correctly(self):
        instructor = User.objects.create(
            email="instructor@test.com",
            password="pass",
            name="Dr. Smith",
            user_type="INSTRUCTOR"
        )
        assignInstructor("EE", 101, 1, "instructor@test.com")
        section = getSection("EE", 101, 1)
        self.assertEqual(section.getInstructor(), "Dr. Smith")

    def test_assign_instructor_raises_for_missing_section(self):
        User.objects.create(
            email="instructor@test.com",
            password="pass",
            name="Dr. Smith",
            user_type="INSTRUCTOR"
        )
        with self.assertRaises(ValueError):
            assignInstructor("EE", 101, 999, "instructor@test.com")

    def test_assign_instructor_raises_for_missing_instructor(self):
        with self.assertRaises(ValueError):
            assignInstructor("EE", 101, 1, "missing@test.com")

    def test_assign_instructor_raises_for_non_instructor(self):
        User.objects.create(
            email="ta@test.com",
            password="pass",
            name="TA John",
            user_type="TA"
        )
        with self.assertRaises(ValueError):
            assignInstructor("EE", 101, 1, "ta@test.com")

    # ----------------------------
    # assignTA tests
    # ----------------------------

    def test_assign_ta_assigns_correctly(self):
        ta = User.objects.create(
            email="ta@test.com",
            password="pass",
            name="TA John",
            user_type="TA"
        )
        assignTA("EE", 101, 1, "ta@test.com")
        section = getSection("EE", 101, 1)
        self.assertEqual(section.getTA(), "TA John")

    def test_assign_ta_raises_for_missing_section(self):
        User.objects.create(
            email="ta@test.com",
            password="pass",
            name="TA John",
            user_type="TA"
        )
        with self.assertRaises(ValueError):
            assignTA("EE", 101, 999, "ta@test.com")

    def test_assign_ta_raises_for_missing_ta(self):
        with self.assertRaises(ValueError):
            assignTA("EE", 101, 1, "missing@test.com")

    def test_assign_ta_raises_for_non_ta(self):
        User.objects.create(
            email="instructor@test.com",
            password="pass",
            name="Dr. Smith",
            user_type="INSTRUCTOR"
        )
        with self.assertRaises(ValueError):
            assignTA("EE", 101, 1, "instructor@test.com")

    # ----------------------------
    # createSection tests
    # ----------------------------

    def test_create_section_creates_new_section(self):
        createSection("EE", 101, 2)
        self.assertTrue(doesSectionExist("EE", 101, 2))

    def test_create_section_raises_if_already_exists(self):
        with self.assertRaises(ValueError):
            createSection("EE", 101, 1)

    def test_create_section_raises_for_missing_course(self):
        with self.assertRaises(ValueError):
            createSection("EE", 999, 1)

    def test_create_section_raises_for_invalid_section_type(self):
        with self.assertRaises(ValueError):
            createSection("EE", 101, 2, section_type="INVALID")

    def test_create_section_default_type_is_lecture(self):
        createSection("EE", 101, 2)
        section = getSection("EE", 101, 2)
        self.assertEqual(section.getSectionType(), "LECTURE")

    def test_create_section_with_lab_type(self):
        createSection("EE", 101, 2, section_type="LAB")
        section = getSection("EE", 101, 2)
        self.assertEqual(section.getSectionType(), "LAB")

    def test_create_section_with_instructor(self):
        User.objects.create(
            email="instructor@test.com",
            password="pass",
            name="Dr. Smith",
            user_type="INSTRUCTOR"
        )
        createSection("EE", 101, 2, instructor_email="instructor@test.com")
        section = getSection("EE", 101, 2)
        self.assertEqual(section.getInstructor(), "Dr. Smith")

    def test_create_section_with_ta(self):
        User.objects.create(
            email="ta@test.com",
            password="pass",
            name="TA John",
            user_type="TA"
        )
        createSection("EE", 101, 2, ta_email="ta@test.com")
        section = getSection("EE", 101, 2)
        self.assertEqual(section.getTA(), "TA John")

    def test_create_section_raises_for_missing_instructor(self):
        with self.assertRaises(ValueError):
            createSection("EE", 101, 2, instructor_email="missing@test.com")

    def test_create_section_raises_for_missing_ta(self):
        with self.assertRaises(ValueError):
            createSection("EE", 101, 2, ta_email="missing@test.com")

    def test_create_section_raises_for_non_instructor(self):
        User.objects.create(
            email="ta@test.com",
            password="pass",
            name="TA John",
            user_type="TA"
        )
        with self.assertRaises(ValueError):
            createSection("EE", 101, 2, instructor_email="ta@test.com")

    def test_create_section_raises_for_non_ta(self):
        User.objects.create(
            email="instructor@test.com",
            password="pass",
            name="Dr. Smith",
            user_type="INSTRUCTOR"
        )
        with self.assertRaises(ValueError):
            createSection("EE", 101, 2, ta_email="instructor@test.com")

    # ----------------------------
    # deleteSection tests
    # ----------------------------

    def test_delete_section_removes_section(self):
        deleteSection("EE", 101, 1)
        self.assertFalse(doesSectionExist("EE", 101, 1))

    def test_delete_section_raises_if_not_exists(self):
        with self.assertRaises(ValueError):
            deleteSection("EE", 101, 999)

    def test_delete_section_only_deletes_correct_section(self):
        Section.objects.create(course=self.course, sectionCode=2)
        deleteSection("EE", 101, 1)
        self.assertFalse(doesSectionExist("EE", 101, 1))
        self.assertTrue(doesSectionExist("EE", 101, 2))