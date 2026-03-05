from django.urls import path
from . import views
from . import admin_views
from . import report_views
from allauth.socialaccount.providers.google.views import oauth2_login

urlpatterns = [
    path('', views.landing_view, name='landing'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('student/verify/', views.otp_request_view, name='otp_request'),
    path('student/verify/code/', views.otp_verify_view, name='otp_verify'),
    path('student/login/', views.otp_login_password_view, name='otp_login_password'),
    path('student/register/', views.otp_register_view, name='otp_register'),
    path('student/forgot-password/', views.otp_forgot_password_view, name='otp_forgot_password'),
    path('student/reset-password/', views.otp_reset_password_view, name='otp_reset_password'),
    path('student/<int:student_id>/', views.student_profile_view, name='student_profile'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('profile/', views.profile_view, name='profile'),
    path('complete-profile/', views.complete_profile_view, name='complete_profile'),
    path('students/', views.students_list_view, name='students_list'),
    path('google/login/', oauth2_login, name='google_login'),
    path('fix-site/', views.fix_site_domain, name='fix_site_domain'),
    path('notifications/poll/', views.notifications_poll, name='notifications_poll'),
    
    # Admin URLs
    path('manage/users/', admin_views.admin_manage_users, name='admin_manage_users'),
    path('manage/create-user/', admin_views.admin_create_user, name='admin_create_user'),
    path('manage/user/<int:user_id>/delete/', admin_views.admin_delete_user, name='admin_delete_user'),
    path('manage/teachers/', admin_views.admin_teachers_list, name='admin_teachers_list'),
    path('manage/teacher/<int:teacher_id>/dashboard/', admin_views.admin_teacher_dashboard, name='admin_teacher_dashboard'),
    path('manage/create-class/', admin_views.admin_create_class, name='admin_create_class'),
    path('manage/enroll-student/', admin_views.admin_enroll_student, name='admin_enroll_student'),
    path('manage/cleanup-users/', admin_views.admin_cleanup_users, name='admin_cleanup_users'),
    path('manage/create-superuser/', admin_views.admin_create_superuser, name='admin_create_superuser'),
    path('report/download/', report_views.download_report, name='download_report'),
]
