# coding=utf-8
import unittest
from libK.conv_date import conv_date

__author__ = 'Александр'


class TestConv_date(unittest.TestCase):
    def test_conv_date(self):
        data = conv_date('2015_01_23', '_')
        self.assertEqual(data, '2015-01-23 00:00:00')

        data = conv_date('2015_01_23', '_', {0: '#'})
        self.assertEqual(data, '2015#01-23 00:00:00')

        data = conv_date('2015_01_23', '_', {0: '#', 4: '^'})
        self.assertEqual(data, '2015#01-23 00:00^00')

        data = conv_date('2015_04_', '_')
        self.assertEqual(data, '2015-04-01 00:00:00')

        data = conv_date('2015__30', '_')
        self.assertEqual(data, '2015-01-30 00:00:00')

        data = conv_date('_04_30', '_')
        self.assertEqual(data, '1970-04-30 00:00:00')

        data = conv_date('2015__', '_')
        self.assertEqual(data, '2015-01-01 00:00:00')

        data = conv_date('_05_', '_')
        self.assertEqual(data, '1970-05-01 00:00:00')

        data = conv_date('__05', '_')
        self.assertEqual(data, '1970-01-05 00:00:00')

        data = conv_date('__', '_')
        self.assertEqual(data, '1970-01-01 00:00:00')

        data = conv_date('2015_01_23_04_05_', '_')
        self.assertEqual(data, '2015-01-23 04:05:00')

        data = conv_date('___14__05', '_')
        self.assertEqual(data, '1970-01-01 14:00:05')


if __name__ == '__main__':
    unittest.main()