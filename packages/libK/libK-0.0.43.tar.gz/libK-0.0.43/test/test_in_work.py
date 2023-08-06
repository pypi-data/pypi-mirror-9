# coding=utf-8
import unittest
from libK.kernel import kernel
from libK.in_work import in_work

__author__ = 'Александр'


class TestIn_work(unittest.TestCase):
    def test_in_work(self):
        kernel['servers'] = ['server.ru']
        in_work('*', 'python', 'server.ru')
        in_work('1 2', 'python')


if __name__ == '__main__':
    unittest.main()