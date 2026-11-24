from django.urls import path
from . import views

app_name = 'academics'

urlpatterns = [
    path('uploads/', views.student_uploads, name='uploads'),
    path('uploads/<int:submission_id>/', views.submission_detail, name='submission_detail'),
    path('uploads/<int:submission_id>/download/', views.secure_download, name='secure_download'),
]
