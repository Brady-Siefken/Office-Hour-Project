from scheduler_app.models import Course, Department
from classes.Sections import SectionClass

class CourseClass:
    def __init__(self, department_name, course_code, course_name):

        # Get existing OR create new department
        department, created = Department.objects.get_or_create(
            DepartmentName=department_name
        )

        # Create the course
        self.course = Course.objects.create(
            Department=department,
            CourseCode=course_code,
            CourseName=course_name
        )

    def getCourseDepartment(self):
        return self.course.department.departmentName

    def getCourseCode(self):
        return self.course.courseCode

    def getCourseName(self):
        return self.course.courseName

    def getSections(self):
        def getSections(self):
            return [SectionClass(s) for s in self.course.sections.all()]