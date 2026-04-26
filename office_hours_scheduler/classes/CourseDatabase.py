# classes/CourseDatabase.py
# classes/CourseDatabase.py
from scheduler_app.models import Course, Department
from classes.Course import CourseClass


def doesCourseExist(department_name, course_code):
    return Course.objects.filter(
        department__departmentName=department_name,
        courseCode=course_code
    ).exists()


def getCourse(department_name, course_code):
    try:
        return CourseClass(department_name, course_code)
    except ValueError:
        return None


def getAllCourses():
    return [
        CourseClass(c.department.departmentName, c.courseCode)
        for c in Course.objects.all()
    ]


def getCoursesByDepartment(department_name):
    return [
        CourseClass(c.department.departmentName, c.courseCode)
        for c in Course.objects.filter(department__departmentName=department_name)
    ]


def createCourse(department_name, course_code, course_name):
    if doesCourseExist(department_name, course_code):
        raise ValueError("Course already exists")
    department, _ = Department.objects.get_or_create(departmentName=department_name)
    Course.objects.create(
        department=department,
        courseCode=course_code,
        courseName=course_name
    )


def deleteCourse(department_name, course_code):
    if not doesCourseExist(department_name, course_code):
        raise ValueError("Course does not exist")
    Course.objects.filter(
        department__departmentName=department_name,
        courseCode=course_code
    ).delete()