from django.shortcuts import render, redirect
from django.views import View
from .models import Lecture, AdminUser, InstructorUser, AssistantUser

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