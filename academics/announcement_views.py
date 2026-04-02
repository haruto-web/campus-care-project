from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from academics.models import Announcement


def _can_access_announcement(user, announcement):
    class_obj = announcement.class_obj
    if user.role == 'admin':
        return True
    if user.role == 'teacher':
        return class_obj.teacher_id == user.id
    if user.role == 'student':
        return class_obj.students.filter(id=user.id).exists()
    return False


@login_required
@require_POST
def mark_announcement_read(request, announcement_id):
    try:
        announcement = Announcement.objects.get(id=announcement_id)
        if not _can_access_announcement(request.user, announcement):
            return JsonResponse({'success': False, 'error': 'Permission denied'}, status=403)
        announcement.read_by.add(request.user)
        return JsonResponse({'success': True})
    except Announcement.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Announcement not found'}, status=404)

@login_required
@require_POST
def toggle_announcement_read(request, announcement_id):
    try:
        announcement = Announcement.objects.get(id=announcement_id)
        if not _can_access_announcement(request.user, announcement):
            return JsonResponse({'success': False, 'error': 'Permission denied'}, status=403)
        if announcement.read_by.filter(id=request.user.id).exists():
            announcement.read_by.remove(request.user)
            is_read = False
        else:
            announcement.read_by.add(request.user)
            is_read = True
        return JsonResponse({'success': True, 'is_read': is_read})
    except Announcement.DoesNotExist:
        return JsonResponse({'success': False}, status=404)
