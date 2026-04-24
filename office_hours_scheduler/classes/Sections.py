from scheduler_app.models import Section, Course, User


class SectionClass:

    def __init__(self, instructor_email, ta_email, course_code, section_code):

        # --- Instructor lookup ---
        try:
            instructor = User.objects.get(email=instructor_email)
        except User.DoesNotExist:
            raise ValueError("Instructor does not exist")

        if instructor.user_type != "INSTRUCTOR":
            raise ValueError("User is not an instructor")

        # --- TA lookup ---
        try:
            ta = User.objects.get(email=ta_email)
        except User.DoesNotExist:
            raise ValueError("TA does not exist")

        if ta.user_type != "TA":
            raise ValueError("User is not a TA")

        # --- Course lookup ---
        try:
            course = Course.objects.get(CourseCode=course_code)
        except Course.DoesNotExist:
            raise ValueError("Course does not exist")

        # --- Create Section ---
        self.section = Section.objects.create(
            instructor=instructor,
            ta=ta,
            course=course,
            sectionCode=section_code
        )

    # ----------------------------
    # Getters (NO side effects)
    # ----------------------------

    def getInstructor(self):
        return self.section.instructor.name

    def getTA(self):
        return self.section.ta.name

    def getSectionCode(self):
        return str(self.section.sectionCode)

    def getTimeSlot(self):
        return None  # placeholder until implemented

    def getCourse(self):
        return self.section.course

    # ----------------------------
    # String representation
    # ----------------------------

    def __str__(self):
        return f"{self.section.course} Section {self.section.sectionCode}"