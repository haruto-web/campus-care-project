from django.urls import path
from . import views
from . import announcement_views

app_name = 'academics'

urlpatterns = [
    path('my-classes/', views.my_classes, name='my_classes'),
    path('create/', views.create_class, name='create_class'),
    path('class/<int:class_id>/', views.class_detail, name='class_detail'),
    path('class/<int:class_id>/edit/', views.edit_class, name='edit_class'),
    path('class/<int:class_id>/announcement/create/', views.create_announcement, name='create_announcement'),
    path('announcement/<int:announcement_id>/mark-read/', announcement_views.mark_announcement_read, name='mark_announcement_read'),
    path('class/<int:class_id>/students/', views.manage_students, name='manage_students'),
    path('class/<int:class_id>/students/add/<int:student_id>/', views.add_student, name='add_student'),
    path('class/<int:class_id>/students/drop/<int:student_id>/', views.drop_student, name='drop_student'),
    path('class/<int:class_id>/assignment/create/', views.create_assignment, name='create_assignment'),
    path('class/<int:class_id>/attendance/', views.mark_attendance, name='mark_attendance'),
    path('class/<int:class_id>/assignment/<int:assignment_id>/submissions/', views.view_submissions, name='view_submissions'),
    path('submission/<int:submission_id>/grade/', views.grade_submission, name='grade_submission'),
    path('class/<int:class_id>/material/upload/', views.upload_material, name='upload_material'),
    path('material/<int:material_id>/delete/', views.delete_material, name='delete_material'),
    
    # Student URLs
    path('student/announcements/', views.student_announcements, name='student_announcements'),
    path('student/materials/', views.student_materials, name='student_materials'),
    path('student/assignments/', views.student_assignments, name='student_assignments'),
    path('student/assignment/<int:assignment_id>/submit/', views.submit_assignment, name='submit_assignment'),
    path('student/grades/', views.student_grades, name='student_grades'),
    path('student/attendance/', views.student_attendance, name='student_attendance'),
]
