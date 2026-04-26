# classes/CourseDatabase.py
from scheduler_app.models import Course, Department
from classes.Course import CourseClass


def doesCourseExist(course_code):
    return Course.objects.filter(courseCode=course_code).exists()


def getCourse(course_code):
    if not doesCourseExist(course_code):
        return None
    course = Course.objects.get(courseCode=course_code)
    return CourseClass(course.department.departmentName, course.courseCode, course.courseName)


def getAllCourses():
    return [
        CourseClass(c.department.departmentName, c.courseCode, c.courseName)
        for c in Course.objects.all()
    ]


def getCoursesByDepartment(department_name):
    return [
        CourseClass(c.department.departmentName, c.courseCode, c.courseName)
        for c in Course.objects.filter(department__departmentName=department_name)
    ]


def createCourse(department_name, course_code, course_name):
    if doesCourseExist(course_code):
        raise ValueError("Course already exists")
    CourseClass(department_name, course_code, course_name)


def deleteCourse(course_code):
    if not doesCourseExist(course_code):
        raise ValueError("Course does not exist")
    Course.objects.filter(courseCode=course_code).delete()