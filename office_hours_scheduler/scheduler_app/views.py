from django.contrib.auth import logout
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
from classes.OfficeHoursDatabase import createOfficeHour, getOfficeHour, getApprovedOfficeHours, getPendingOfficeHoursForInstructor, rejectOfficeHour, approveOfficeHour
from classes.TimeSlot import TimeSlot

DASHBOARD_ROUTES = {
    "INSTRUCTOR": "/instructor/dashboard/",
    "TA": "/ta/dashboard/",
    "STUDENT": "/student/dashboard/",
    "ADMIN": "/admin/dashboard/",
}

class AccountSelectView(View):
    def get(self, request):
        return render(request, "scheduler_app/account_select.html", {})

class Home(View): # staff login
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

        # Students cannot log in via the staff portal
        if user.getType() == "STUDENT":
            return render(request, "scheduler_app/login.html", {"message": "Please use the student login"})

        route = DASHBOARD_ROUTES.get(user.getType())
        if route is None:
            return render(request, "scheduler_app/login.html", {"message": "Unknown user type"})

        return redirect(route)

class StudentLoginView(View):
    def get(self, request):
        return render(request, "scheduler_app/student_login.html", {})
    ##### I just pasted the original login view, needs to be updated
    def post(self, request):
        email = request.POST.get("email")
        #password = request.POST.get("password")

        if not doesUserWithEmailExist(email):
            return render(request, "scheduler_app/student_login.html", {"message": "No such user"})

        user = UserClass(email)
        request.session["user_id"] = user.getEmail()
        request.session["user_type"] = user.getType()

        # Staff cannot log in via the student portal
        if user.getType() != "STUDENT":
            return render(request, "scheduler_app/student_login.html", {"message": "Please use the staff login"})

        #return redirect(DASHBOARD_ROUTES["STUDENT"])

        return redirect("/set/password/")

class SetPasswordView(View):
    def get(self, request):
        return render(request, "scheduler_app/set_password.html", {})

    ##### I just pasted the original login view, needs to be updated
    def post(self, request):
        #email = request.POST.get("email")
        password = request.POST.get("password")

        #user = UserClass(email)
        #request.session["user_id"] = user.getEmail()
        #request.session["user_type"] = user.getType()

        # Staff cannot log in via the student portal
        #if user.getType() != "STUDENT":
            #return render(request, "scheduler_app/student_login.html", {"message": "Please use the staff login"})

        return redirect(DASHBOARD_ROUTES["STUDENT"])

class StudentPasswordView(View):
    def get(self, request):
        return render(request, "scheduler_app/student_enter_password.html", {})

    ##### I just pasted the original login view, needs to be updated
    def post(self, request):
        #email = request.POST.get("email")
        password = request.POST.get("password")

        #user = UserClass(email)
        #request.session["user_id"] = user.getEmail()
        #request.session["user_type"] = user.getType()

        # Staff cannot log in via the student portal
        #if user.getType() != "STUDENT":
            #return render(request, "scheduler_app/student_login.html", {"message": "Please use the staff login"})

        return redirect(DASHBOARD_ROUTES["STUDENT"])


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

class StudentDashboardView(View):
    def get(self, request):
        user = request.session.get("user_id")

        if user is None or request.session.get("user_type") != "STUDENT":
            return redirect("{% url 'student-login' %}")

        #sections = getSectionsByTA(user.getEmail())

        context = {
            "user": user,
            "courses": [],
        }

        return render(request, "scheduler_app/student_dashboard.html", context)

    def post(self, request):
        return redirect("/student/dashboard/")

def logout_view(request):
    logout(request)
    return render(request, "scheduler_app/logout.html")


class ApproveOfficeHoursView(View):
    def get(self, request):
        user = getUser(request.session.get("user_id"))

        if user is None or user.getType() != "INSTRUCTOR":
            return redirect("/")

        context = {
            "user": user,
            "pending_office_hours": getPendingOfficeHoursForInstructor(user.getEmail()),
        }

        return render(request, "scheduler_app/approve_office_hours.html", context)

    def post(self, request):
        user = getUser(request.session.get("user_id"))

        if user is None or user.getType() != "INSTRUCTOR":
            return redirect("/")

        action = request.POST.get("action")
        office_hour_id = request.POST.get("office_hours_id")

        if not office_hour_id:
            return redirect("/instructor/office-hours/approve/")

        try:
            if action == "approve":
                approveOfficeHour(int(office_hour_id))
            elif action == "reject":
                rejectOfficeHour(int(office_hour_id))
        except (ValueError, TypeError):
            # Office hour doesn't exist or invalid id; silently ignore
            pass
        return redirect("/instructor/office-hours/approve/")

class ViewOfficeHoursView(View):
    def get(self, request):
        user = getUser(request.session.get("user_id"))
        if user is None:
            return redirect("/")

        lecture_str = request.GET.get("lecture", "").strip()
        ta_email = request.GET.get("ta", "").strip()

        course_filter = None
        if lecture_str:
            try:
                course_filter = int(lecture_str)
            except ValueError:
                course_filter = None

        staff_filter = ta_email or None

        context = {
            "user": user,
            "ta_office_hours_list": getApprovedOfficeHours(
                course_filter=course_filter,
                staff_filter=staff_filter,
            ),
            "lecture_filter": lecture_str,
            "ta_filter": ta_email,
        }
        return render(request, "scheduler_app/view_office_hours.html", context)

########################################################################################################################

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
class ProposeOfficeHoursView(View):
    def get(self, request):
        user = getUser(request.session.get("user_id"))

        if user is not None and user.getType() == "INSTRUCTOR":
            sections = getSectionsByInstructor(user.getEmail())
        elif user is not None and user.getType() == "TA":
            sections = getSectionsByTA(user.getEmail())
        else:
            return redirect("/")

        # Deduplicate by course code, keeping only one section per course
        seen_courses = set()
        unique_sections = []
        for section in sections:
            course_code = section.getCourse().getCourseCode()
            if course_code not in seen_courses:
                seen_courses.add(course_code)
                unique_sections.append(section)

        approved_hours = getApprovedOfficeHours(staff_filter=user.getEmail())
        context = {
            "user": user,
            "sections": unique_sections,
            "all_sections": sections,
            "approved_hours": approved_hours,
        }

        return render(request, "scheduler_app/propose_office_hours.html", context)

    def post(self, request):
        user = getUser(request.session.get("user_id"))

        if user is None or (user.getType() != "TA" and user.getType() != "INSTRUCTOR"):
            return redirect("/")

        # Re-fetch sections for this user
        if user.getType() == "INSTRUCTOR":
            sections = getSectionsByInstructor(user.getEmail())
        else:
            sections = getSectionsByTA(user.getEmail())

        section_code = request.POST.get("section_selection")
        if not section_code:
            return redirect("/staff/office-hours/propose/")

        # Find the matching section from the fetched list
        selected_section = next(
            (s for s in sections if s.getSectionCode() == section_code), None
        )
        if selected_section is None:
            return redirect("/staff/office-hours/propose/")

        # Extract day booleans
        days = {
            'monday': request.POST.get('monday') == 'on',
            'tuesday': request.POST.get('tuesday') == 'on',
            'wednesday': request.POST.get('wednesday') == 'on',
            'thursday': request.POST.get('thursday') == 'on',
            'friday': request.POST.get('friday') == 'on',
        }

        if not any(days.values()):
            return redirect("/staff/office-hours/propose/")

        if not any(days.values()):
            return redirect("/staff/office-hours/propose/")

        # Extract and validate time fields
        try:
            start_hour = int(request.POST.get('start_hour'))
            start_minutes = int(request.POST.get('start_minutes'))
            end_hour = int(request.POST.get('end_hour'))
            end_minutes = int(request.POST.get('end_minutes'))
        except (TypeError, ValueError):
            return redirect("/staff/office-hours/propose/")

        if not (0 <= start_hour <= 23 and 0 <= end_hour <= 23):
            return redirect("/staff/office-hours/propose/")
        if not (0 <= start_minutes <= 59 and 0 <= end_minutes <= 59):
            return redirect("/staff/office-hours/propose/")

        start_total = start_hour * 60 + start_minutes
        end_total = end_hour * 60 + end_minutes

        if end_total <= start_total:
            return redirect("/staff/office-hours/propose/")

        # Format as HH:MM strings for the Timeslot model
        start_time = f"{start_hour:02d}:{start_minutes:02d}"
        end_time = f"{end_hour:02d}:{end_minutes:02d}"

        office_hours = createOfficeHour(user.getEmail(), selected_section, start_time, end_time, days)

        if user.getType() == "INSTRUCTOR":
            office_hours.setApproved(True)

        return redirect("/office-hours/")

