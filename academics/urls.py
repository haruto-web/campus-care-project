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
    path('class/<int:class_id>/assignment/create/', views.create_assignment, name='create_assignment'),
    path('class/<int:class_id>/attendance/', views.mark_attendance, name='mark_attendance'),
    path('class/<int:class_id>/assignment/<int:assignment_id>/submissions/', views.view_submissions, name='view_submissions'),
    path('submission/<int:submission_id>/grade/', views.grade_submission, name='grade_submission'),
    path('class/<int:class_id>/material/upload/', views.upload_material, name='upload_material'),
    path('material/<int:material_id>/delete/', views.delete_material, name='delete_material'),
]
