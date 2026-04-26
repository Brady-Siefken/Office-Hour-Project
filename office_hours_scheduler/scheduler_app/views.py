from django.views import View
from django.shortcuts import render, redirect
from classes.Users import UserClass
from classes.UserDatabase import doesUserWithEmailExist, validatePassword, getUser, countByType, deleteUser, createUser, \
    getUsersByType
from classes.CourseDatabase import getAllCourses
from classes.CourseDatabase import getAllCourses, doesCourseExist, createCourse, deleteCourse
from classes.Sections import SectionClass
from classes.SectionsDatabase import createSection, deleteSection, assignInstructor, assignTA
from classes.UserDatabase import getUser, getUsersByType

DASHBOARD_ROUTES = {
    "INSTRUCTOR": "/instructor/dashboard/",
    "TA": "/ta/dashboard/",
    "STUDENT": "/student/dashboard/",
    "ADMIN": "/admin/dashboard/",
}
class Home(View):
    def get(self, request):
        return render(request, "scheduler_app/login.html", {})

    def post(self, request):
        email = request.POST.get("email")
        password = request.POST.get("password")

        if not doesUserWithEmailExist(email):
            return render(request, "scheduler_app/login.html", {"message": "No such user"})

        if not validatePassword(email, password):
            return render(request, "scheduler_app/login.html", {"message": "Incorrect password"})

        user = UserClass(email)
        request.session["user_id"] = user.getEmail()
        request.session["user_type"] = user.getType()

        route = DASHBOARD_ROUTES.get(user.getType())
        if route is None:
            return render(request, "scheduler_app/login.html", {"message": "Unknown user type"})

        return redirect(route)

class AdminDashboardView(View):
    def get(self, request):
        user = getUser(request.session.get("user_id"))

        if user is None or user.getType() != "ADMIN":
            return redirect("/")

        context = {
            "user": user,
            "ta_count": countByType("TA"),
            "instructor_count": countByType("INSTRUCTOR"),
            "lecture_list": getAllCourses(),  # matches template
        }

        return render(request, "scheduler_app/admin_dashboard.html", context)

    def post(self, request):
        pass

class ManageUsersView(View):
        def get(self, request):
            user = getUser(request.session.get("user_id"))

            if user is None or user.getType() != "ADMIN":
                return redirect("/")

            context = {
                "instructor_list": getUsersByType("INSTRUCTOR"),
                "ta_list": getUsersByType("TA"),
                "student_list": getUsersByType("STUDENT"),
            }

            return render(request, "scheduler_app/manage_users.html", context)

        def post(self, request):
            user = getUser(request.session.get("user_id"))

            if user is None or user.getType() != "ADMIN":
                return redirect("/")

            action = request.POST.get("action")

            if action == "create":
                email = request.POST.get("email")
                password = request.POST.get("password")
                name = request.POST.get("name")
                user_type = request.POST.get("user_type")

                if doesUserWithEmailExist(email):
                    context = {
                        "instructor_list": getUsersByType("INSTRUCTOR"),
                        "ta_list": getUsersByType("TA"),
                        "student_list": getUsersByType("STUDENT"),
                        "duplicate_msg": "A user with that email already exists",
                    }
                    return render(request, "scheduler_app/manage_users.html", context)

                createUser(email, password, name, user_type)

            elif action == "edit":
                email = request.POST.get("email")
                name = request.POST.get("name")
                password = request.POST.get("password")
                user_type = request.POST.get("user_type")

                if not doesUserWithEmailExist(email):
                    return redirect("/admin/users/")

                target_user = UserClass(email)
                if name:
                    target_user.setName(name)
                if password:
                    target_user.setPassword(password)
                if user_type:
                    target_user.setType(user_type)

            elif action == "delete":
                email = request.POST.get("email")
                if doesUserWithEmailExist(email):
                    deleteUser(email)

            return redirect("/admin/users/")
    ################ Create next View here #########################



class ManageCoursesView(View):
    def get(self, request):
        user = getUser(request.session.get("user_id"))

        if user is None or user.getType() != "ADMIN":
            return redirect("/")

        context = {
            "user": user,
            "course_list": getAllCourses(),
            "instructor_list": getUsersByType("INSTRUCTOR"),
            "ta_list": getUsersByType("TA"),
        }

        return render(request, "scheduler_app/manage_courses.html", context)

    def post(self, request):
        user = getUser(request.session.get("user_id"))

        if user is None or user.getType() != "ADMIN":
            return redirect("/")

        action = request.POST.get("action")

        if action == "create_course":
            department_name = request.POST.get("department_name")
            course_code = request.POST.get("course_code")
            course_name = request.POST.get("course_name")
            try:
                createCourse(department_name, int(course_code), course_name)
            except ValueError as e:
                context = {
                    "user": user,
                    "course_list": getAllCourses(),
                    "instructor_list": getUsersByType("INSTRUCTOR"),
                    "ta_list": getUsersByType("TA"),
                    "error_msg": str(e),
                }
                return render(request, "scheduler_app/manage_courses.html", context)

        elif action == "delete_course":
            department_name = request.POST.get("department_name")
            course_code = request.POST.get("course_code")
            try:
                deleteCourse(department_name, int(course_code))
            except ValueError as e:
                pass

        elif action == "create_section":
            department_name = request.POST.get("department_name")
            course_code = request.POST.get("course_code")
            section_code = request.POST.get("section_code")
            section_type = request.POST.get("section_type")
            try:
                createSection(department_name, int(course_code), int(section_code), section_type=section_type)
            except ValueError as e:
                context = {
                    "user": user,
                    "course_list": getAllCourses(),
                    "instructor_list": getUsersByType("INSTRUCTOR"),
                    "ta_list": getUsersByType("TA"),
                    "error_msg": str(e),
                }
                return render(request, "scheduler_app/manage_courses.html", context)

        elif action == "delete_section":
            department_name = request.POST.get("department_name")
            course_code = request.POST.get("course_code")
            section_code = request.POST.get("section_code")
            try:
                deleteSection(department_name, int(course_code), int(section_code))
            except ValueError:
                pass

        elif action == "assign_instructor":
            department_name = request.POST.get("department_name")
            course_code = request.POST.get("course_code")
            section_code = request.POST.get("section_code")
            instructor_email = request.POST.get("instructor_email")
            try:
                assignInstructor(department_name, int(course_code), int(section_code), instructor_email)
            except ValueError:
                pass

        elif action == "assign_ta":
            department_name = request.POST.get("department_name")
            course_code = request.POST.get("course_code")
            section_code = request.POST.get("section_code")
            ta_email = request.POST.get("ta_email")
            try:
                assignTA(department_name, int(course_code), int(section_code), ta_email)
            except ValueError:
                pass

        return redirect("/admin/courses/")

from classes.UserDatabase import getUser
from classes.SectionsDatabase import getSectionsByInstructor

class InstructorDashboardView(View):
    def get(self, request):
        user = getUser(request.session.get("user_id"))

        if user is None or user.getType() != "INSTRUCTOR":
            return redirect("/")

        sections = getSectionsByInstructor(user.getEmail())

        context = {
            "user": user,
            "sections": sections,
        }

        return render(request, "scheduler_app/instructor_dashboard.html", context)

    def post(self, request):
        return redirect("/instructor/dashboard/")

from classes.UserDatabase import getUser
from classes.SectionsDatabase import getSectionsByTA

class TADashboardView(View):
    def get(self, request):
        user = getUser(request.session.get("user_id"))

        if user is None or user.getType() != "TA":
            return redirect("/")

        sections = getSectionsByTA(user.getEmail())

        context = {
            "user": user,
            "sections": sections,
        }

        return render(request, "scheduler_app/ta_dashboard.html", context)

    def post(self, request):
        return redirect("/ta/dashboard/")
# class TADashboardView(View):
#     def get(self, request):
#         # 1. Check that the logged-in user is a TA
#         user_id = request.session.get('user_id')
#         user_type = request.session.get('user_type')
#         if not user_id or user_type != 'ta':
#             return redirect('/login/')
#
#         # Look up the TA record from the database
#         try:
#             ta_user = AssistantUser.objects.get(id=user_id)
#         except AssistantUser.DoesNotExist:
#             return redirect('/login/')
#
#         # Query all lectures assigned to this TA
#         my_lectures = Lecture.objects.filter(TA=ta_user)
#
#         # Query upcoming office hours for this TA
#         upcoming_office_hours = my_lectures.filter(TAOfficeHoursApproved=True)
#
#         # Query upcoming unapproved office hours for this TA
#         pending_office_hours = my_lectures.filter(TAOfficeHoursApproved=False)
#
#         # Bundle data for the template
#         context = {
#             'ta_user': ta_user,
#             'my_lectures': my_lectures,
#             'upcoming_office_hours': upcoming_office_hours,
#             'pending_office_hours': pending_office_hours,
#         }
#
#         # Render the template
#         return render(request, 'scheduler_app/ta_dashboard.html', context)
#
#         def post(self, request):
#             # like the design doc says, POST is navigation only so there's nothing to handle here.
#             return redirect('/ta/dashboard/')
