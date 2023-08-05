from __future__ import absolute_import, unicode_literals

import re

from operator import mul

from django.forms import ValidationError
from django.utils.translation import ugettext_lazy as _


def abn_validator(value):
    """
    Validate an ABN, based upon the rules from
    http://www.ato.gov.au/businesses/content.aspx?doc=/content/13187.htm

    Returns the ABN as it was passed in, if it is valid.

    Raises a ValidationError if the ABN is invalid
    """

    # ABNs are made up of digits only
    if re.search(r'[^0-9]', value):
        raise ValidationError('Only digits are allowed in an ABN')

    # ABNs are 11 digits long
    if len(value) != 11:
        raise ValidationError(
            _('An ABN must have 11 digits, "{0}" has {1}').format(
                value, len(value)))

    # Convert the string in to a list of digits
    nums = map(int, value)

    # 1. Subtract 1 from the first digit to give a new eleven digit number
    nums[0] -= 1

    # 2. Multiply each of the digits in this new number by its weighting factor
    weighing_factors = [10, 1, 3, 5, 7, 9, 11, 13, 15, 17, 19]
    weighted_nums = map(mul, nums, weighing_factors)

    # 3. Sum the resulting 11 products
    digit_sum = sum(weighted_nums)

    # 4. Divide the total by 89, noting the remainder
    remainder = digit_sum % 89

    # 5. If the remainder is zero the number is valid
    if remainder != 0:
        raise ValidationError(
            'This is not a valid ABN. Check you have entered the number '
            'correctly, and try again.')

    return value


def acn_validator(value):
    """
    Validate an ACN, based upon the rules from
    http://www.asic.gov.au/asic/asic.nsf/byheadline/Australian+Company+Number+%28ACN%29+Check+Digit?opendocument

    Returns the ACN as it was passed in, if it is valid.

    Raises a ValidationError if the ACN is invalid
    """

    # ACNs are made up of digits only
    if re.search(r'[^0-9]', value):
        raise ValidationError('Only digits are allowed in an ACN')

    # ACNs are 9 digits long
    if len(value) != 9:
        raise ValidationError(
            _('An ACN must have 9 digits, "{0}" has {1}').format(
                value, len(value)))

    # Convert the string in to a list of digits
    nums = map(int, value)

    digits, check = nums[0:8], nums[8]

    # 1. Apply weighting to digits 1 to 8
    weighing_factors = [8, 7, 6, 5, 4, 3, 2, 1]
    weighted_digits = map(mul, digits, weighing_factors)

    # 2. Sum the products
    digit_sum = sum(weighted_digits)

    # 3. Divide by 10 to obtain remainder
    remainder = digit_sum % 10

    # 4. Complement the remainder to 10
    complement = 10 - remainder

    # Note: if complement = 10, set to 0
    if complement == 10:
        complement = 0

    if complement != check:
        raise ValidationError(
            'This is not a valid ACN. Check you have entered the number '
            'correctly, and try again.')

    return value
