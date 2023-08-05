from formskit import Form
from formskit.tests.base import FormskitTestCase
from formskit.formvalidators import MustMatch


class Form1(Form):

    name1 = 'something'
    name2 = 'something2'

    def create_form(self):
        self.add_field(self.name1)
        self.add_field(self.name2)

        self.add_form_validator(MustMatch([self.name1, self.name2]))


class MustMatchTest(FormskitTestCase):

    def setUp(self):
        super().setUp()
        self.form = Form1()
        self.field1 = self.form.fields[self.form.name1]
        self.field2 = self.form.fields[self.form.name2]

    def test_success(self):
        self.field1.set_values(['1'])
        self.field2.set_values(['1'])

        assert self.form._validate_form_validators() is True
        assert self.form.messages == []

    def test_fail(self):
        self.field1.set_values(['1'])
        self.field2.set_values(['2'])

        assert self.form._validate_form_validators() is False
        assert self.form.messages[0].text == 'input must be the same!'

    def test_fail_when_number_of_values_do_not_match(self):
        self.field1.set_values(['1'])
        self.field2.set_values([])

        assert self.form._validate_form_validators() is False
        assert self.form.messages[0].text == 'input must be the same!'

    def test_success_when_number_of_values_do_not_match(self):
        self.field1.set_values(['1', '2'])
        self.field2.set_values(['1'])

        assert self.form._validate_form_validators() is True
        assert self.form.messages == []
