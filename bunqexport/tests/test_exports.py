import datetime
import unittest
from .. import export


class TestExports(unittest.TestCase):
    def test_flatten(self):
        self.assertEqual(export.Payments.flatten({}), {})

    def test_flatten2(self):
        res = export.Payments.flatten({
            'a': {
                'a': 'value',
                'b': {
                    'c': None,
                    'd': 'other_val'
                }
            }, 'b': 1})
        self.assertEqual(res,
                         {'a_a': 'value',
                          'a_b_c': None,
                          'a_b_d': 'other_val',
                          'b': 1})
        
    def test_fmt_date(self):
        d = "2019-12-23 09:56:48.004134"
        self.assertEqual(export.Payments.fmt_date(d, "%d.%m.%Y"), "23.12.2019")

    def test_fmt_date_empty(self):
        self.assertEqual(export.Payments.fmt_date("", "%d.%m.%Y"), "")
        
