from django.shortcuts import render, redirect
from django.views import View
from .models import Lecture, AdminUser, InstructorUser, AssistantUser, StudentUser
from django.db.models import Q

#Login view
class Home(View):
    def get(self,request):
        return render(request,"scheduler_app/login.html",{})

    def post(self, request):
        identifier = request.POST.get('username')
        password = request.POST.get('password')

        bad_password = False
        # Check Admin
        try:
            user = StudentUser.objects.get(Q(username=identifier) | Q(email=identifier))
            bad_password = (user.password != password)
            if bad_password: return render(request, 'scheduler_app/login.html', {"message":"incorrect password"})
            request.session['user_id'] = user.username
            request.session['user_type'] = 'admin'
            return redirect('/admin/dashboard/')
        except AdminUser.DoesNotExist:
            pass

        # Check Instructor
        try:
            user = InstructorUser.objects.get(Q(username=identifier) | Q(email=identifier))
            bad_password = (user.password != password)
            if bad_password: return render(request, 'scheduler_app/login.html', {"message": "incorrect password"})
            request.session['user_id'] = user.username
            request.session['user_type'] = 'instructor'
            return redirect('/instructor/dashboard/')
        except InstructorUser.DoesNotExist:
            pass

        # Check Student
        try:
            user = StudentUser.objects.get(Q(username=identifier) | Q(email=identifier))
            bad_password = (user.password != password)
            if bad_password: return render(request, 'scheduler_app/login.html', {"message": "incorrect password"})
            request.session['user_id'] = user.username
            request.session['user_type'] = 'student'
            return redirect('/student/dashboard/')
        except StudentUser.DoesNotExist:
            pass

        # Check TA
        try:
            user = AssistantUser.objects.get(Q(username=identifier) | Q(email=identifier))
            bad_password = (user.password != password)
            if bad_password: return render(request, 'scheduler_app/login.html', {"message": "incorrect password"})
            request.session['user_id'] = user.username
            request.session['user_type'] = 'ta'
            return redirect('/ta/dashboard/')
        except AssistantUser.DoesNotExist:
            pass

        # If no match
        return render(request, 'scheduler_app/login.html', {"message":"no such user"})

class AdminDashboardView(View):
    def get(self, request):
        # 1. Check that the logged-in user is an admin
        user_id = request.session.get('user_id')
        user_type = request.session.get('user_type')
        if not user_id or user_type != 'admin':
            return redirect('/login/')

        # Look up the admin record from the database
        try:
            admin_user = AdminUser.objects.get(id=user_id)
        except AdminUser.DoesNotExist:
            return redirect('/login/')

        # Query all lectures
        lecture_list = Lecture.objects.all()

        # Compute summary counts
        ta_count = AssistantUser.objects.count()
        instructor_count = InstructorUser.objects.count()

        # Bundle data for the template
        context = {
            'user': admin_user,
            'lecture_list': lecture_list,
            'ta_count': ta_count,
            'instructor_count': instructor_count,
        }

        # Render the template
        return render(request, 'scheduler_app/admin_dashboard.html', context)

    def post(self, request):
        # like the design doc says, POST is navigation only so there's nothing to handle here.
        return redirect('/admin/dashboard/')

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
    ################ Create next View here #########################