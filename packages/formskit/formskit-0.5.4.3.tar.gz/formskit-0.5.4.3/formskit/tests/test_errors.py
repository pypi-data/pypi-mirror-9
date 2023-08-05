from formskit.tests.base import FormskitTestCase
from formskit import errors


class ErrorsTests(FormskitTestCase):

    def test_BadValue(self):
        error = errors.BadValue('name1')
        self.assertEqual('name1', error.name)
        self.assertEqual('name1', str(error))

    def test_ValueNotPresent(self):
        error = errors.ValueNotPresent('name2')
        self.assertEqual('name2', error.name)
        self.assertEqual('name2', str(error))
