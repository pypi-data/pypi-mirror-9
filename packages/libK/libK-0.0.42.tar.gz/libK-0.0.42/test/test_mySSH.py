# coding=utf-8
import json
import os
import unittest
import sys
from libK.ssh import ssh

__author__ = 'Александр'


class TestMySSH(unittest.TestCase):
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
                if self.kernel['sftp'][client]['method'] == 'ssh':
                    buff['ssh.' + client] = self.kernel['sftp'][client]

        if 'client' in self.kernel.keys():
            for client in self.kernel['client'].keys():
                if self.kernel['client'][client]['method'] == 'ssh':
                    buff['ssh.' + client] = self.kernel['client'][client]

        if 'ssh' in self.kernel.keys():
            for client in self.kernel['ssh'].keys():
                if self.kernel['ssh'][client]['method'] == 'ssh':
                    buff['ssh.' + client] = self.kernel['ssh'][client]
        self.assertEqual(ssh.data_kernel_ssh, buff)

    def test_conn(self):
        self.assertEqual(ssh.conn('ssh.clientName'), None)

    def test_shell(self):
        data = ssh.shell('ssh.clientName', 'date')
        buff = {u'ssh.clientName': {'connect': "Can't connect by passwd", 'exec_command': "Can't use exec_command(command)"}}
        self.assertEqual(data, buff)

    def test_c(self):
        self.assertEqual(ssh.c(), None)


if __name__ == '__main__':
    unittest.main()