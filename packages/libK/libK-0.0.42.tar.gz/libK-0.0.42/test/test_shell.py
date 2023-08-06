# coding=utf-8
import unittest
from libK.shell import shell

__author__ = 'Александр'


class TestShell(unittest.TestCase):
    def test_shell(self):
        shell('ls')
        self.assertEqual(shell(''), [['']])


if __name__ == '__main__':
    unittest.main()