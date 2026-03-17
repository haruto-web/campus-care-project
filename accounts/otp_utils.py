import requests
from django.conf import settings


def send_otp_email(email, code):
    requests.post(
        'https://api.brevo.com/v3/smtp/email',
        headers={
            'api-key': settings.BREVO_API_KEY,
            'Content-Type': 'application/json',
        },
        json={
            'sender': {'name': 'BrightTrack', 'email': settings.EMAIL_HOST_USER},
            'to': [{'email': email}],
            'subject': 'Your BrightTrack Verification Code',
            'textContent': f'Your verification code is: {code}\n\nThis code expires in 3 minutes.',
        },
    )


def send_transactional_email(to_email, subject, text_content):
    """Generic Brevo email sender. Fails silently."""
    try:
        requests.post(
            'https://api.brevo.com/v3/smtp/email',
            headers={
                'api-key': settings.BREVO_API_KEY,
                'Content-Type': 'application/json',
            },
            json={
                'sender': {'name': 'BrightTrack', 'email': settings.EMAIL_HOST_USER},
                'to': [{'email': to_email}],
                'subject': subject,
                'textContent': text_content,
            },
            timeout=10,
        )
    except Exception:
        pass
