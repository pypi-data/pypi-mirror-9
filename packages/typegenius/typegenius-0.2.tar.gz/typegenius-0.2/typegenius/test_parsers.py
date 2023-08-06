import unittest
from datetime import datetime
from typegenius import parsers


class TestParsers(unittest.TestCase):
    def test_is_float_valid_instance(self):
        val = 1.2
        self.assertTrue(parsers.is_float(val))

    def test_is_float_valid_string(self):
        val = '1.2'
        self.assertTrue(parsers.is_float(val))

    def test_is_float_invalid(self):
        val = 'abc'
        self.assertFalse(parsers.is_float(val))

    def test_is_int_valid_instance(self):
        val = 1
        self.assertTrue(parsers.is_int(val))

    def test_is_int_valid_string(self):
        val = '1'
        self.assertTrue(parsers.is_int(val))

    def test_is_int_invalid(self):
        val = 'abc'
        self.assertFalse(parsers.is_int(val))

    def test_is_bool_valid_instance(self):
        val = True
        self.assertTrue(parsers.is_bool(val))

    def test_is_bool_valid_string_true(self):
        val = 'TRUE'
        self.assertTrue(parsers.is_bool(val))

    def test_is_bool_valid_string_false(self):
        val = 'false'
        self.assertTrue(parsers.is_bool(val))

    def test_is_bool_invalid(self):
        val = 'abc'
        self.assertFalse(parsers.is_bool(val))

    def test_is_date_valid_instance(self):
        val = datetime.now()
        self.assertTrue(parsers.is_date(val))

    def test_get_float(self):
        val = 1.2
        result = parsers.get(str(val))
        self.assertEqual(val, result)

    def test_get_int(self):
        val = 1
        result = parsers.get(str(val))
        self.assertEqual(val, result)

    def test_get_bool(self):
        val = True
        result = parsers.get(str(val))
        self.assertEqual(val, result)