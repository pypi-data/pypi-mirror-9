"""Here are all validators for our models"""
import re

from django.core.exceptions import ValidationError

## precompiled Regexp patterns
name_pattern = re.compile(r"^[A-Za-z0-9][A-Za-z0-9\ _]*$")
alphanum_pattern = re.compile(r"^[A-Za-z0-9]*$")


def name_vld(name):
    """Check if name contains letters that are not allowed

    Only alphanumerical letters, spaces and underscores are allowed. Should start with a alphanumerical character.

    :param name: the name
    :type name: str
    :returns: None
    :rtype: None
    :raises: ValidationError
    """
    if not re.match(name_pattern, name):
        raise ValidationError("%s contains characters other than alphanumerical, spaces and underscores or does not start with a alphanumerical one." % name)


def alphanum_vld(value):
    """Check if value contains anything but alphanumerical chars

    :param value: the value to check
    :type value: str
    :returns: None
    :rtype: None
    :raises: ValidationError
    """
    if not re.match(alphanum_pattern, value):
        raise ValidationError("Value contains characters other than alphanumerical ones.")
