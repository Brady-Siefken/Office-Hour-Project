# classes/SectionDatabase.py
from scheduler_app.models import Section, Course, User
from classes.Sections import SectionClass
from classes.constants import SECTION_TYPES


def doesSectionExist(department_name, course_code, section_code):
    return Section.objects.filter(
        course__department__departmentName=department_name,
        course__courseCode=course_code,
        sectionCode=section_code
    ).exists()


def getSection(department_name, course_code, section_code):
    try:
        return SectionClass(department_name, course_code, section_code)
    except ValueError:
        return None


def getAllSections():
    return [
        SectionClass(
            s.course.department.departmentName,
            s.course.courseCode,
            s.sectionCode
        )
        for s in Section.objects.all()
    ]


def getSectionsByCourse(department_name, course_code):
    return [
        SectionClass(
            s.course.department.departmentName,
            s.course.courseCode,
            s.sectionCode
        )
        for s in Section.objects.filter(
            course__department__departmentName=department_name,
            course__courseCode=course_code
        )
    ]


def getSectionsByType(section_type):
    if section_type not in SECTION_TYPES:
        raise ValueError(f"Invalid section type '{section_type}'")
    return [
        SectionClass(
            s.course.department.departmentName,
            s.course.courseCode,
            s.sectionCode
        )
        for s in Section.objects.filter(section_type=section_type)
    ]


def getSectionsByInstructor(instructor_email):
    return [
        SectionClass(
            s.course.department.departmentName,
            s.course.courseCode,
            s.sectionCode
        )
        for s in Section.objects.filter(instructor__email=instructor_email, course__isnull = False,)
    ]


def getSectionsByTA(ta_email):
    return [
        SectionClass(
            s.course.department.departmentName,
            s.course.courseCode,
            s.sectionCode
        )
        for s in Section.objects.filter(ta__email=ta_email, course__isnull = False,)
    ]

def getSectionsByStudent(student_email):
    sections = Section.objects.filter(students__email=student_email)
    return [SectionClass(s.course.department.departmentName, s.course.courseCode, s.sectionCode) for s in sections]

def assignInstructor(department_name, course_code, section_code, instructor_email):
    section = getSection(department_name, course_code, section_code)
    if section is None:
        raise ValueError("Section does not exist")
    section.setInstructor(instructor_email)


def assignTA(department_name, course_code, section_code, ta_email):
    section = getSection(department_name, course_code, section_code)
    if section is None:
        raise ValueError("Section does not exist")
    section.setTA(ta_email)


def createSection(department_name, course_code, section_code, instructor_email=None, ta_email=None, section_type="LECTURE"):
    if doesSectionExist(department_name, course_code, section_code):
        raise ValueError("Section already exists")

    if section_type not in SECTION_TYPES:
        raise ValueError(f"Invalid section type '{section_type}'")

    try:
        course = Course.objects.get(
            department__departmentName=department_name,
            courseCode=course_code
        )
    except Course.DoesNotExist:
        raise ValueError("Course does not exist")

    instructor = None
    if instructor_email is not None:
        try:
            instructor = User.objects.get(email=instructor_email)
        except User.DoesNotExist:
            raise ValueError("Instructor does not exist")
        if instructor.user_type != "INSTRUCTOR":
            raise ValueError("User is not an instructor")

    ta = None
    if ta_email is not None:
        try:
            ta = User.objects.get(email=ta_email)
        except User.DoesNotExist:
            raise ValueError("TA does not exist")
        if ta.user_type != "TA":
            raise ValueError("User is not a TA")

    Section.objects.create(
        course=course,
        sectionCode=section_code,
        instructor=instructor,
        ta=ta,
        section_type=section_type
    )


def deleteSection(department_name, course_code, section_code):
    if not doesSectionExist(department_name, course_code, section_code):
        raise ValueError("Section does not exist")
    Section.objects.filter(
        course__department__departmentName=department_name,
        course__courseCode=course_code,
        sectionCode=section_code
    ).delete()

def addStudentsFromText(department_name, course_code, section_code, text):
    section = getSection(department_name, course_code, section_code)
    if section is None:
        raise ValueError("Section does not exist")
    section.addStudentsFromText(text)

def getStudents(department_name, course_code, section_code):
    section = getSection(department_name, course_code, section_code)
    if section is None:
        raise ValueError("Section does not exist")
    return section.getStudents()

def getCoursesByStudent(student_email):
    from classes.Course import CourseClass
    sections = Section.objects.filter(students__email=student_email)
    seen = set()
    courses = []
    for s in sections:
        code = s.course.courseCode
        if code not in seen:
            seen.add(code)
            courses.append(CourseClass(s.course.department.departmentName, s.course.courseCode))
    return courses