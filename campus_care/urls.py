"""
URL configuration for campus_care project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from accounts.views import protected_media_view
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from ai_assistant import views as ai_assistant_views


@login_required
def cloudinary_check_view(request):
    if not request.user.is_superuser:
        return JsonResponse({'error': 'forbidden'}, status=403)
    try:
        import cloudinary
        import cloudinary.uploader
        cfg = cloudinary.config()
        result = cloudinary.uploader.upload(
            'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==',
            public_id='brighttrack_test_ping',
            overwrite=True,
        )
        return JsonResponse({
            'status': 'ok',
            'cloud_name': cfg.cloud_name,
            'url': result.get('secure_url'),
        })
    except Exception as e:
        return JsonResponse({'status': 'error', 'error': str(e), 'type': type(e).__name__})


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('accounts.urls')),
    path('class/', include('academics.urls')),
    path('wellness/', include('wellness.urls')),
    path('ai/', include('ai_assistant.urls')),
    path('ai-teacher/feedback/<int:submission_id>/', ai_assistant_views.generate_teacher_feedback, name='generate_teacher_feedback'),
    path('messages/', include('messaging.urls')),
    path('debug/cloudinary/', cloudinary_check_view, name='cloudinary_check'),
]

if settings.DEBUG:
    urlpatterns += [
        re_path(r'^media/(?P<path>.*)$', protected_media_view),
    ]
