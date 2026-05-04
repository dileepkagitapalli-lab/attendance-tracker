from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('subject/<str:subject_name>/', views.subject_detail, name='subject_detail'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('timetable/', views.timetable_manage, name='timetable_manage'),
    path('timetable/summary/', views.timetable_summary, name='timetable_summary'),
    path('timetable/delete/<int:pk>/', views.timetable_delete, name='timetable_delete'),
    path('semester-info/', views.semester_info_update, name='semester_info_update'),
    path('mark-working-day/', views.mark_working_day, name='mark_working_day'),
    path('extra-class/', views.extra_class_manage, name='extra_class_manage'),
    path('mark-attendance/', views.mark_attendance, name='mark_attendance'),
    path('calendar/', views.attendance_calendar, name='attendance_calendar'),
    path('export-pdf/', views.export_pdf, name='export_pdf'),
    path('export-excel/', views.export_excel, name='export_excel'),
]
