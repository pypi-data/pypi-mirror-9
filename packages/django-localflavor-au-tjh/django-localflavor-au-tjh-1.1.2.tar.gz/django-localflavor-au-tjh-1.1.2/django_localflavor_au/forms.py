"""
Australian-specific Form helpers
"""

from __future__ import absolute_import, unicode_literals

import re

from django_localflavor_au.au_states import STATE_CHOICES
from django_localflavor_au.utils import abn_validator, acn_validator
from django.core.validators import EMPTY_VALUES
from django.forms import ValidationError, CharField
from django.forms.fields import Field, RegexField, Select
from django.utils.encoding import smart_text
from django.utils.translation import ugettext_lazy as _


PHONE_DIGITS_RE = re.compile(r'^(\d{10})$')


class AUPostCodeField(RegexField):
    """ Australian post code field.

    Assumed to be 4 digits.
    Northern Territory 3-digit postcodes should have leading zero.
    """
    default_error_messages = {
        'invalid': _('Enter a 4 digit postcode.'),
    }

    def __init__(self, max_length=4, min_length=None, *args, **kwargs):
        super(AUPostCodeField, self).__init__(
            r'^\d{4}$', max_length, min_length, *args, **kwargs)


class AUPhoneNumberField(CharField):
    """Australian phone number field."""
    default_error_messages = {
        'invalid': 'Phone numbers must contain 10 digits.',
    }

    def __init__(self, default_area_code=None, *args, **kwargs):
        self.default_area_code = default_area_code
        super(AUPhoneNumberField, self).__init__(*args, **kwargs)

    def clean(self, value):
        """
        Validate a phone number. Strips parentheses, whitespace and hyphens.
        """
        super(AUPhoneNumberField, self).clean(value)
        if value in EMPTY_VALUES:
            return ''
        value = re.sub('(\(|\)|\s+|-)', '', smart_text(value))
        if len(value) == 8:
            if self.default_area_code:
                value = self.default_area_code + value
        phone_match = PHONE_DIGITS_RE.search(value)
        if phone_match:
            return value
        raise ValidationError(self.error_messages['invalid'])


class AUStateSelect(Select):
    """
    A Select widget that uses a list of Australian states/territories as its
    choices.
    """
    def __init__(self, attrs=None):
        super(AUStateSelect, self).__init__(attrs, choices=STATE_CHOICES)


class ABNField(CharField):

    SEPERATOR_RE = re.compile('[ /-]')

    def __init__(self, add_spaces=True, *args, **kwargs):
        self.add_spaces = add_spaces

        if add_spaces:
            max_length = 14
        else:
            max_length = 11

        kwargs['max_length'] = max_length

        super(ABNField, self).__init__(*args, **kwargs)

    def clean(self, value):
        # Normalise empty values to the empty string
        if not value:
            return ''

        # Strip spaces out and try and validate it.
        # We allow spaces in the input ABN, because it makes it look nicer
        value = self.SEPERATOR_RE.sub('', value)

        try:
            abn_validator(value)
        except ValueError as e:
            raise ValidationError(e)

        if self.add_spaces:
            return '{0} {1} {2} {3}'.format(
                value[0:2], value[2:5], value[5:8], value[8:12])
        else:
            return value


class ACNField(CharField):

    SEPERATOR_RE = re.compile('[ /-]')

    def __init__(self, add_spaces=True, *args, **kwargs):
        self.add_spaces = add_spaces

        if add_spaces:
            max_length = 11
        else:
            max_length = 9

        kwargs['max_length'] = max_length

        super(ACNField, self).__init__(*args, **kwargs)

    def clean(self, value):
        # Normalise empty values to the empty string
        if not value:
            return ''

        # Strip spaces out and try and validate it.
        # We allow spaces in the input ACN, because it makes it look nicer
        value = self.SEPERATOR_RE.sub('', value)

        try:
            acn_validator(value)
        except ValueError as e:
            raise ValidationError(e)

        if self.add_spaces:
            return '{0} {1} {2}'.format(
                value[0:3], value[3:6], value[6:9])
        else:
            return value
