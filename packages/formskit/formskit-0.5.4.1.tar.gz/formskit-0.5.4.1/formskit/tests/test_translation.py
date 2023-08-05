from pytest import fixture
from mock import create_autospec

from formskit.translation import Translation, Translable
from formskit.tests.base import FormskitTestCase


class TranslationTests(FormskitTestCase):

    def test_casting(self):
        class InheritedTranslation(Translation):
            pass

        message = Translation()
        message.init('text', 'one', two='two')

        casted = InheritedTranslation(message)

        assert casted.text == 'text'
        assert casted.args == ('one',)
        assert casted.kwargs == {'two': 'two'}

    def test_normaln_translating(self):
        message = Translation()
        message.init('text {0} {two}', 'one', two='two')

        assert message() == 'text one two'

    def test_inherited_translation(self):
        class InheritedTranslation(Translation):

            def translate(self):
                return self.text + 'something'

        message = Translation()
        message.init('text {0} {two}', 'one', two='two')

        casted = InheritedTranslation(message)
        assert casted() == 'text one twosomething'


class TestTranslable(object):

    @fixture
    def translable(self, message):
        obj = Translable()
        obj.messages = [message]
        return obj

    @fixture
    def message(self):
        return create_autospec(Translation)

    def test_reset(self, translable):
        """
        .reset should make empty list
        """
        translable.reset()

        assert translable.messages == []

    def test_get_error_messages(self, translable, message):
        """
        .get_error_messages should return compiled messages.
        """
        assert translable.get_error_messages() == [message.return_value]
