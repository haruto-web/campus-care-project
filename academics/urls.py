from django.urls import path
from . import views
from . import announcement_views

app_name = 'academics'

urlpatterns = [
    path('my-classes/', views.my_classes, name='my_classes'),
    path('student/schedule/export/', views.export_student_schedule, name='export_student_schedule'),
    path('student/grades/export/', views.export_student_grades, name='export_student_grades'),
    path('create/', views.create_class, name='create_class'),
    path('class/<int:class_id>/', views.class_detail, name='class_detail'),
    path('class/<int:class_id>/edit/', views.edit_class, name='edit_class'),
    path('class/<int:class_id>/announcement/create/', views.create_announcement, name='create_announcement'),
    path('class/<int:class_id>/announcement/<int:announcement_id>/edit/', views.edit_announcement, name='edit_announcement'),
    path('announcement/<int:announcement_id>/delete/', views.delete_announcement, name='delete_announcement'),
    path('announcement/undo/<str:token>/', views.undo_announcement_delete, name='undo_announcement_delete'),
    path('announcement/<int:announcement_id>/mark-read/', announcement_views.mark_announcement_read, name='mark_announcement_read'),
    path('announcement/<int:announcement_id>/toggle-read/', announcement_views.toggle_announcement_read, name='toggle_announcement_read'),
    path('class/<int:class_id>/students/', views.manage_students, name='manage_students'),
    path('class/<int:class_id>/students/add/<int:student_id>/', views.add_student, name='add_student'),
    path('class/<int:class_id>/students/bulk-add/', views.bulk_add_students, name='bulk_add_students'),
    path('class/<int:class_id>/students/drop/<int:student_id>/', views.drop_student, name='drop_student'),
    path('class/students/undo-drop/<str:token>/', views.undo_drop_student, name='undo_drop_student'),
    path('class/<int:class_id>/assignment/create/', views.create_assignment, name='create_assignment'),
    path('class/<int:class_id>/assignment/<int:assignment_id>/edit/', views.edit_assignment, name='edit_assignment'),
    path('class/<int:class_id>/attendance/', views.mark_attendance, name='mark_attendance'),
    path('class/<int:class_id>/attendance/update/', views.update_attendance_ajax, name='update_attendance_ajax'),
    path('class/<int:class_id>/assignment/<int:assignment_id>/submissions/', views.view_submissions, name='view_submissions'),
    path('submission/<int:submission_id>/grade/', views.grade_submission, name='grade_submission'),
    path('submission/<int:submission_id>/comment/', views.comment_submission, name='comment_submission'),
    path('class/<int:class_id>/material/upload/', views.upload_material, name='upload_material'),
    path('class/<int:class_id>/material/<int:material_id>/edit/', views.edit_material, name='edit_material'),
    path('material/<int:material_id>/delete/', views.delete_material, name='delete_material'),
    path('material/undo/<str:token>/', views.undo_material_delete, name='undo_material_delete'),
    
    path('assignment/<int:assignment_id>/delete/', views.delete_assignment, name='delete_assignment'),
    path('assignment/undo/<str:token>/', views.undo_assignment_delete, name='undo_assignment_delete'),
    # Student URLs
    path('student/announcements/', views.student_announcements, name='student_announcements'),
    path('student/materials/', views.student_materials, name='student_materials'),
    path('student/assignments/', views.student_assignments, name='student_assignments'),
    path('student/assignment/<int:assignment_id>/submit/', views.submit_assignment, name='submit_assignment'),
    path('student/grades/', views.student_grades, name='student_grades'),
    path('student/attendance/', views.student_attendance, name='student_attendance'),
]
