from django.urls import path
from . import admin_views

app_name = 'admin_dashboard'

urlpatterns = [
    path('', admin_views.admin_dashboard_home, name='dashboard'),
    
    # Student Management
    path('students/', admin_views.admin_students_list, name='students_list'),
    path('students/<int:student_id>/', admin_views.admin_student_detail, name='student_detail'),
    
    # Academic Evaluations
    path('evaluations/', admin_views.admin_evaluations_list, name='evaluations_list'),
    path('evaluations/<int:submission_id>/', admin_views.admin_evaluate_submission, name='evaluate_submission'),
    
    # Companies
    path('companies/', admin_views.admin_companies_list, name='companies_list'),
    path('companies/create/', admin_views.admin_company_create, name='company_create'),
    path('companies/<int:company_id>/edit/', admin_views.admin_company_edit, name='company_edit'),
    
    # Placement Drives
    path('drives/', admin_views.admin_drives_list, name='drives_list'),
    path('drives/create/', admin_views.admin_drive_create, name='drive_create'),
    path('drives/<int:drive_id>/edit/', admin_views.admin_drive_edit, name='drive_edit'),
    path('drives/<int:drive_id>/toggle/', admin_views.admin_drive_toggle_status, name='drive_toggle'),
    path('drives/<int:drive_id>/delete/', admin_views.admin_drive_delete, name='drive_delete'),
    
    # Discipline & Debarment
    path('discipline/', admin_views.admin_discipline_list, name='discipline_list'),
    path('discipline/create/', admin_views.admin_discipline_create, name='discipline_create'),
    path('discipline/<int:record_id>/status/<str:new_status>/', admin_views.admin_discipline_update_status, name='discipline_status'),
    path('discipline/<int:record_id>/debar/', admin_views.admin_debar_student, name='debar_student'),
    path('discipline/<int:record_id>/reinstate/', admin_views.admin_reinstate_student, name='reinstate_student'),
    path('discipline/<int:record_id>/delete/', admin_views.admin_discipline_delete, name='discipline_delete'),
    path('appeals/<int:appeal_id>/review/', admin_views.admin_appeal_review, name='appeal_review'),
]
