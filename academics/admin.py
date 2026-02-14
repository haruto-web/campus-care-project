from django.contrib import admin
from .models import Class, Assignment, Submission, Attendance, Grade

@admin.register(Class)
class ClassAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'teacher', 'semester']
    search_fields = ['code', 'name']

@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ['title', 'class_obj', 'due_date', 'total_points']
    list_filter = ['class_obj', 'due_date']

@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ['student', 'assignment', 'submitted_at', 'score']
    list_filter = ['assignment__class_obj']

@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ['student', 'class_obj', 'date', 'status']
    list_filter = ['status', 'date', 'class_obj']

@admin.register(Grade)
class GradeAdmin(admin.ModelAdmin):
    list_display = ['student', 'class_obj', 'score', 'max_score', 'date']
    list_filter = ['class_obj', 'date']
