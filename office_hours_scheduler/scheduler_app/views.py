from django.shortcuts import render, redirect
from django.views import View
from .models import Lecture, AdminUser, InstructorUser, AssistantUser, StudentUser
from django.db.models import Q

#Login view
from django.views import View
from django.shortcuts import render, redirect
from classes.Users import UserClass

from django.views import View
from django.shortcuts import render, redirect
from classes.Users import UserClass
from classes.UserDatabase import getUsersByType, countByType
from classes.CourseDatabase import getAllCourses

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

        user = getUser(email)
        request.session["user_id"] = user.getEmail()
        request.session["user_type"] = user.getType()

        route = DASHBOARD_ROUTES.get(user.getType())
        if route is None:
            return render(request, "scheduler_app/login.html", {"message": "Unknown user type"})

        return redirect(route)





    class AdminDashboardView(View):
        def get(self, request):
            user = UserClass(request.session.get("user_id"))

            if not user.exists() or user.getType() != "ADMIN":
                return redirect("/")

            context = {
                "user": user,
                "ta_count": countByType("TA"),
                "instructor_count": countByType("INSTRUCTOR"),
                "course_list": getAllCourses(),
            }

            return render(request, "scheduler_app/admin_dashboard.html", context)

        def post(self, request):
            pass

    ################ Create next View here #########################
class TADashboardView(View):
    def get(self, request):
        # 1. Check that the logged-in user is a TA
        user_id = request.session.get('user_id')
        user_type = request.session.get('user_type')
        if not user_id or user_type != 'ta':
            return redirect('/login/')

        # Look up the TA record from the database
        try:
            ta_user = AssistantUser.objects.get(id=user_id)
        except AssistantUser.DoesNotExist:
            return redirect('/login/')

        # Query all lectures assigned to this TA
        my_lectures = Lecture.objects.filter(TA=ta_user)

        # Query upcoming office hours for this TA
        upcoming_office_hours = my_lectures.filter(TAOfficeHoursApproved=True)

        # Query upcoming unapproved office hours for this TA
        pending_office_hours = my_lectures.filter(TAOfficeHoursApproved=False)

        # Bundle data for the template
        context = {
            'ta_user': ta_user,
            'my_lectures': my_lectures,
            'upcoming_office_hours': upcoming_office_hours,
            'pending_office_hours': pending_office_hours,
        }

        # Render the template
        return render(request, 'scheduler_app/ta_dashboard.html', context)

        def post(self, request):
            # like the design doc says, POST is navigation only so there's nothing to handle here.
            return redirect('/ta/dashboard/')
