# coding=utf-8
import json
import os
import unittest
import sys
from libK.ftp import ftp

__author__ = 'Александр'


class TestMyFTP(unittest.TestCase):
    kernel = {}
    HDSlash = ''
    HD = ''
    tableName = 'tableName'

    def test___init__(self):
        """
        Create kernel
        start
        """
        if sys.platform == 'win32':
            self.HDSlash = '\\'
        if sys.platform == 'linux2' or sys.platform == 'darwin':
            self.HDSlash = '/'
        self.HD = sys.path[0]
        buff = sys.path[0]
        self.kernel = {}
        search = True
        while search:
            if not buff:
                buff = self.HDSlash
            if buff[-1] != self.HDSlash:
                buff += self.HDSlash
            if os.path.isfile(buff + 'kernel.json'):
                # корень запушеного приложения
                HD = os.path.dirname(os.path.realpath(buff + 'kernel.json')) + self.HDSlash
                # чтение переменных в kernel
                with open(buff + 'kernel.json') as data_file:
                    self.kernel = json.load(data_file)
                    search = False
            else:
                buff = os.path.dirname(os.path.realpath(buff))
            if buff == self.HDSlash and self.kernel == {}:
                kernel = {"error": "kernel.json not found"}
                HD = buff
                print kernel
                search = False
        """
        stop
        """
        buff = {}
        for client in self.kernel['ftp'].keys():
            buff['ftp.' + client] = self.kernel['ftp'][client]
        self.assertEqual(ftp.data_kernel_ftp, buff)

    def test_conn(self):
        self.assertEqual(ftp.conn('ftp.clientName'), None)

    def test_li(self):
        data = ftp.li('ftp.clientName')
        buff = {'ftp': {}, 'ftp.clientName': {'path': "Can't select path",
                                              'connect': "Can't connect to {u'passwd': u'pass', u'path': u'/path', u'host': u'localhost', u'user': u'user', u'method': u'ftp'}",
                                              'retrlines': "Can't use retrlines('LIST')"}}
        self.assertEqual(data, buff)

    def test_l(self):
        data = ftp.l('ftp.clientName')
        buff = {'ftp': {}, 'ftp.clientName': {'dir': "Can't use dir(dir_callback)"}}
        self.assertEqual(data, buff)

    def test_c(self):
        self.assertEqual(ftp.c(), None)


if __name__ == '__main__':
    unittest.main()