# coding=utf-8
import json
import os
import unittest
import sys
from libK.sftp import sftp

__author__ = 'Александр'


class TestMySFTP(unittest.TestCase):
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

        if 'sftp' in self.kernel.keys():
            for client in self.kernel['sftp'].keys():
                if self.kernel['sftp'][client]['method'] == 'sftp':
                    buff['sftp.' + client] = self.kernel['sftp'][client]

        if 'client' in self.kernel.keys():
            for client in self.kernel['client'].keys():
                if self.kernel['client'][client]['method'] == 'sftp':
                    buff['sftp.' + client] = self.kernel['client'][client]

        if 'ssh' in self.kernel.keys():
            for client in self.kernel['ssh'].keys():
                if self.kernel['ssh'][client]['method'] == 'sftp':
                    buff['sftp.' + client] = self.kernel['ssh'][client]
        self.assertEqual(sftp.data_kernel_sftp, buff)

    def test_conn(self):
        self.assertEqual(sftp.conn('sftp.clientName'), None)

    def test_l(self):
        data = sftp.l('sftp.clientName')
        buff = {u'sftp.clientName': {'listdir': "Can't use listdir(dir)",
                                     'SFTPClient': "Can't create SFTPClient.from_transport",
                                     'connect': "Can't connect by passwd",
                                     'Transport': "Can't Transport to localhost:22"}}
        self.assertEqual(data, buff)

    def test_get(self):
        data = sftp.get('sftp.clientName', '/remoteFile', '/localFile')
        buff = {u'sftp.clientName': {'SFTPClient': "Can't create SFTPClient.from_transport",
                                     'connect': "Can't connect by passwd",
                                     'Transport': "Can't Transport to localhost:22",
                                     'get': "Can't use get(remote, local)"}}
        self.assertEqual(data, buff)

    def test_put(self):
        data = sftp.put('sftp.clientName', '/localFile', '/remoteFile')
        buff = {u'sftp.clientName': {'put': "Can't use put(local, remote)",
                                     'SFTPClient': "Can't create SFTPClient.from_transport",
                                     'connect': "Can't connect by passwd",
                                     'Transport': "Can't Transport to localhost:22"}}
        self.assertEqual(data, buff)

    def test_c(self):
        self.assertEqual(sftp.c(), None)


if __name__ == '__main__':
    unittest.main()