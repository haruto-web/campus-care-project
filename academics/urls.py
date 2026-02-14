from django.urls import path
from . import views

app_name = 'academics'

urlpatterns = [
    path('create/', views.create_class, name='create_class'),
    path('class/<int:class_id>/', views.class_detail, name='class_detail'),
    path('class/<int:class_id>/announcement/create/', views.create_announcement, name='create_announcement'),
    path('class/<int:class_id>/students/', views.manage_students, name='manage_students'),
    path('class/<int:class_id>/students/add/<int:student_id>/', views.add_student, name='add_student'),
    path('class/<int:class_id>/students/remove/<int:student_id>/', views.remove_student, name='remove_student'),
]
