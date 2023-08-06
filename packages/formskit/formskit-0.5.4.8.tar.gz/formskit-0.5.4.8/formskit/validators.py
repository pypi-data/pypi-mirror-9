# encoding: utf8
import re
from decimal import Decimal, InvalidOperation


class FieldValidator(object):
    message = None

    def __init__(self):
        if self.message is None:
            self.message = self.__class__.__name__

    def init_field(self, field):
        self.field = field

    def make_field(self):
        if self.validate_field() is False:
            self.set_field_error()

    def make_value(self, field_value):
        self.field_value = field_value
        self.value = field_value.value
        if self.validate_value() is False:
            self.set_value_error()

    @property
    def value_converted(self):
        return self.field.convert(self.value)

    def set_field_error(self):
        self.field.set_error(self.message)

    def set_value_error(self):
        self.field_value.set_error(self.message)

    def validate_field(self):
        pass


class NotEmpty(FieldValidator):

    """Will fail if no value found of value is empty or has only whitespaces"""

    def validate_field(self):
        return len(self.field.values) > 0

    def validate_value(self):
        if self.value is None:
            return False
        elif type(self.value) == str and self.value.strip() == '':
            return False
        elif type(self.value) == bytes and self.value.strip() == b'':
            return False
        elif type(self.value) in [list, dict, tuple] and len(self.value) == 0:
            return False
        return True


class IsDigit(FieldValidator):

    """Will fail if value is not a digit."""

    regex = re.compile('^-{0,1}[0-9]+$')

    def validate_value(self):
        if not self.value:
            return True
        return re.search(self.regex, self.value) is not None


class IsDecimal(FieldValidator):

    """Will fail if value can not be converted to decimal.Decimal."""

    def validate_value(self):
        try:
            Decimal(self.value)
            return True
        except InvalidOperation:
            return False


class IsEmail(FieldValidator):

    """Will fail if value is not an email."""

    regex = re.compile(
        "^.+\\@(\\[?)[a-zA-Z0-9\\-\\.]+\\.([a-zA-Z]{2,3}|[0-9]{1,3})(\\]?)$")

    def validate_value(self):
        if len(self.value) > 7:
            return re.match(self.regex, self.value) is not None
        return False


class IsValueInAvalibleValues(FieldValidator):

    """Will fail if value is not in list."""

    def __init__(self, allow_empty=False):
        super().__init__()
        self.allow_empty = allow_empty

    def validate_value(self):
        if self.allow_empty:
            if self.value is None:
                return True
            elif type(self.value) == str and self.value.strip() == '':
                return True

        return self.value_converted in [
            avalible.value for avalible in self.field.avalible_values
        ]
