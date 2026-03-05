import requests
from django.conf import settings


def send_otp_email(email, code):
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

