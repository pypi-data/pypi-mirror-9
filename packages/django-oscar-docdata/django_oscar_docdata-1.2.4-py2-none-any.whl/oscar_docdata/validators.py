from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ValidationError
from django.core.validators import MinLengthValidator, MaxLengthValidator

__all__ = (
    'validate_postal_code',
)

_validate_min1 = MinLengthValidator(1)
_validate_max50 = MaxLengthValidator(50)
_validate_max35 = MaxLengthValidator(35)

validate_string35 = MaxLengthValidator(35)  # NOTE: value should be converted to normalizedString


def _validate_nmtoken(value):
    # NMTOKEN contains unicode chars, digits, and various interpunction chars.
    # If you want a regexp for that, see:
    # http://sourceforge.net/p/pyxb/code/ci/master/tree/pyxb/utils/unicode.py#l691
    # For now, stick with the obvious exclusions.

    # avoid entering things like N/A
    if '/' in value \
    or ' ' in value:
        raise ValidationError(_('Enter a valid value.'), code='nmtoken')


def _validate_simple_nmtoken(value):
    _validate_nmtoken(value)
    #_validate_min1(value)
    _validate_max50(value)


def validate_postal_code(value):
    """
    Validate a Postal code to send to Docdata.

    This only performs simple validations,
    there is no complete NMTOKEN validation built in right now.
    """
    _validate_simple_nmtoken(value)
