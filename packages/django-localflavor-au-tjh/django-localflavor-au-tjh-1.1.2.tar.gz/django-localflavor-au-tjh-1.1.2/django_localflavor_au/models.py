from __future__ import absolute_import, unicode_literals

import re

from django.utils.six import string_types

from django.core import validators
from django.db import models

from django.utils.translation import ugettext_lazy as _
from django.db.models import SubfieldBase
from django.db.models.fields import CharField

from django_localflavor_au import forms
from django_localflavor_au.au_states import STATE_CHOICES
from django_localflavor_au.utils import abn_validator, acn_validator


class AUStateField(CharField):

    description = _("Australian State")

    def __init__(self, *args, **kwargs):
        kwargs['choices'] = STATE_CHOICES
        kwargs['max_length'] = 3
        super(AUStateField, self).__init__(*args, **kwargs)

    def south_field_triple(self):
        from south.modelsinspector import introspector
        args, kwargs = introspector(self)
        return ('django_localflavor_au.models.AUStateField', args, kwargs)


class AUPostCodeField(CharField):

    description = _("Australian Postcode")

    def __init__(self, *args, **kwargs):
        kwargs['max_length'] = 4
        super(AUPostCodeField, self).__init__(*args, **kwargs)

    def formfield(self, **kwargs):
        defaults = {'form_class': forms.AUPostCodeField}
        defaults.update(kwargs)
        return super(AUPostCodeField, self).formfield(**defaults)

    def south_field_triple(self):
        from south.modelsinspector import introspector
        args, kwargs = introspector(self)
        return ('django_localflavor_au.models.AUPostCodeField', args, kwargs)


class FormattedNumberField(CharField):

    __metaclass__ = SubfieldBase

    EMPTY_VALUE = None

    SEPERATOR_RE = None

    DIGITS = None

    errors = {
        'not_string': _('The provided value is not a string, it is a {0!r}'),
    }

    add_space = True

    def __init__(self, default_area_code=None, add_spaces=True, *args,
                 **kwargs):
        self.add_spaces = add_spaces

        kwargs.setdefault('max_length', self.DIGITS)
        super(FormattedNumberField, self).__init__(*args, **kwargs)
        self.validators.append(validators.MinLengthValidator(self.DIGITS))

    def to_python(self, value):
        if not value:
            return self.EMPTY_VALUE

        # If it is not a string, I have no idea what to do about it
        if not isinstance(value, string_types):
            raise ValueError(self.errors['not_string'].format(type(value)))

        value = self.SEPERATOR_RE.sub('', value)

        if self.add_spaces:
            return self.format_number(value)
        else:
            # Else return it plain
            return value

    def get_prep_value(self, value):
        if not value:
            return value

        if not isinstance(value, string_types):
            # If it is not a string, I have no idea what to do about it
            raise ValueError(self.errors['not_string'].format(type(value)))

        # Strip out all seperators.
        value = self.SEPERATOR_RE.sub('', value)
        return value

    def value_to_string(self, obj):
        value = self._get_val_from_obj(obj)
        return self.get_prep_value(value)

    def clean(self, value, model_instance):
        """
        Convert the value's type and run validation. Validation errors
        from to_python and validate are propagated. The correct value is
        returned if no error is raised.

        This is a modified `clean`. It runs the validation on `get_prep_value`,
        instead of on `to_python`, as the `to_python` version may have spaces
        which are not allowed in validation - but are not saved, either.
        """
        value = self.to_python(value)
        prep_value = self.get_prep_value(value)

        self.validate(prep_value, model_instance)
        self.run_validators(prep_value)
        return value


class AUPhoneNumberField(FormattedNumberField):
    """
    Represent an Australian phone number in the database. Phone numbers are
    always saved with out any formatting, and with their area code.

    A default area code can be used when setting this field - just call
    AUPhoneNumberField with `default_area_code='03'`, for example. This is
    `None` by default, and phone numbers with no area code will raise a
    ValueError when set.

    Phone numbers will nicely formatted when retrieved from the database, to
    aid with displaying them in a consistent manner. Normal phone numbers will
    be formatted as `(03) 6231 9110`, while mobile phones will be formatted as
    `0412 345 678`. Set `add_spaces=False` when constructing the
    AUPhoneNumberField to disable this functionality. The phone numbers will be
    returned as they are represented in the database, with out any formatting.
    """

    __metaclass__ = SubfieldBase

    description = _("Australian Phone number")

    SEPERATOR_RE = re.compile('[ /()-]')
    DIGITS = 10

    errors = {
        'not_string': _('The provided value is not a string, it is a {0!r}'),
        'missing_area_code': _('Phone numbers must have an area code'),
    }

    default_area_code = None

    def __init__(self, default_area_code=None, *args, **kwargs):
        self.default_area_code = default_area_code
        super(AUPhoneNumberField, self).__init__(*args, **kwargs)

    def format_number(self, value):
        if value[0:2] == '04':
            # Mobile numbers are '0412 345 678'
            return '{0} {1} {2}'.format(
                value[0:4], value[4:7], value[7:10])
        else:
            # Other numbers are '(03) 6231 9110'
            return '({0}) {1} {2}'.format(
                value[0:2], value[2:6], value[6:10])

    def to_python(self, value):
        if not value:
            return value

        # If it is not a string, I have no idea what to do about it
        if not isinstance(value, string_types):
            raise ValueError(
                'Phone number is not a string, it is a {0!r}'.format(
                    type(value)))

        stripped_value = self.SEPERATOR_RE.sub('', value)
        if len(stripped_value) == 8:
            if self.default_area_code:
                stripped_value = self.default_area_code + stripped_value
            else:
                return value
        # We only check for 10 or 8, too many alternatives
        elif len(stripped_value) != 10:
            return value

        if self.add_spaces:
            return self.format_number(stripped_value)
        else:
            # Else return it plain
            return stripped_value

    def formfield(self, **kwargs):
        defaults = {
            'max_length': 20,
            'default_area_code': self.default_area_code,
            'form_class': forms.AUPhoneNumberField,
        }
        defaults.update(kwargs)
        return super(AUPhoneNumberField, self).formfield(**defaults)

    def south_field_triple(self):
        from south.modelsinspector import introspector
        args, kwargs = introspector(self)
        kwargs['default_area_code'] = self.default_area_code
        kwargs['add_spaces'] = self.add_spaces
        return ('django_localflavor_au.models.AUPhoneNumberField', args, kwargs)


class ABNField(FormattedNumberField):

    __metaclass__ = SubfieldBase

    description = _('Australian Business Number field')

    SEPERATOR_RE = re.compile('[ /-]')
    DIGITS = 11

    def __init__(self, add_spaces=True, *args, **kwargs):
        super(ABNField, self).__init__(*args, **kwargs)
        self.validators.append(abn_validator)

    def format_number(self, value):
        # Return it as '12 345 678 901' if requested
        return '{0} {1} {2} {3}'.format(
            value[0:2], value[2:5], value[5:8], value[8:11])

    def formfield(self, **kwargs):
        defaults = {
            'add_spaces': self.add_spaces,
            'form_class': forms.ABNField,
        }
        defaults.update(kwargs)
        return super(ABNField, self).formfield(**defaults)

    def south_field_triple(self):
        from south.modelsinspector import introspector
        args, kwargs = introspector(self)
        kwargs['add_spaces'] = self.add_spaces
        return ('django_localflavor_au.models.ABNField', args, kwargs)


class ACNField(FormattedNumberField):

    __metaclass__ = SubfieldBase

    description = _('Australian Company Number field')

    SEPERATOR_RE = re.compile('[ /-]')
    DIGITS = 9

    def __init__(self, add_spaces=True, *args, **kwargs):
        super(ACNField, self).__init__(*args, **kwargs)
        self.validators.append(acn_validator)

    def format_number(self, value):
        # Return it as '12 345 678 901' if requested
        return '{0} {1} {2}'.format(
            value[0:3], value[3:6], value[6:9])

    def formfield(self, **kwargs):
        defaults = {
            'add_spaces': self.add_spaces,
            'form_class': forms.ACNField,
        }
        defaults.update(kwargs)
        return super(ACNField, self).formfield(**defaults)

    def south_field_triple(self):
        from south.modelsinspector import introspector
        args, kwargs = introspector(self)
        kwargs['add_spaces'] = self.add_spaces
        return ('django_localflavor_au.models.ACNField', args, kwargs)
