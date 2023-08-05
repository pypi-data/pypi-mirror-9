from django.test import TestCase
from mobile_framework.core.utils import Bool

class BoolTestCase(TestCase):
    
    def test_number_true(self):
        value = 1
        self.assertTrue(Bool(value))

    def test_number_false(self):
        value = 0
        self.assertFalse(Bool(value))

    def test_string_number_true(self):
        value = '1'
        self.assertTrue(Bool(value))

    def test_string_number_false(self):
        value = '0'
        self.assertFalse(Bool(value))

    def test_none_value(self):
        value = None
        self.assertFalse(Bool(value))

    def test_non_empty_string(self):
        value = 'not empty'
        self.assertTrue(Bool(value))

    def test_empty_string(self):
        value = ''
        self.assertFalse(Bool(value))

    def test_non_empty_list(self):
        value = ['not', 'empty']
        self.assertTrue(Bool(value))

    def test_empty_list(self):
        value = []
        self.assertFalse(Bool(value))

    def test_non_empty_tuple(self):
        value = ('not', 'empty')
        self.assertTrue(Bool(value))

    def test_empty_tuple(self):
        value = ()
        self.assertFalse(Bool(value))

    def test_non_empty_dict(self):
        value = {'not':'empty'}
        self.assertTrue(Bool(value))

    def test_empty_dict(self):
        value = {}
        self.assertFalse(Bool(value))