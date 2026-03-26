from django.contrib import messages
from django.contrib.auth import logout
from django.http import JsonResponse
from django.shortcuts import redirect
from django.urls import reverse


class NoCacheAuthenticatedPagesMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if getattr(request, 'user', None) and request.user.is_authenticated:
            expected_session_key = getattr(request.user, 'current_session_key', '')
            current_session_key = request.session.session_key or ''
            if expected_session_key and current_session_key and expected_session_key != current_session_key:
                logout(request)
                accepts_json = 'application/json' in (request.headers.get('accept') or '').lower()
                is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest' or accepts_json
                if is_ajax:
                    return JsonResponse(
                        {
                            'session_expired': True,
                            'message': 'Session expired. This account was logged in on another device.',
                        },
                        status=440
                    )
                messages.warning(request, 'Session expired. This account was logged in on another device.')
                return redirect(f"{reverse('login')}?session_expired=1")

        response = self.get_response(request)

        if getattr(request, 'user', None) and request.user.is_authenticated:
            response['Cache-Control'] = 'no-cache, no-store, must-revalidate, private'
            response['Pragma'] = 'no-cache'
            response['Expires'] = '0'

        response['Content-Security-Policy'] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' https://cdn.tailwindcss.com https://cdn.jsdelivr.net; "
            "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://fonts.googleapis.com; "
            "font-src 'self' https://fonts.gstatic.com https://cdn.jsdelivr.net data:; "
            "img-src 'self' data: https:; "
            "connect-src 'self'; "
            "media-src 'self' https:; "
            "manifest-src 'self'; "
            "object-src 'none'; "
            "base-uri 'self'; "
            "frame-ancestors 'none'; "
            "frame-src 'none'; "
            "form-action 'self'"
        )
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        response['Permissions-Policy'] = 'camera=(), microphone=(), geolocation=()'

        return response
