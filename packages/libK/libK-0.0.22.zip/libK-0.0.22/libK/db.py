from kernel import kernel
import MySQLdb

__author__ = 'negash'


class MySQL:
    mysql = {}
    data_kernel_db = {}
    cursor = {}

    # create connection vars
    def __init__(self, dbs):
        self.data_kernel_db = dbs
        for i in self.data_kernel_db.keys():
            self.mysql[i] = ''

    # simple query to db
    def q(self, database, query, params=None):
        # create connect if is null
        if self.mysql[database] == '':
            self.mysql[database] = MySQLdb.connect(host=self.data_kernel_db[database]['host'],
                                                   user=self.data_kernel_db[database]['user'],
                                                   passwd=self.data_kernel_db[database]['passwd'],
                                                   db=self.data_kernel_db[database]['db'], charset="utf8")
            self.cursor[database] = self.mysql[database].cursor()
        # run query and return
        return self.cursor[database].execute(query, params)

    # return result
    def af(self, database):
        return self.cursor[database].fetchall()

    # return result in array
    def s(self, database, query, params=None):
        # query
        self.q(database, query, params)
        # columns in result
        columns = self.cursor[database].description
        result = []
        # create array with key => result
        for value in db.af(database):
            tmp = {}
            for (index, column) in enumerate(value):
                tmp[columns[index][0]] = column
            result.append(tmp)
        return result

    # get current result for all rows
    def sc(self, database, query, params=None):
        self.q(database, query, params)
        result = []
        for value in db.af(database):
            for (index, column) in enumerate(value):
                result.append(column)
        return result

    # select one row
    def s1(self, database, query, params=None):
        self.q(database, query, params)
        columns = self.cursor[database].description
        tmp = {}
        for value in db.af(database):
            for (index, column) in enumerate(value):
                tmp[columns[index][0]] = column
            break
        return tmp

    # select one row
    def u(self, database, table=None, update=None, where=None, params=None):
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
                where[key] = str(where[key])
                if where[key] in ['Null']:
                    whereBuff.append("`" + key + "`=" + where[key])
                elif str(where[key]).find(search) != -1:
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
            return self.q(database, str("UPDATE " + table + " SET " + s_update + s_where))

    # close all connections
    def c(self):
        for i in self.data_kernel_db.keys():
            self.mysql[i] = ''
            if i in self.cursor.keys():
                self.cursor[i].close()
                self.cursor[i] = ''


db = MySQL(kernel['db'])