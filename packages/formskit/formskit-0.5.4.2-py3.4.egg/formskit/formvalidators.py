# encoding: utf8
class FormValidationError(Exception):

    def __init__(self, validator):
        self.validator = validator.__class__.__name__
        self.message = validator.message


class FormValidator(object):

    message = None

    def set_form(self, form):
        self.form = form

    def __call__(self):
        if not self.validate():
            raise FormValidationError(self)


class MustMatch(FormValidator):
    """Will fail if first values of provided field names are not the same."""

    message = 'input must be the same!'

    def __init__(self, names):
        self.names = names

    def validate(self):
        values = []
        for name in self.names:
            field = self.form.fields[name]
            try:
                values.append(field.values[0].value)
            except IndexError:
                return False
        first = values.pop(0)
        for value in values:
            if first != value:
                return False
        return True
