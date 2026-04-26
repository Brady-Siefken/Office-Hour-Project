from classes.Course import CourseClass
from scheduler_app.models import Section, Course, User


class SectionClass:

    def __init__(self, course_code, section_code, instructor_email=None, ta_email=None):
        instructor = None
        ta = None

        if instructor_email is not None:
            try:
                instructor = User.objects.get(email=instructor_email)
            except User.DoesNotExist:
                raise ValueError("Instructor does not exist")
            if instructor.user_type != "INSTRUCTOR":
                raise ValueError("User is not an instructor")

        if ta_email is not None:
            try:
                ta = User.objects.get(email=ta_email)
            except User.DoesNotExist:
                raise ValueError("TA does not exist")
            if ta.user_type != "TA":
                raise ValueError("User is not a TA")

        try:
            course = Course.objects.get(courseCode=course_code)
        except Course.DoesNotExist:
            raise ValueError("Course does not exist")

        # BUG FIX: look up by natural key (course + sectionCode) only,
        # then update instructor/TA separately so stale values don't
        # silently create duplicate sections.
        self.section, created = Section.objects.get_or_create(
            course=course,
            sectionCode=section_code,
            defaults={"instructor": instructor, "ta": ta},
        )

        if not created:
            # Overwrite instructor/TA if explicitly supplied
            changed = False
            if instructor_email is not None and self.section.instructor != instructor:
                self.section.instructor = instructor
                changed = True
            if ta_email is not None and self.section.ta != ta:
                self.section.ta = ta
                changed = True
            if changed:
                self.section.save()

    # ----------------------------
    # Getters (NO side effects)
    # ----------------------------

    def getInstructor(self):
        # BUG FIX: guard against None
        return self.section.instructor.name if self.section.instructor else None

    def getTA(self):
        # BUG FIX: guard against None
        return self.section.ta.name if self.section.ta else None

    def getSectionCode(self):
        return str(self.section.sectionCode)

    def getTimeSlot(self):
        return None  # placeholder until implemented

    def getCourse(self):
        return CourseClass(
            self.section.course.department.departmentName,
            self.section.course.courseCode,
            self.section.course.courseName,
        )

    # ----------------------------
    # String representation
    # ----------------------------

    def __str__(self):
        return f"{self.section.course} Section {self.section.sectionCode}"