from re import match
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


def place_value_validator(value):
    """Validate place value.
    
    For more information check provided raises error.
    """
    if not value.isdigit() and match(r'^\d{1,2}-\d{1,2}$', value):
        raise ValidationError(
            _(
                'The place values must de a digit string or matches with '
                '99-99 pattern, but %(value)s was given.',
            ), params={'value': value}
        )
