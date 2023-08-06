import re

import six

import iso8601
import rfc3987

from flex.utils import is_value_of_any_type
from flex.exceptions import ValidationError
from flex.decorators import partial_safe_wraps
from flex.constants import (
    STRING,
    INTEGER,
    UUID,
    DATETIME,
    INT32,
    INT64,
    EMAIL,
    URI,
)
from flex.error_messages import MESSAGES

if six.PY2:
    import validate_email
else:
    # TODO: when a new version is released, this can be removed.
    from flex.compat import validate_email


class FormatRegistry(object):
    def __init__(self):
        self.formats = {}

    def register(self, format_name, *types):
        if format_name in self.formats:
            raise ValueError(
                "The format `{0}` is already registered".format(format_name),
            )

        def outer(func):
            @partial_safe_wraps(func)
            def inner(value, *args, **kwargs):
                """
                Format validation should only be executed if the value is of
                one of the appropriate types for the format.

                http://json-schema.org/latest/json-schema-validation.html#anchor105
                """
                if is_value_of_any_type(value, types):
                    return func(value, *args, **kwargs)

            self.formats[format_name] = inner
            return inner
        return outer

    def __getitem__(self, key):
        return self.formats[key]

    def __contains__(self, key):
        return key in self.formats


registry = FormatRegistry()
register = registry.register


"""
('number', 'float'),
('number', 'double'),
('string', 'byte'),
('string', 'date'),
"""


@register(URI, STRING)
def uri_validator(value, **kwargs):
    parts = rfc3987.parse(value, rule='URI')
    if not parts['scheme'] or not parts['authority']:
        raise ValidationError(MESSAGES['format']['invalid_uri'].format(value))


def number_of_bits(n):
    try:
        return n.bit_length()
    except AttributeError:
        return len(bin(n)) - 1


@register(INT32, INTEGER)
def int32_validator(value, **kwargs):
    num_bits = number_of_bits(value)
    if num_bits > 32:
        raise ValidationError(MESSAGES['format']['too_many_bits'].format(
            value, num_bits, 32
        ))


@register(INT64, INTEGER)
def int64_validator(value, **kwargs):
    num_bits = number_of_bits(value)
    if num_bits > 64:
        raise ValidationError(MESSAGES['format']['too_many_bits'].format(
            value, num_bits, 64
        ))


@register(EMAIL, STRING)
def email_validator(value, **kwargs):
    if not validate_email.validate_email(value):
        raise ValidationError(MESSAGES['format']['invalid_email'].format(value))


@register(DATETIME, STRING)
def date_time_format_validator(value, **kwargs):
    try:
        iso8601.parse_date(value)
    except iso8601.ParseError:
        raise ValidationError(MESSAGES['format']['invalid_datetime'].format(value))


UUID_PATTERN = re.compile(
    '^'
    '[a-f0-9]{8}-'
    '[a-f0-9]{4}-'
    '[1345][a-f0-9]{3}-'
    '[a-f0-9]{4}'
    '-[a-f0-9]{12}'
    '$'
)


@register(UUID, STRING)
def uuid_format_validator(value, **kwargs):
    if not UUID_PATTERN.match(value):
        raise ValidationError(MESSAGES['format']['invalid_uuid'].format(value))
