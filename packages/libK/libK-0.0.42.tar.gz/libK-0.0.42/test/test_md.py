# coding=utf-8
import json
import os
import unittest
import sys
from libK.md import md

__author__ = 'Александр'


class TestMd(unittest.TestCase):
    def test_md(self):
        """
        Create kernel
        start
        """
        if sys.platform == 'win32':
            HDSlash = '\\'
        if sys.platform == 'linux2' or sys.platform == 'darwin':
            HDSlash = '/'
        HD = sys.path[0]
        buff = sys.path[0]
        kernel = {}
        search = True
        while search:
            if not buff:
                buff = HDSlash
            if buff[-1] != HDSlash:
                buff += HDSlash
            if os.path.isfile(buff + 'kernel.json'):
                # корень запушеного приложения
                HD = os.path.dirname(os.path.realpath(buff + 'kernel.json')) + HDSlash
                # чтение переменных в kernel
                with open(buff + 'kernel.json') as data_file:
                    kernel = json.load(data_file)
                    search = False
            else:
                buff = os.path.dirname(os.path.realpath(buff))
            if buff == HDSlash and kernel == {}:
                kernel = {"error": "kernel.json not found"}
                HD = buff
                search = False
        """
        stop
        """
        buff = md(HD + "md_TEST")
        if os.path.exists(HD + "md_TEST"):
            self.assertEqual(buff, None)
        os.rmdir(HD + "md_TEST")


if __name__ == '__main__':
    unittest.main()