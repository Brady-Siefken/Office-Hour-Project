from scheduler_app.models import Section
from classes.constants import SECTION_TYPES


class SectionClass:

    def __init__(self, department_name, course_code, section_code):
        try:
            self.section = Section.objects.get(
                course__courseCode=course_code,
                course__department__departmentName=department_name,
                sectionCode=section_code
            )
        except Section.DoesNotExist:
            raise ValueError("Section does not exist")

    # ----------------------------
    # Getters (NO side effects)
    # ----------------------------

    def getInstructor(self):
        return self.section.instructor.name if self.section.instructor else None

    def getTA(self):
        return self.section.ta.name if self.section.ta else None

    def getSectionCode(self):
        return str(self.section.sectionCode)

    def getSectionType(self):
        return self.section.section_type

    def getTimeSlot(self):
        return None  # placeholder until implemented

    def getCourse(self):
        from classes.Course import CourseClass
        return CourseClass(
            self.section.course.department.departmentName,
            self.section.course.courseCode
        )

    # ----------------------------
    # Setters
    # ----------------------------

    def setInstructor(self, instructor_email):
        from scheduler_app.models import User
        if instructor_email is None:
            self.section.instructor = None
        else:
            try:
                instructor = User.objects.get(email=instructor_email)
            except User.DoesNotExist:
                raise ValueError("Instructor does not exist")
            if instructor.user_type != "INSTRUCTOR":
                raise ValueError("User is not an instructor")
            self.section.instructor = instructor
        self.section.save()

    def setTA(self, ta_email):
        from scheduler_app.models import User
        if ta_email is None:
            self.section.ta = None
        else:
            try:
                ta = User.objects.get(email=ta_email)
            except User.DoesNotExist:
                raise ValueError("TA does not exist")
            if ta.user_type != "TA":
                raise ValueError("User is not a TA")
            self.section.ta = ta
        self.section.save()

    def setSectionType(self, section_type):
        if section_type not in SECTION_TYPES:
            raise ValueError(f"Invalid section type '{section_type}'")
        self.section.section_type = section_type
        self.section.save()

    # ----------------------------
    # String representation
    # ----------------------------

    def __str__(self):
        return f"{self.section.course} Section {self.section.sectionCode}"