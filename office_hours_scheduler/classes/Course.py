from scheduler_app.models import Course


class CourseClass:

    def __init__(self, department_name, course_code):
        try:
            self.course = Course.objects.get(
                department__departmentName=department_name,
                courseCode=course_code
            )
        except Course.DoesNotExist:
            raise ValueError("Course does not exist")

    # ----------------------------
    # Getters (NO side effects)
    # ----------------------------

    def getCourseDepartment(self):
        return self.course.department.departmentName

    def getCourseCode(self):
        return self.course.courseCode

    def getCourseName(self):
        return self.course.courseName

    def getSections(self):
        from classes.Sections import SectionClass
        return [
            SectionClass(
                self.course.department.departmentName,
                self.course.courseCode,
                s.sectionCode
            )
            for s in self.course.sections.all()
        ]

    # ----------------------------
    # String representation
    # ----------------------------

    def __str__(self):
        return (
            f"{self.course.department.departmentName} "
            f"{self.course.courseCode} - {self.course.courseName}"
        )