from .field import Field
from .formvalidators import FormValidationError
from .translation import Translation, Translable


class Form(Translable):

    form_name_value = 'form_name'
    translation_class = Translation

    def get_name(self):
        """Gets name of this form."""
        return self.__class__.__name__

    def __init__(self):
        self._init_before_create()
        self.create_form()
        self.reset()

    def _init_before_create(self):
        self.fields = {}
        self.form_validators = []
        self.raw_data = None
        self.index = None

    def add_field_object(self, field):
        """
        Add field to form.

        :param field: field object
        """
        self.fields[field.name] = field
        field.init_form(self)

    def add_field(self, *args, **kwargs):
        """
        Create and add field to form.
        Params are the same as in ``Field`` init.
        """
        field = Field(*args, **kwargs)
        self.add_field_object(field)
        return field

    def validate(self, raw_data):
        """
        Gets raw data from dict and validate this object.

        :returns:
            * None: if form is not submited
            * True: if form is submited, and validation is success
            * Fail: if form is submited, and validation is fails
        """
        if self._is_form_submitted(raw_data):
            self._parse_raw_data(raw_data)
            if self._validate():
                self.on_success()
                return True
            else:
                self.on_fail()
                return False
        else:
            return None

    def _is_form_submitted(self, raw_data):
        return raw_data.get(self.form_name_value, None) == [self.get_name(), ]

    def _parse_raw_data(self, raw_data):
        for name, values in raw_data.items():
            if name == self.form_name_value:
                continue
            field = self._get_field(name)
            field.set_values(values)

    def _get_field(self, name):
        try:
            return self.fields[name]
        except KeyError:
            raise WrongValueName(name)

    def reset(self):
        """Reset the form and clear all it's fields."""
        super().reset()
        self.success = None
        for field in self.fields.values():
            field.reset()

    def _validate(self):
        # Why this method was implemented in this way?
        # Goal was to run validation on fields and if it succeeded, then form
        # can run form validators.
        # But sub_forms should always run validation.
        self.success = True
        self.success &= (
            self._validate_fields()
            and self._validate_form_validators()
        )
        return self.success

    def _validate_fields(self):
        success = True
        for field in self.fields.values():
            success &= field.validate()
        return success

    def _validate_form_validators(self):
        for validator in self.form_validators:
            try:
                validator()
            except FormValidationError as er:
                message = self._get_message_object()
                message.init(er.message, form=self)
                self.messages.append(message)
                return False
        return True

    def add_form_validator(self, validator):
        """
        Adds form validator to form.

        :param validator: Object of FormValidator class.
        """
        validator.set_form(self)
        self.form_validators.append(validator)

    def get_values(self, name):
        """
        Get all values of field.

        :param name: name of field.
        :rtype: FieldValue
        """
        return self.fields[name].get_values()

    def get_value(self, name, index=0, default=NotImplemented):
        """
        Get field value at index.

        :param name: name of field
        :param index: index of value in field (default: 0)
        :param default: what to return if value not found (default: raise
            error)
        """
        return self.fields[name].get_value(index, default)

    def set_values(self, name, values, force=False):
        """
        Set values for field.

        :param name: name of field
        :param values: list of values
        :param force: if set to False and field.ignore is set to True, nothing
            will happend
        """
        self.fields[name].set_values(values, force=force)

    def set_value(self, name, value, index=0, force=False):
        """set_value(name, value[, index, force])
        Set value at index.

        :param name: name of field
        :param value: value
        :param force: if set to False and field.ignore is set to True, nothing
            will happend
        """
        self.fields[name].set_value(value, index, force=force)

    def get_data_dict(self, minified=False):
        """get_data_dict([minified])
        Get all values from all fields.

        :param minified: if True: all list with length of 1 will be converted
            to direct value. all empty list will be omited
        :rtype: dict
        """
        tree = {}
        for name, field in self.fields.items():
            tree[name] = field.get_values()
            if minified and len(tree[name]) == 1:
                tree[name] = tree[name][0]
            elif minified and len(tree[name]) == 0:
                del tree[name]
        return tree

    def parse_dict(self, data, force=False):
        """parse_dict(data[, force])
        Parse data from dict. Keys is the field name, values can be in form of
        list or without it.

        :param data: dict of data to parse
        :param force: if set to False and field.ignore is set to True, nothing
            will happend
        """
        for name, values in data.items():
            if name in self.fields:
                field = self.fields[name]
                if hasattr(values, '__iter__') and type(values) is not str:
                    field.set_values(values, force=force)
                else:
                    field.set_value(values, force=force)
            else:
                self._parse_sub_form(name, values)

    def get_report(self):
        """Get report from all fields."""
        def convert(messages):
            data = []
            for message in messages:
                data.append(message())
            return data

        report = {
            'success': self.success,
            'messages': convert(self.messages),
            'fields': {},
        }
        for name, field in self.fields.items():
            values = []
            for value in field.values:
                values.append({
                    'value': value.value,
                    'success': not value.error,
                    'messages': convert(value.messages),
                })
            report['fields'][name] = {
                'success': not field.error,
                'messages': convert(field.messages),
                'values': values,
            }
        return report

    def _get_message_object(self, *args, **kwargs):
        return self.translation_class(*args, **kwargs)

    def create_form(self):
        """
        This metod will be called to create form.
        It should be reimplemented.
        """
        pass

    def on_success(self):
        """
        This metod will be called when validation will success.
        It should be reimplemented.
        """
        pass

    def on_fail(self):
        """
        This metod will be called when validation will fail.
        It should be reimplemented.
        """
        pass


class WrongValueName(Exception):

    def __init__(self, name):
        self.name = name
