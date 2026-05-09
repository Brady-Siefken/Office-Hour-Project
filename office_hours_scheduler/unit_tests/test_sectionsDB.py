import unittest
from scheduler_app.models import Course, Department, Section, User
from classes.Sections import SectionClass
# from classes.SectionsDatabase import (
#     doesSectionExist,
#     getSection,
#     getAllSections,
#     getSectionsByCourse,
#     getSectionsByType,
#     getSectionsByInstructor,
#     getSectionsByTA,
#     assignInstructor,
#     assignTA,
#     createSection,
#     deleteSection
# )
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
    deleteSection,
    addStudentsFromText,
    getStudents
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









    # ----------------------------
    # getStudents tests
    # ----------------------------

    def test_get_students_returns_empty_when_no_students(self):
        result = getStudents("EE", 101, 1)
        self.assertEqual(result, [])

    def test_get_students_returns_correct_student(self):
        from classes.Users import UserClass
        student = User.objects.create(
            email="student@test.com",
            password="pass",
            name="Test Student",
            user_type="STUDENT"
        )
        self.section.students.add(student)
        result = getStudents("EE", 101, 1)
        self.assertEqual(len(result), 1)
        self.assertIsInstance(result[0], UserClass)
        self.assertEqual(result[0].getEmail(), "student@test.com")

    def test_get_students_returns_multiple_students(self):
        student1 = User.objects.create(email="s1@test.com", password="pass", name="Student One", user_type="STUDENT")
        student2 = User.objects.create(email="s2@test.com", password="pass", name="Student Two", user_type="STUDENT")
        self.section.students.add(student1, student2)
        result = getStudents("EE", 101, 1)
        self.assertEqual(len(result), 2)

    def test_get_students_raises_for_missing_section(self):
        with self.assertRaises(ValueError):
            getStudents("EE", 101, 999)

    # ----------------------------
    # addStudentsFromText tests
    # ----------------------------

    def test_add_students_from_text_creates_new_user(self):
        addStudentsFromText("EE", 101, 1, "newstudent@test.com, New Student")
        self.assertTrue(User.objects.filter(email="newstudent@test.com").exists())

    def test_add_students_from_text_new_user_is_student(self):
        addStudentsFromText("EE", 101, 1, "newstudent@test.com, New Student")
        user = User.objects.get(email="newstudent@test.com")
        self.assertEqual(user.user_type, "STUDENT")

    def test_add_students_from_text_new_user_password_is_email(self):
        addStudentsFromText("EE", 101, 1, "newstudent@test.com, New Student")
        user = User.objects.get(email="newstudent@test.com")
        self.assertEqual(user.password, "newstudent@test.com")

    def test_add_students_from_text_existing_student_is_added(self):
        student = User.objects.create(
            email="existing@test.com",
            password="pass",
            name="Existing Student",
            user_type="STUDENT"
        )
        addStudentsFromText("EE", 101, 1, "existing@test.com, Existing Student")
        result = getStudents("EE", 101, 1)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].getEmail(), "existing@test.com")

    def test_add_students_from_text_existing_user_not_overwritten(self):
        User.objects.create(
            email="existing@test.com",
            password="oldpassword",
            name="Old Name",
            user_type="STUDENT"
        )
        addStudentsFromText("EE", 101, 1, "existing@test.com, New Name")
        user = User.objects.get(email="existing@test.com")
        self.assertEqual(user.name, "Old Name")
        self.assertEqual(user.password, "oldpassword")

    def test_add_students_from_text_non_student_is_skipped(self):
        User.objects.create(
            email="instructor@test.com",
            password="pass",
            name="An Instructor",
            user_type="INSTRUCTOR"
        )
        addStudentsFromText("EE", 101, 1, "instructor@test.com, An Instructor")
        result = getStudents("EE", 101, 1)
        self.assertEqual(len(result), 0)

    def test_add_students_from_text_skips_malformed_lines(self):
        addStudentsFromText("EE", 101, 1, "bademail\nnoemail")
        result = getStudents("EE", 101, 1)
        self.assertEqual(len(result), 0)

    def test_add_students_from_text_skips_blank_lines(self):
        addStudentsFromText("EE", 101, 1, "\n\n\n")
        result = getStudents("EE", 101, 1)
        self.assertEqual(len(result), 0)

    def test_add_students_from_text_multiple_lines(self):
        addStudentsFromText("EE", 101, 1,
                            "s1@test.com, Student One\ns2@test.com, Student Two\ns3@test.com, Student Three")
        result = getStudents("EE", 101, 1)
        self.assertEqual(len(result), 3)

    def test_add_students_from_text_raises_for_missing_section(self):
        with self.assertRaises(ValueError):
            addStudentsFromText("EE", 101, 999, "student@test.com, Test Student")