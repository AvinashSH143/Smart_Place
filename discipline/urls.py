from django.urls import path
from . import views

app_name = 'discipline'

urlpatterns = [
    path('discipline/', views.student_discipline_view, name='discipline_view'),
    path('discipline/appeal/<int:record_id>/', views.submit_appeal_view, name='submit_appeal'),
]
