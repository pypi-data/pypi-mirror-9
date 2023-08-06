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

    def test_is_date_rfc_3339_allows_t_replacement(self):
        val = '2011-10-05 22:26:12-04:00'
        self.assertTrue(parsers.is_date_rfc_3339(val))

    def test_is_date_rfc_3339_allows_negative_zero(self):
        val = '2011-10-05 22:26:12-00:00'
        self.assertTrue(parsers.is_date_rfc_3339(val))

    def test_is_date_rfc_3339_requires_full_date_time(self):
        val = '2011-10-05'
        self.assertFalse(parsers.is_date_rfc_3339(val))

    def test_is_date_rfc_3339_requires_period_fractions(self):
        val = '2011-10-05T22:26:12,123-04:00'
        self.assertFalse(parsers.is_date_rfc_3339(val))

    def test_is_date_iso_8601_allows_omitting_time(self):
        val = '2011-10-05'
        self.assertTrue(parsers.is_date_iso_8601(val))

    def test_is_date_iso_8601_requires_at_least_date(self):
        val = '12'
        self.assertFalse(parsers.is_date_iso_8601(val))

    def test_is_date_iso_8601_allows_period_comma_fractions(self):
        val = '2011-10-05T22:26:12,123+04:00'
        self.assertTrue(parsers.is_date_iso_8601(val))

    def test_is_date_iso_8601_disallows_negative_zero(self):
        val = '2011-10-05T22:26:12-00:00'
        self.assertFalse(parsers.is_date_iso_8601(val))

    def test_is_date_rfc_2822(self):
        val = 'Wed, 05 Oct 2011 22:26:12 -0400'
        self.assertTrue(parsers.is_date_rfc_2822(val))

    def test_is_date_rfc_1123(self):
        val = 'Sun, 06 Nov 1994 08:49:37 GMT'
        self.assertTrue(parsers.is_date_rfc_1123(val))

    def test_is_date_rfc_850_20th_century(self):
        val = 'Sunday, 06-Nov-94 08:49:37 GMT'
        self.assertTrue(parsers.is_date_rfc_850(val))

    def test_is_date_rfc_850_21st_century(self):
        val = 'Sunday, 06-Nov-10 08:49:37 GMT'
        self.assertTrue(parsers.is_date_rfc_850(val))

    def test_is_date_ansi_c(self):
        val = 'Sun Nov  6 08:49:37 1994'
        self.assertTrue(parsers.is_date_ansi_c(val))

    def test_is_date_rfc_2616_1123(self):
        val = 'Sun, 06 Nov 1994 08:49:37 GMT'
        self.assertTrue(parsers.is_date_rfc_2616(val))

    def test_is_date_rfc_2616_850(self):
        val = 'Sunday, 06-Nov-94 08:49:37 GMT'
        self.assertTrue(parsers.is_date_rfc_2616(val))

    def test_is_date_rfc_2616_asctime(self):
        val = 'Sun Nov  6 08:49:37 1994'
        self.assertTrue(parsers.is_date_rfc_2616(val))

    def test_get_none(self):
        val = None
        result = parsers.get(None)
        self.assertEqual(val, result)

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

    def test_get_date_by_year_month_day_iso_8601(self):
        val = datetime(2010, 1, 1)
        result = parsers.get(val.strftime('%Y-%m-%d'))
        self.assertEqual(val, result)

    def test_get_date_by_year_month_day_hour_iso_8601(self):
        val = datetime(2010, 1, 1, 1)
        result = parsers.get(val.strftime('%Y-%m-%dT%H'))
        self.assertEqual(val, result)

    def test_get_date_by_year_month_day_hour_minute_iso_8601(self):
        val = datetime(2010, 1, 1, 1, 1)
        result = parsers.get(val.strftime('%Y-%m-%dT%H:%M'))
        self.assertEqual(val, result)

    def test_get_date_with_z_3339_8601(self):
        val = datetime.strptime('2015-03-16T13:29:14.50+0000', '%Y-%m-%dT%H:%M:%S.%f%z')
        result = parsers.get('2015-03-16T13:29:14.50Z')
        self.assertEqual(val, result)

    def test_get_date_with_timezone_3339_8601(self):
        val = datetime.strptime('2015-03-16T13:29:14.550+0200', '%Y-%m-%dT%H:%M:%S.%f%z')
        result = parsers.get('2015-03-16T13:29:14.550+02:00')
        self.assertEqual(val, result)

    def test_get_date_rfc_2822(self):
        val = datetime.strptime('Wed, 05 Oct 2011 22:26:12 -0400', '%a, %d %b %Y %H:%M:%S %z')
        result = parsers.get('Wed, 05 Oct 2011 22:26:12 -0400')
        self.assertEqual(val, result)

    def test_get_date_rfc_1123(self):
        val = datetime.strptime('Sun, 06 Nov 1994 08:49:37 +0000', '%a, %d %b %Y %H:%M:%S %z')
        result = parsers.get('Sun, 06 Nov 1994 08:49:37 GMT')
        self.assertEqual(val, result)

    def test_get_date_rfc_850(self):
        val = datetime.strptime('Sunday, 06-Nov-94 08:49:37 +0000', '%A, %d-%b-%y %H:%M:%S %z')
        result = parsers.get('Sunday, 06-Nov-94 08:49:37 GMT')
        self.assertEqual(val, result)

    def test_get_date_ansi_c(self):
        val = datetime.strptime('Sun Nov 6 08:49:37 1994', '%a %b %d %H:%M:%S %Y')
        result = parsers.get('Sun Nov  6 08:49:37 1994')
        self.assertEqual(val, result)