from mock import create_autospec
from unittest import TestCase
from pytest import raises

from formskit.field import Field
from formskit.form import WrongValueName
from formskit.tree_form import TreeForm
from formskit.validators import NotEmpty, IsDigit
from formskit.formvalidators import FormValidator


class TreeFormTest(TestCase):

    def test_reset(self):
        field = create_autospec(Field('name'))
        form = TreeForm()
        form.add_field_object(field)
        form2 = create_autospec(TreeForm())
        form2_name = form2.get_name.return_value
        form.add_sub_form(form2)
        form.get_or_create_sub_form(form2_name, 3)

        form.success = False

        form.reset()

        assert form.success is None
        field.reset.assert_called_once_with()
        assert len(form.childs[form2_name]) == 1
        form2.reset.assert_called_once_with()

    def test_parse_test_data(self):
        form = TreeForm()
        form.add_field('name')
        form.add_field('second')
        form2 = TreeForm()
        form2.add_field('surname')
        form.add_sub_form(form2)

        form.parse_dict({
            'name': ['n1'],
            'second': 'n2',
            'TreeForm': [{
                'surname': ['s1']
            }]
        })

        assert form.get_value('name') == 'n1'
        assert form.get_value('second') == 'n2'

    def test_error_decoding_name(self):
        form = TreeForm()
        form.add_field('one')
        name = form.fields['one'].get_name()
        raw_data = {
            name.replace(b'x', b'y'): ['value'],
        }

        with raises(WrongValueName):
            form._parse_raw_data(raw_data)


class TreeFormsTest(TestCase):

    def setUp(self):
        self.form = TreeForm()
        self.field = self.form.add_field('one')

        self.subform = TreeForm()
        self.subform.add_field('two', validators=[NotEmpty()])
        self.form.add_sub_form(self.subform)

    def _get_raw_data(self, value='value3'):
        raw_data = {
            self.form.form_name_value: [self.form.get_name(), ],
            self.form.fields['one'].get_name(): ['value1'],

        }
        name = (
            self.form.get_or_create_sub_form('TreeForm', 2)
            .fields['two'].get_name()
        )
        raw_data[name] = ['value2.1', 'value2.2']
        name = (
            self.form.get_or_create_sub_form('TreeForm', 3)
            .fields['two'].get_name()
        )
        raw_data[name] = [value]

        return raw_data

    def test_parse_tree(self):
        raw_data = self._get_raw_data()

        self.form.validate(raw_data)

        assert self.form.fields['one'].values[0].value == 'value1'

        field = self.form.get_sub_form('TreeForm', 2).fields['two']
        assert field.values[0].value == 'value2.1'
        assert field.values[1].value == 'value2.2'

        field = self.form.get_sub_form('TreeForm', 3).fields['two']
        assert field.values[0].value == 'value3'

    def test_validation(self):
        raw_data = self._get_raw_data('')

        self.form.validate(raw_data)

        assert self.form.success is False

        field = self.form.get_sub_form('TreeForm', 2).fields['two']
        assert field.error is False

        field = self.form.get_sub_form('TreeForm', 3).fields['two']
        assert field.error is True


class GetDataDictTreeTest(TestCase):

    def setUp(self):
        super().setUp()
        self.form = TreeForm()
        self.form.add_field('name1')

        subform = TreeForm()
        subform.add_field('name2')

        self.form.add_sub_form(subform)

        data = {
            self.form.form_name_value: [self.form.get_name()],
            self.form.fields['name1'].get_name(): ['one'],
            (
                self.form.get_or_create_sub_form('TreeForm', 0)
                .fields['name2'].get_name()
            ): [
                'two',
                'three'],
            (
                self.form.get_or_create_sub_form('TreeForm', 1)
                .fields['name2'].get_name()
            ): [
                'four'],
            (
                self.form.get_or_create_sub_form('TreeForm', 2)
                .fields['name2'].get_name()
            ): [],
        }

        self.form.validate(data)

    def test_tree(self):
        assert self.form.get_data_dict() == {
            'name1': ['one'],
            'TreeForm': {
                0: {'name2': ['two', 'three']},
                1: {'name2': ['four']},
                2: {'name2': []},
            }
        }

    def test_tree_minified(self):
        assert self.form.get_data_dict(True) == {
            'name1': 'one',
            'TreeForm': {
                0: {'name2': ['two', 'three']},
                1: {'name2': 'four'},
                2: {},
            }
        }


class GetReportTreeTest(TestCase):

    def setUp(self):
        super().setUp()
        self.form = TreeForm()
        self.form.add_field('name1', validators=[NotEmpty()])
        self.form.add_field('name2', validators=[IsDigit()])
        self.form_validator = ExampleFormValidator()
        self.form.add_form_validator(self.form_validator)
        self.child = TreeForm()
        self.child.add_field('name1', validators=[NotEmpty()])
        self.child.add_field('name2', validators=[IsDigit()])
        self.child_validator = ExampleFormValidator()
        self.child.add_form_validator(self.child_validator)
        self.form.add_sub_form(self.child)

    def run_form(self):
        data = {
            self.form.form_name_value: [self.form.get_name()]
        }
        return self.form.validate(data)

    def test_success(self):
        self.form.parse_dict({
            'name1': ['one'],
            'TreeForm': [
                {
                    'name1': ['two'],
                }
            ]
        })
        assert self.run_form() is True

        assert self.form.get_report() == {
            'childs': {
                'TreeForm': {
                    0: {
                        'childs': {},
                        'fields': {
                            'name1': {
                                'messages': [],
                                'success': True,
                                'values': [
                                    {
                                        'messages': [],
                                        'success': True,
                                        'value': 'two'
                                    }
                                ]
                            },
                            'name2': {
                                'messages': [],
                                'success': True,
                                'values': []
                            }
                        },
                        'messages': [],
                        'success': True
                    }
                }
            },
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
            },
        }

    def test_error_at_form_validator(self):
        self.form.parse_dict({
            'name1': ['one'],
            'TreeForm': [
                {
                    'name1': ['two'],
                }
            ]
        })
        self.form_validator._validate = False
        assert self.run_form() is False

        assert self.form.get_report() == {
            'childs': {
                'TreeForm': {
                    0: {
                        'childs': {},
                        'fields': {
                            'name1': {
                                'messages': [],
                                'success': True,
                                'values': [
                                    {
                                        'messages': [],
                                        'success': True,
                                        'value': 'two'
                                    }
                                ]
                            },
                            'name2': {
                                'messages': [],
                                'success': True,
                                'values': []
                            }
                        },
                        'messages': [],
                        'success': True
                    }
                }
            },
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
            },
        }

    def test_error_at_field_validator_with_compiling(self):
        self.form.parse_dict({
            'TreeForm': [
                {
                    'name1': ['two'],
                }
            ]
        })
        assert self.run_form() is False

        assert self.form.get_report() == {
            'childs': {
                'TreeForm': {
                    0: {
                        'childs': {},
                        'fields': {
                            'name1': {
                                'messages': [],
                                'success': True,
                                'values': [
                                    {
                                        'messages': [],
                                        'success': True,
                                        'value': 'two'
                                    }
                                ]
                            },
                            'name2': {
                                'messages': [],
                                'success': True,
                                'values': []
                            }
                        },
                        'messages': [],
                        'success': True
                    }
                }
            },
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
            },
        }

    def test_error_at_field_value_validator(self):
        self.form.parse_dict({
            'name1': ['one'],
            'name2': ['three'],
            'TreeForm': [
                {
                    'name1': ['two'],
                }
            ]
        })
        assert self.run_form() is False

        assert self.form.get_report() == {
            'childs': {
                'TreeForm': {
                    0: {
                        'childs': {},
                        'fields': {
                            'name1': {
                                'messages': [],
                                'success': True,
                                'values': [
                                    {
                                        'messages': [],
                                        'success': True,
                                        'value': 'two'
                                    }
                                ]
                            },
                            'name2': {
                                'messages': [],
                                'success': True,
                                'values': []
                            }
                        },
                        'messages': [],
                        'success': True
                    }
                }
            },
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
            },
        }

    def test_subform_error_at_form_validator(self):
        self.form.parse_dict({
            'name1': ['one'],
            'TreeForm': [
                {
                    'name1': ['two'],
                }
            ]
        })
        self.child_validator._validate = False
        assert self.run_form() is False

        assert self.form.get_report() == {
            'childs': {
                'TreeForm': {
                    0: {
                        'childs': {},
                        'fields': {
                            'name1': {
                                'messages': [],
                                'success': True,
                                'values': [
                                    {
                                        'messages': [],
                                        'success': True,
                                        'value': 'two'
                                    }
                                ]
                            },
                            'name2': {
                                'messages': [],
                                'success': True,
                                'values': []
                            }
                        },
                        'messages': ['example validator'],
                        'success': False
                    }
                }
            },
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
                    'success': True,
                    'messages': [],
                    'values': []
                },
            },
        }

    def test_subform_error_at_field_value_validator(self):
        self.form.parse_dict({
            'name1': ['one'],
            'TreeForm': [
                {
                    'name1': [],
                }
            ]
        })
        assert self.run_form() is False

        assert self.form.get_report() == {
            'childs': {
                'TreeForm': {
                    0: {
                        'childs': {},
                        'fields': {
                            'name1': {
                                'messages': ['NotEmpty'],
                                'success': False,
                                'values': []
                            },
                            'name2': {
                                'messages': [],
                                'success': True,
                                'values': []
                            }
                        },
                        'messages': [],
                        'success': False
                    }
                }
            },
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
                    'success': True,
                    'messages': [],
                    'values': []
                },
            },
        }


class ExampleFormValidator(FormValidator):

    message = 'example validator'

    def __init__(self):
        super().__init__()
        self._validate = True

    def validate(self):
        return self._validate
