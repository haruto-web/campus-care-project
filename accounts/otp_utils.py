from django.core.mail import send_mail
from django.conf import settings
import socket


def send_otp_email(email, code):
    old_timeout = socket.getdefaulttimeout()
    socket.setdefaulttimeout(10)
    try:
        send_mail(
            subject='Your BrightTrack Verification Code',
            message=f'Your verification code is: {code}\n\nThis code expires in 10 minutes. Do not share it with anyone.',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            fail_silently=False,
        )
    finally:
        socket.setdefaulttimeout(old_timeout)
