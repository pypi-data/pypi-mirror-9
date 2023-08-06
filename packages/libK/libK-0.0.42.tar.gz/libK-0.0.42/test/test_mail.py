# coding=utf-8
import json
import os
import unittest
import sys
from libK.mail import mail

__author__ = 'Александр'


class TestMail(unittest.TestCase):
    def test_mail(self):
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
        array = {}
        self.assertEqual(mail(array), {"error": "need in 'from'"})

        array["from"] = "SMTPkey"
        self.assertEqual(mail(array), {"error": "need in 'text'"})

        array["text"] = "Some HTML text"
        array["subject"] = "Some subject"
        self.assertEqual(mail(array), [{'error': "Can't use connect()"}, {'error': "Can't use login()"}, {'error': "Can't use sendmail()"}, {'error': "Can't use quit()"}])

        buffMailTo = kernel['mailTo']
        kernel.pop("mailTo", None)
        self.assertEqual(mail(array), [{'error': "Can't use connect()"}, {'error': "Can't use login()"}, {'error': "Can't use sendmail()"}, {'error': "Can't use quit()"}])

        kernel['mailTo'] = buffMailTo
        array["files"] = [HD + 'kernel.json']
        self.assertEqual(mail(array), [{'error': "Can't use connect()"}, {'error': "Can't use login()"}, {'error': "Can't use sendmail()"}, {'error': "Can't use quit()"}])