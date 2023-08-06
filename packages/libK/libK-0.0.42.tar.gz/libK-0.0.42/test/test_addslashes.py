# coding=utf-8
import unittest
from libK.addslashes import addslashes


__author__ = 'Александр'


class TestAddslashes(unittest.TestCase):
    def test_addslashes(self):
        data = addslashes('"SQl QUERY FROM EXAMPLE" and some text')
        self.assertEqual(data, '\\"SQl QUERY FROM EXAMPLE\\" and some text')


if __name__ == '__main__':
    unittest.main()