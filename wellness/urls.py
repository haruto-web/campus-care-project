from django.urls import path
from . import views

app_name = 'wellness'

urlpatterns = [
    path('concern/create/', views.create_concern, name='create_concern'),
    path('concern/create/<int:student_id>/', views.create_concern, name='create_concern_for_student'),
    path('concerns/', views.view_concerns, name='view_concerns'),
]
