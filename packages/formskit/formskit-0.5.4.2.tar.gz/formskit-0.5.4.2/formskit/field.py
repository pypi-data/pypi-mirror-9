from json import dumps
from base64 import urlsafe_b64encode

from .converters import FakeConvert
from .translation import Translable


class Field(Translable):

    def __init__(self,
                 name,
                 validators=None,
                 label=None,
                 ignore=False,
                 convert=None):
        self.name = name
        self.label = label
        self.ignore = ignore
        self.form = None
        self._init_validators(validators)
        self._init_convert(convert)
        self.values = []
        self.reset(True)

    def _init_validators(self, validators=None):
        self.validators = []
        validators = validators or []
        for validator in validators:
            validator.init_field(self)
            self.validators.append(validator)

    def init_form(self, form):
        """
        Set form parent.
        """
        self.form = form

    def _init_convert(self, convert):
        if convert is None:
            convert = FakeConvert()
        self.convert = convert
        self.convert._set_field(convert)

    def reset(self, force=False):
        """
        Reset field values.

        :param force: if set to False and field.ignore is set to True, nothing
            will happend
        """
        if self._can_this_be_edited(force):
            super().reset()
            self.values = []
            self.error = False

    def validate(self):
        """
        Validate field.

        :return: Is validation successed?
        """
        for validator in self.validators:
            validator.make_field()

        if self.error:
            return False

        for validator in self.validators:
            for value in self.values:
                validator.make_value(value)
        return not self.error

    def set_error(self, text):
        """
        Sets error for field.

        :param text: text of error
        """
        self.error = True
        message = self._get_message_object()
        message.init(text, field=self)
        self.messages.append(message)

    def get_value(self, index=0, default=NotImplemented):
        """
        Gets value from field.

        :param index: index of value
        :param default: what will be return if value is not found. If not set,
            then raise IndexError
        """
        try:
            field_value = self.values[index]
        except IndexError:
            if default is NotImplemented:
                raise
            else:
                return default
        return self.convert(field_value.value)

    def get_value_errors(self, index=0, default=NotImplemented):
        """
        Gets errors from value.

        :param index: index of value
        :param default: what will be return if value is not found. If not set,
            then raise IndexError
        """
        try:
            field_value = self.values[index]
        except IndexError:
            if default is NotImplemented:
                raise
            else:
                return default
        return field_value.get_error_messages()

    def get_values(self):
        """
        Get list of values from field.
        """
        return [
            self.convert(field_value.value)
            for field_value in self.values
        ]

    def _can_this_be_edited(self, force):
        return force is True or self.ignore is False

    def set_values(self, values, force=False):
        """
        Sets values for field. This method will remove old ones.

        :param values: list of values to set
        :param force: if set to False and field.ignore is set to True, nothing
            will happend
        """
        if not self._can_this_be_edited(force):
            return
        self.values = []
        for value in values:
            self.values.append(
                FieldValue(
                    self,
                    value
                )
            )

    def set_value(self, value, index=0, force=False):
        """
        Sets value at index or at the end of list of values.

        :param index: index of value
        :param force: if set to False and field.ignore is set to True, nothing
            will happend
        """
        if not self._can_this_be_edited(force):
            return
        try:
            field_value = self.values[index]
            field_value.value = self.convert.back(value)
        except IndexError:
            self.values.append(
                FieldValue(
                    self,
                    self.convert.back(value)
                ))

    def get_name(self):
        """
        Get name of field.
        """
        return self.name

    def _get_message_object(self, *args, **kwargs):
        return self.form._get_message_object(*args, **kwargs)


class TreeField(Field):

    def get_name(self):
        """
        Get name of field.
        """
        data = {
            'name': self.name,
            'parents': self.form._get_parents(),
        }
        json = dumps(data)
        return urlsafe_b64encode(json.encode())


class FieldValue(Translable):

    def __init__(self, field, value):
        self.field = field
        self.value = value
        self.reset()

    def set_error(self, text):
        """
        Set error for field value.

        :param text: text of error
        """
        self.error = True
        self.field.error = True
        message = self.field._get_message_object()
        message.init(text, field=self.field, value=self)
        self.messages.append(message)

    def reset(self):
        super().reset()
        self.error = False
