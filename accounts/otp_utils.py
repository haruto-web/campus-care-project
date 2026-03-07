import requests
from django.conf import settings
from django.core.mail import send_mail


def send_otp_email(email, code):
    if not settings.BREVO_API_KEY or settings.DEBUG:
        send_mail(
            subject='Your BrightTrack Verification Code',
            message=f'Your verification code is: {code}\n\nThis code expires in 10 minutes.',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
        )
        return

    response = requests.post(
        'https://api.brevo.com/v3/smtp/email',
        headers={
            'api-key': settings.BREVO_API_KEY,
            'Content-Type': 'application/json',
        },
        json={
            'sender': {'name': 'BrightTrack', 'email': settings.DEFAULT_FROM_EMAIL},
            'to': [{'email': email}],
            'subject': 'Your BrightTrack Verification Code',
            'textContent': f'Your verification code is: {code}\n\nThis code expires in 10 minutes.',
        },
        timeout=10,
    )
    if response.status_code not in (200, 201):
        raise Exception(f'Brevo API error: {response.text}')
