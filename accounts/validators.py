import re
from django.core.exceptions import ValidationError


class StrongPasswordValidator:
    def validate(self, password, user=None):
        errors = []
        if not re.search(r'[A-Z]', password):
            errors.append('Password must contain at least 1 uppercase letter.')
        if not re.search(r'[0-9]', password):
            errors.append('Password must contain at least 1 number.')
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            errors.append('Password must contain at least 1 special character.')
        if errors:
            raise ValidationError(errors)

    def get_help_text(self):
        return 'Password must contain at least 1 uppercase letter, 1 number, and 1 special character.'
