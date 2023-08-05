from pytest import fixture

from formskit.tests.base import FormskitTestCase
from formskit.field import Field, FieldValue
from formskit.translation import Translation
import formskit.validators as VAL


class ExampleField(Field):

    def _get_message_object(self):
        return Translation()


class ValidatorTestMixin(object):
    cls = None
    good_samples = None
    bad_samples = None

    def setUp(self):
        super().setUp()
        self.field = ExampleField('name')
        self.validator = self.cls()
        self.validator.init_field(self.field)

    def test_success(self):
        for sample in self.good_samples:
            field_value = FieldValue(self.field, sample)
            self.validator.make_value(field_value)

            assert self.field.error is False
            assert self.field.messages == []
            assert field_value.messages == []
            assert field_value.error is False

    def test_fail(self):
        for sample in self.bad_samples:
            self.field.reset()
            field_value = FieldValue(self.field, sample)

            self.validator.make_value(field_value)

            assert self.field.error is True
            if self._is_field_value_validator():
                assert self.field.messages == []
                assert field_value.error is True
                assert field_value.messages[0].text == self.cls.__name__
            else:
                assert self.field.messages[0].text == self.cls.__name__
                assert field_value.messages == []
                assert field_value.error is False

    def _is_field_value_validator(self):
        return issubclass(self.cls, VAL.FieldValidator)

    def test_set_form(self):
        field = ExampleField('my field')
        validator = self.cls()
        validator.init_field(field)

        self.assertEqual(field, validator.field)


class NotEmptyValidatorTest(ValidatorTestMixin, FormskitTestCase):
    cls = VAL.NotEmpty

    good_samples = [
        'z', '0', '12312312dasd213123', ',', ' ad sda ',
    ]

    bad_samples = [
        ' ', '', None, [], {}, b'',
    ]


class IsDigitValidatorTest(ValidatorTestMixin, FormskitTestCase):
    cls = VAL.IsDigit

    good_samples = [
        '1', '123123123', '012312', '-123123', '',
    ]

    bad_samples = [
        'a', '-123213.12323', '2a',
    ]


class EmailValidatorTest(ValidatorTestMixin, FormskitTestCase):
    cls = VAL.IsEmail

    good_samples = [
        'msocek@gmail.com',
        '1asd@asdasd.sadad.pl',
    ]

    bad_samples = [
        'a', '', '-123213.12323', '2a',
        ' ', '@asdweq.asdad.pl', '1asd@asdasd.sadad.asdpl',
    ]


class IsDecimalTest(ValidatorTestMixin, FormskitTestCase):
    cls = VAL.IsDecimal

    good_samples = [
        '1',
        '1.2',
        '1.2213123123123123',
        '123123123.123123'
        '234234234234',
        '-123123.123123',
    ]

    bad_samples = [
        'a', '', '-123213,12323', '2a',
        ' ', '@asdweq.asdad.pl', '1asd@asdasd.sadad.asdpl',
    ]


class InListTest(FormskitTestCase):
    cls = VAL.InList

    def setUp(self):
        super().setUp()
        self.field = ExampleField('name')
        self.data = ['5']
        self.validator = self.cls(self.data)
        self.validator.init_field(self.field)

    def test_good(self):
        field_value = FieldValue(self.field, '5')
        self.validator.make_value(field_value)

        assert self.field.error is False
        assert self.field.messages == []
        assert field_value.messages == []
        assert field_value.error is False

    def test_fail(self):
        field_value = FieldValue(self.field, '6')
        self.validator.make_value(field_value)

        assert self.field.error is True
        assert self.field.messages == []
        assert field_value.error is True
        assert field_value.messages[0].text == self.cls.__name__

    def test_good_method(self):
        def method():
            return ['4']

        self.validator = self.cls(method)
        self.validator.init_field(self.field)

        field_value = FieldValue(self.field, '4')
        self.validator.make_value(field_value)

        assert self.field.error is False
        assert self.field.messages == []
        assert field_value.messages == []
        assert field_value.error is False

    def test_fail_method(self):
        def method():
            return ['4']

        self.validator = self.cls(method)
        self.validator.init_field(self.field)

        field_value = FieldValue(self.field, '5')
        self.validator.make_value(field_value)

        assert self.field.error is True
        assert self.field.messages == []
        assert field_value.error is True
        assert field_value.messages[0].text == self.cls.__name__


class TestFieldValidatorInit(object):

    def test_custom_message(self):
        """
        .__init__ should do nothing when message is set.
        """
        class Example2(VAL.FieldValidator):
            message = 'custome message'

        obj = Example2()

        assert obj.message == 'custome message'

    def test_default_message(self):
        """
        .__init__ should generate message from class name
        """
        class Example3(VAL.FieldValidator):
            pass

        obj = Example3()

        assert obj.message == 'Example3'
