# coding=utf-8
import unittest
from libK.get_kernel import get_kernel

__author__ = 'Александр'


class TestGet_kernel(unittest.TestCase):
    def test_get_kernel(self):
        data = get_kernel('mail')
        buff = {u'error': u"Can't use fetchall()"}
        self.assertEqual(data, buff)
        get_kernel('folder')


if __name__ == '__main__':
    unittest.main()