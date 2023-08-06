from mock import create_autospec
from unittest import TestCase
from pytest import raises

from formskit.field import Field
from formskit.form import Form, WrongValueName
from formskit.validators import NotEmpty, IsDigit
from formskit.converters import ToInt
from formskit.formvalidators import FormValidator
from formskit.translation import Translation


class FormTest(TestCase):

    def test_add_field_object(self):
        field = create_autospec(Field('name'))
        form = Form()
        form.add_field_object(field)

        field.init_form.assert_called_once_with(form)
        assert field is form.fields[field.name]

    def test_add_field(self):
        form = Form()
        form.add_field('myname')

        assert isinstance(form.fields['myname'], Field)

    def test_reset(self):
        field = create_autospec(Field('name'))
        form = Form()
        form.add_field_object(field)

        form.success = False

        form.reset()

        assert form.success is None
        field.reset.assert_called_once_with()

    def test_is_validated(self):
        form = Form()

        data = {
            form.form_name_value: [form.get_name(), ],
        }
        assert form.validate(data) is True

    def test_is_not_submited(self):
        form = Form()

        assert form.validate({}) is None

    def test_if_not_validated(self):
        form = Form()
        form.add_field('name', validators=[NotEmpty()])

        data = {
            form.form_name_value: [form.get_name(), ],
        }
        assert form.validate(data) is False

    def test_parse_test_data(self):
        form = Form()
        form.add_field('name')
        form.add_field('second')

        form.parse_dict({
            'name': ['n1'],
            'second': 'n2',
        })

        assert form.get_value('name') == 'n1'
        assert form.get_value('second') == 'n2'

    def test_messages(self):
        class ExampleTranslation(Translation):

            def translate(self):
                return 'translated!'
        form = Form()
        form.translation_class = ExampleTranslation

        form.add_field('name', validators=[NotEmpty()])

        assert form.validate({
            form.form_name_value: [form.get_name()],
        }) is False

        assert form.fields['name'].messages[0]() == 'translated!'


class TestGetAndSet(TestCase):

    def setUp(self):
        super().setUp()
        self.form = Form()
        self.form.add_field('name')

    def test_set_once(self):
        self.form.set_value('name', 'value')

        assert self.form.get_value('name') == 'value'
        assert self.form.get_values('name') == ['value']

    def test_set_once_with(self):
        self.form.set_value('name', 'value', 1)
        self.form.set_value('name', 'value2', 1)
        self.form.set_value('name', 'value3', 1)

        assert self.form.get_value('name', 0) == 'value'
        assert self.form.get_value('name', 1) == 'value3'
        assert self.form.get_values('name') == ['value', 'value3']

    def test_set_many(self):
        self.form.set_values('name', ['one', 'two'])

        assert self.form.get_value('name', 0) == 'one'
        assert self.form.get_value('name', 1) == 'two'
        assert self.form.get_values('name') == ['one', 'two']

    def test_set_many_with_converter(self):
        self.form.add_field('name2', convert=ToInt())
        self.form.set_values('name2', ['2', '3'])

        assert self.form.get_value('name2', 0) == 2
        assert self.form.get_value('name2', 1) == 3
        assert self.form.get_values('name2') == [2, 3]

    def test_ignore(self):
        self.form.fields['name'].ignore = True

        self.form.set_value('name', 'one')
        self.form.set_values('name', ['one', 'two'])

        assert self.form.get_values('name') == []

    def test_force(self):
        self.form.fields['name'].ignore = True

        self.form.set_value('name', 'one', force=True)

        assert self.form.get_values('name') == ['one']

    def test_force_many(self):
        self.form.fields['name'].ignore = True

        self.form.set_values('name', ['one', 'two'], force=True)

        assert self.form.get_values('name') == ['one', 'two']


class IsFormSubmittedTest(TestCase):

    def test_name_do_not_match(self):
        form = Form()
        raw_data = {
            Form.form_name_value: [form.get_name() + 'bad'],
        }

        assert form._is_form_submitted(raw_data) is False

    def test_name_match(self):
        form = Form()
        raw_data = {
            Form.form_name_value: [form.get_name()],
        }

        assert form._is_form_submitted(raw_data) is True

    def test_not_form_data(self):
        form = Form()
        raw_data = {}

        assert form._is_form_submitted(raw_data) is False


class ParseRawDataTest(TestCase):

    def setUp(self):
        self.form = Form()
        self.field = self.form.add_field('one')

    def test_good_data(self):
        raw_data = {
            self.form.fields['one'].get_name(): ['value']
        }

        self.form._parse_raw_data(raw_data)

        assert self.form.fields['one'].values[0].value == 'value'

    def test_too_many_data(self):
        raw_data = {
            self.form.fields['one'].get_name(): ['value'],
            'two': ['something'],
        }

        with raises(WrongValueName):
            self.form._parse_raw_data(raw_data)

    def test_too_few_data(self):
        raw_data = {}

        self.form._parse_raw_data(raw_data)

        assert self.form.fields['one'].values == []


class GetDataDictTest(TestCase):

    def setUp(self):
        super().setUp()
        self.form = Form()
        self.form.add_field('name1')
        self.form.add_field('name2')

        data = {
            self.form.form_name_value: [self.form.get_name()],
            'name1': ['one'],
            'name2': ['two', 'three'],
        }

        self.form.validate(data)

    def test_dict(self):
        assert self.form.get_data_dict() == {
            'name1': ['one'],
            'name2': ['two', 'three'],
        }

    def test_dict_minified(self):
        assert self.form.get_data_dict(True) == {
            'name1': 'one',
            'name2': ['two', 'three'],
        }


class ExampleFormValidator(FormValidator):

    message = 'example validator'

    def __init__(self):
        super().__init__()
        self._validate = True

    def validate(self):
        return self._validate


class GetReportTest(TestCase):

    def setUp(self):
        super().setUp()
        self.form = Form()
        self.form.add_field('name1', validators=[NotEmpty()])
        self.form.add_field('name2', validators=[IsDigit()])
        self.form_validator = ExampleFormValidator()
        self.form.add_form_validator(self.form_validator)

    def run_form(self):
        data = {
            self.form.form_name_value: [self.form.get_name()]
        }
        return self.form.validate(data)

    def test_success(self):
        self.form.parse_dict({
            'name1': ['one'],
        })
        assert self.run_form() is True

        assert self.form.get_report() == {
            'success': True,
            'messages': [],
            'fields': {
                'name1': {
                    'success': True,
                    'messages': [],
                    'values': [{
                        'value': 'one',
                        'success': True,
                        'messages': [],
                    }]
                },
                'name2': {
                    'success': True,
                    'messages': [],
                    'values': []
                },
            }
        }

    def test_error_at_form_validator(self):
        self.form.parse_dict({
            'name1': ['one'],
        })
        self.form_validator._validate = False
        assert self.run_form() is False

        assert self.form.get_report() == {
            'success': False,
            'messages': ['example validator'],
            'fields': {
                'name1': {
                    'success': True,
                    'messages': [],
                    'values': [{
                        'value': 'one',
                        'success': True,
                        'messages': [],
                    }]
                },
                'name2': {
                    'success': True,
                    'messages': [],
                    'values': []
                },
            }
        }

    def test_error_at_field_validator_with_compiling(self):
        self.form.parse_dict({
        })
        assert self.run_form() is False

        assert self.form.get_report() == {
            'success': False,
            'messages': [],
            'fields': {
                'name1': {
                    'success': False,
                    'messages': ['NotEmpty'],
                    'values': []
                },
                'name2': {
                    'success': True,
                    'messages': [],
                    'values': []
                },
            }
        }

    def test_error_at_field_value_validator(self):
        self.form.parse_dict({
            'name1': ['one'],
            'name2': ['three']
        })
        assert self.run_form() is False

        assert self.form.get_report() == {
            'success': False,
            'messages': [],
            'fields': {
                'name1': {
                    'success': True,
                    'messages': [],
                    'values': [{
                        'value': 'one',
                        'success': True,
                        'messages': [],
                    }]
                },
                'name2': {
                    'success': False,
                    'messages': [],
                    'values': [{
                        'value': 'three',
                        'success': False,
                        'messages': ['IsDigit'],
                    }]
                },
            }
        }
