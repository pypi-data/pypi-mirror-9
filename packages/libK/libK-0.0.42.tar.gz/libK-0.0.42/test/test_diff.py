# coding=utf-8
import unittest
from libK.diff import diff

__author__ = 'Александр'


class TestDiff(unittest.TestCase):
    def test_diff(self):
        a = {
            "a": "aaa",
            "d": "ddd",
            "f": "fff"
        }
        b = {
            "a": "aaa",
            "b": "bbb",
            "c": "ccc"
        }
        data = diff(a, b)
        self.assertEqual(data, ["d", "f"])


if __name__ == '__main__':
    unittest.main()