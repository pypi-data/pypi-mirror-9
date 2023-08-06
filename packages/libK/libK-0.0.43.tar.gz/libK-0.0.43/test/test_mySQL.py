# coding=utf-8
import json
import os
import unittest
import sys
from libK.db import db
from parallel import parallel

__author__ = 'Александр'


class TestMySQL(unittest.TestCase):
    kernel = {}
    HDSlash = ''
    HD = ''
    tableName = 'tableName'


    def setUp(self):
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
                self.kernel = {"error": "kernel.json not found"}
                HD = buff
                search = False
        """
        stop
        """
        self.assertEqual(db.data_kernel_db, self.kernel['db'])

    def test_q(self):
        data = db.q('l', "SELECT NOW()")
        errors = {}
        for database in self.kernel['db'].keys():
            errors[database] = {}
        errors['l']['connect'] = "Can't connect to " + str(self.kernel['db']['l'])
        errors['l']['cursor'] = "Can't use cursor()"
        errors['l']['execute'] = "Can't use execute(query, params)"
        self.assertEqual(data, errors['l'])

    def test_af(self):
        data = db.af('l')
        buff = ((u'error', u"Can't use fetchall()"),)
        self.assertEqual(data, buff)

    def test_s(self):
        data = db.s('l', "SELECT NOW()")
        buff = [{'value': u"Can't use fetchall()", 'key': u'error'}]
        self.assertEqual(data, buff)

    def test_sc(self):
        data = db.sc('l', "SELECT NOW()")
        buff = [u'error', u"Can't use fetchall()"]
        self.assertEqual(data, buff)

    def test_s1(self):
        data = db.s1('l', "SELECT NOW()")
        buff = {'key': u'error', 'value': u"Can't use fetchall()"}
        self.assertEqual(data, buff)

    def test_u_1(self):
        data = db.u('l', self.tableName, {"packages": "libK"}, {"packages": "libIO"})
        buff = "Can't use commit()"
        self.assertEqual(data, buff)

    def test_u_2(self):
        data = db.u('l', self.tableName, {"packages": "Null"}, {"packages": "libIO"})
        buff = "Can't use commit()"
        self.assertEqual(data, buff)

    def test_u_3(self):
        data = db.u('l', self.tableName, {"packages": "UNHEX('libK')"}, {"packages": "libIO"})
        buff = "Can't use commit()"
        self.assertEqual(data, buff)

    def test_u_4(self):
        data = db.u('l', self.tableName, {"packages": "libK"}, {"packages": "Null"})
        buff = "Can't use commit()"
        self.assertEqual(data, buff)

    def test_u_5(self):
        data = db.u('l', self.tableName, {"packages": "libK"}, {"packages": "UNHEX('libIO')"})
        buff = "Can't use commit()"
        self.assertEqual(data, buff)

    def test_u_6(self):
        data = db.u('l', self.tableName, {"packages": "libK"}, {"packages": int(123)})
        buff = "Can't use commit()"
        self.assertEqual(data, buff)

    def test_s_p(self):
        data = parallel([
            [db.s, ('l', "SELECT NOW()")],
            [db.s, ('l', "SELECT NOW()")]
        ])
        self.assertEqual(data, {})

    def test_s1_p(self):
        data = parallel([
            [db.s1, ('l', "SELECT NOW()")],
            [db.s1, ('l', "SELECT NOW()")]
        ])
        self.assertEqual(data, {})

    def test_sc_p(self):
        data = parallel([
            [db.sc, ('l', "SELECT NOW()")],
            [db.sc, ('l', "SELECT NOW()")]
        ])
        self.assertEqual(data, {})

    def test_c(self):
        self.assertEqual(db.c(), None)


if __name__ == '__main__':
    unittest.main()