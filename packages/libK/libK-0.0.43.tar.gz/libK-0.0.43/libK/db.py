# coding=utf-8
import traceback
import multiprocessing
from kernel import kernel
import MySQLdb

__author__ = 'negash'


class MySQL:
    mysql = {}
    data_kernel_db = {}
    cursor = {}
    errors = {}

    def __pool(self):
        p = {
            '__bootstrap': 'self.__bootstrap_inner()',
            '__bootstrap_inner': 'self.run()',
            'run': 'self.__target(*self.__args, **self.__kwargs)',
            'worker': 'result = (True, func(*args, **kwds))'
        }
        for row in traceback.extract_stack():
            if row[2] in p.keys():
                if row[3] == p[row[2]]:
                    del p[row[2]]
        if p == {}:
            return True
        return False

    def __closePool(self, database, pool):
        del self.mysql[database][pool]
        self.cursor[database][pool].close()
        del self.cursor[database][pool]
        del self.errors[database][pool]

    # create connection vars
    def __init__(self, dbs):
        self.data_kernel_db = dbs
        for i in self.data_kernel_db.keys():
            self.mysql[i] = {}
            self.mysql[i][1] = ''
            self.cursor[i] = {}
            self.cursor[i][1] = ''
            self.errors[i] = {}
            self.errors[i][1] = ''

    # simple query to db
    def q(self, database, query, params=None, pool=1):
        # create connect if is null
        if pool not in self.mysql[database].keys():
            self.mysql[database][pool] = ''
        if self.mysql[database][pool] == '':
            try:
                self.errors[database][pool] = {}
                self.mysql[database][pool] = MySQLdb.connect(host=self.data_kernel_db[database]['host'],
                                                             user=self.data_kernel_db[database]['user'],
                                                             passwd=self.data_kernel_db[database]['passwd'],
                                                             db=self.data_kernel_db[database]['db'],
                                                             charset="utf8",
                                                             local_infile=True)
            except:
                self.errors[database][pool]['connect'] = "Can't connect to " + str(self.data_kernel_db[database])
            try:
                self.cursor[database][pool] = self.mysql[database][pool].cursor()
            except:
                self.errors[database][pool]['cursor'] = "Can't use cursor()"
        # run query and return
        try:
            return self.cursor[database][pool].execute(query, params)
        except:
            self.errors[database][pool]['execute'] = "Can't use execute(query, params)"
        if self.errors[database][pool] is not {}:
            return self.errors[database][pool]

    # return result
    def af(self, database, pool=1):
        try:
            self.errors[database][pool] = {}
            return self.cursor[database][pool].fetchall()
        except:
            return ((u'error', u'Can\'t use fetchall()'),)

    # return result in array
    def s(self, database, query, params=None, pool=1):
        __pool = self.__pool()
        if __pool:
            pool = multiprocessing.Process()._identity[0]
        # query
        self.q(database, query, params, pool)
        # columns in result
        columns = ()
        try:
            self.errors[database][pool] = {}
            columns = self.cursor[database][pool].description
        except:
            pass
        if columns is None or columns is ():
            columns = (('key',), ('value',))
        result = []
        # create array with key => result
        for value in db.af(database, pool):
            tmp = {}
            for (index, column) in enumerate(value):
                tmp[columns[index][0]] = column
            result.append(tmp)
        if __pool:
            self.__closePool(database, pool)
        return result

    # get current result for all rows
    def sc(self, database, query, params=None, pool=1):
        __pool = self.__pool()
        if __pool:
            pool = multiprocessing.Process()._identity[0]
        self.q(database, query, params, pool)
        result = []
        for value in db.af(database, pool):
            for (index, column) in enumerate(value):
                result.append(column)
        if __pool:
            self.__closePool(database, pool)
        return result

    # select one row
    def s1(self, database, query, params=None, pool=1):
        __pool = self.__pool()
        if __pool:
            pool = multiprocessing.Process()._identity[0]
        self.q(database, query, params, pool)
        # columns in result
        columns = ()
        try:
            self.errors[database][pool] = {}
            columns = self.cursor[database][pool].description
        except:
            pass
        if columns is None or columns is ():
            columns = (('key',), ('value',))
        tmp = {}
        for value in db.af(database, pool):
            for (index, column) in enumerate(value):
                tmp[columns[index][0]] = column
            break
        if __pool:
            self.__closePool(database, pool)
        return tmp

    # select one row
    def u(self, database, table=None, update=None, where=None, pool=1):
        updateBuff = []
        search = "UNHEX('"
        # array of update
        if update != None:
            for key in update.keys():
                if update[key] in ['Null']:
                    updateBuff.append("`" + key + "`=" + update[key])
                elif update[key].find(search) != -1:
                    updateBuff.append("`" + key + "`=" + update[key])
                else:
                    updateBuff.append("`" + key + "`='" + update[key] + "'")

        # string of update
        s_update = ''
        if updateBuff:
            s_update = ', '.join(updateBuff)

        whereBuff = []
        # array of where
        if where != None:
            for key in where.keys():
                if not isinstance(where[key], basestring):
                    where[key] = str(where[key])
                if type(where[key]) == 'encode':
                    where[key] = str(where[key].text().encode('utf-8'))
                if where[key] in ['Null']:
                    whereBuff.append("`" + key + "`=" + where[key])
                elif where[key].find(search) != -1:
                    whereBuff.append("`" + key + "`=" + where[key])
                else:
                    whereBuff.append("`" + key + "`='" + where[key] + "'")

        # string of where
        s_where = ''
        if whereBuff:
            s_where = ' WHERE ' + ' AND '.join(whereBuff)

        # create database.table query
        buffTable = table.split('.')
        if len(buffTable) < 2:
            table = self.data_kernel_db[database]['db'] + '.' + table
        # query
        if table and update and s_update:
            Qstring = "UPDATE " + table + " SET " + s_update + s_where
            self.q(database, Qstring.encode('utf-8'), pool=pool)
            try:
                self.errors[database][pool] = {}
                return self.mysql[database][pool].commit()
            except:
                self.errors[database][pool]['commit'] = "Can't use commit()"
                return self.errors[database][pool]['commit']

    # close all connections
    def c(self):
        for i in self.data_kernel_db.keys():
            self.mysql[i] = {}
            self.mysql[i][1] = ''
            if i in self.cursor.keys():
                for j in self.cursor[i].keys():
                    try:
                        self.cursor[i][j].close()
                        del self.cursor[i][j]
                    except:
                        pass
                    self.cursor[i] = {}
                    self.cursor[i][1] = ''
                self.cursor[i] = {}
                self.cursor[i][1] = ''
                self.errors[i] = {}
                self.errors[i][1] = ''


db = MySQL(kernel['db'])