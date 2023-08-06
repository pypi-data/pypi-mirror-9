# coding=utf-8
import unittest
from libK.agree import agree

__author__ = 'Александр'


class TestAgree(unittest.TestCase):
    def test_agree(self):
        data = agree({'key': 'i@tester.ru'}, {'key': 'mail'})
        self.assertEqual(data, True)
        # error date '23' mounts
        data = agree({'key': 'i@tester.ru', 'date': '2014-23-23'}, {'key': 'mail', 'date': 'date'})
        self.assertEqual(data, False)
        # TODO bug with february!
        data = agree({'date': '2014-02-30'}, {'date': 'date'})
        self.assertEqual(data, True)
        data = agree({'date': '2014-02-30 00:00:00'}, {'date': 'datetime'})
        self.assertEqual(data, True)


if __name__ == '__main__':
    unittest.main()