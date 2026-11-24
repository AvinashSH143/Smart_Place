from django.urls import path
from . import views

app_name = 'companies'

urlpatterns = [
    path('drives/', views.drives_list, name='drives_list'),
    path('drives/<int:drive_id>/', views.drive_detail, name='drive_detail'),
]
