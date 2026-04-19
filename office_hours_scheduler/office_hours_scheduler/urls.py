"""
URL configuration for office_hours_scheduler project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from scheduler_app.views import *

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', Home.as_view()), #Login Page
    path('admin/dashboard/', AdminDashboardView.as_view()),
    #path('admin/users/', AdminManageUsersView.as_view()),
    #path('admin/lectures/', AdminManageLecturesView.as_view()),
    #path('ta/dashboard/', TADashboardView.as_view()),
    #path('staff/office-hours/propose/', OfficeHourProposalView.as_view()),
    #path('office-hours/', OfficeHoursView.as_view()),
    #path('instructor/office-hours/approve/', InstructorApproveHoursView.as_view()),
    #path('student/reserve/', StudentReserveHoursView.as_view()),
    #path('student/reservations/', StudentReservationsView.as_view()),
    #path('staff/tardy-report/', TardyReportView.as_view()),
]
