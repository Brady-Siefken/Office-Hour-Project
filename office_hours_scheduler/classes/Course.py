from scheduler_app.models import Course, Department


class CourseClass:

    def __init__(self, department_name, course_code, course_name):

        # Quietly create department if it doesn't exist
        department, _ = Department.objects.get_or_create(
            departmentName=department_name
        )

        # Natural key: (department, courseCode)
        self.course, _ = Course.objects.get_or_create(
            department=department,
            courseCode=course_code,
            defaults={"courseName": course_name},
        )

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

        sections = []
        for s in self.course.sections.all():
            instructor_email = s.instructor.email if s.instructor else None
            ta_email = s.ta.email if s.ta else None
            sections.append(
                SectionClass(
                    s.course.courseCode,
                    s.sectionCode,
                    instructor_email,
                    ta_email,
                )
            )
        return sections

    # ----------------------------
    # String representation
    # ----------------------------

    def __str__(self):
        return (
            f"{self.course.department.departmentName} "
            f"{self.course.courseCode} - {self.course.courseName}"
        )