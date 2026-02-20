from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from academics.models import Announcement

@login_required
@require_POST
def mark_announcement_read(request, announcement_id):
    try:
        announcement = Announcement.objects.get(id=announcement_id)
        announcement.read_by.add(request.user)
        return JsonResponse({'success': True})
    except Announcement.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Announcement not found'}, status=404)
