import re

from django.core.exceptions import ValidationError


class ComplexityPasswordValidator:
    def validate(self, password, user=None):
        errors = []

        if not re.search(r'[A-Z]', password):
            errors.append('Password must contain at least one uppercase letter.')

        if not re.search(r'[a-z]', password):
            errors.append('Password must contain at least one lowercase letter.')

        if not re.search(r'\d', password):
            errors.append('Password must contain at least one number.')

        if errors:
            raise ValidationError(errors)

    def get_help_text(self):
        return (
            'Your password must contain at least one uppercase letter, '
            'one lowercase letter, and one number.'
        )