# coding=utf-8
import unittest
from libK.array_to_table import array_to_table


__author__ = 'Александр'


class TestArray_to_table(unittest.TestCase):
    def test_array_to_table(self):
        data = array_to_table([{'date': '2014-01-30'}, {'date': 'date'}])
        self.assertEqual(data, '<table><tr><td>date</td></tr><tr><td>2014-01-30</td></tr><tr><td>date</td></tr></table>')


if __name__ == '__main__':
    unittest.main()