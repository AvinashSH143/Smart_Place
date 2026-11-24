from django.urls import path
from . import views

app_name = 'students'

urlpatterns = [
    path('dashboard/', views.student_dashboard, name='dashboard'),
    path('profile/', views.student_profile, name='profile'),
    path('profile/skills/add/', views.add_student_skill, name='add_skill'),
    path('profile/skills/<int:skill_id>/delete/', views.delete_student_skill, name='delete_skill'),
]
