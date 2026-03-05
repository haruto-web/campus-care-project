from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.shortcuts import redirect

class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    def pre_social_login(self, request, sociallogin):
        # Block Google OAuth for new student registrations — use OTP instead
        if sociallogin.is_existing:
            return
        if 'email' in sociallogin.account.extra_data:
            email = sociallogin.account.extra_data['email']
            from .models import User
            try:
                user = User.objects.get(email=email)
                sociallogin.connect(request, user)
            except User.DoesNotExist:
                from allauth.exceptions import ImmediateHttpResponse
                from django.shortcuts import redirect
                from django.contrib import messages
                messages.error(request, 'Students must register using email OTP. Please use the student login page.')
                raise ImmediateHttpResponse(redirect('otp_request'))
    
    def save_user(self, request, sociallogin, form=None):
        user = super().save_user(request, sociallogin, form)
        # Set default role to student for Google sign-ups
        user.role = 'student'
        
        # Extract name from Google data
        data = sociallogin.account.extra_data
        if 'given_name' in data:
            user.first_name = data['given_name']
        if 'family_name' in data:
            user.last_name = data['family_name']
        
        # Generate username from email
        if not user.username:
            user.username = user.email.split('@')[0]
        
        user.save()
        return user
