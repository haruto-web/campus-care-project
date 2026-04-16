from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, OTPCode, AuditLog

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ['username', 'email', 'role', 'first_name', 'last_name', 'section', 'year_level']
    list_filter = ['role', 'is_staff', 'is_active']
    fieldsets = UserAdmin.fieldsets + (
        ('Additional Info', {'fields': ('role', 'phone', 'profile_picture', 'year_level', 'section', 'subject', 'id_picture', 'about_me', 'profile_completed')}),
    )

@admin.register(OTPCode)
class OTPCodeAdmin(admin.ModelAdmin):
    list_display = ['contact_value', 'created_at', 'is_used', 'code_hash']
    list_filter = ['is_used']


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ['timestamp', 'actor', 'action', 'target_type', 'target_label', 'ip_address']
    list_filter = ['action', 'timestamp']
    search_fields = ['actor__username', 'actor__first_name', 'actor__last_name', 'target_type', 'target_label', 'ip_address']
    readonly_fields = [field.name for field in AuditLog._meta.fields]
    ordering = ['-timestamp']

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
