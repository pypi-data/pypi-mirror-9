# coding=utf-8
__author__ = 'negash'
from kernel import kernel
from ftplib import FTP


class MyFTP:
    ftp = {}
    data_kernel_ftp = {}
    errors = {}

    # create connection vars
    def __init__(self, kernel_data):
        for i in ['client', 'ftp']:
            if i in kernel_data:
                for j in kernel_data[i].keys():
                    add = True
                    if 'method' in kernel_data[i][j]:
                        if kernel_data[i][j]['method'] == 'ftp':
                            add = True
                        else:
                            add = False
                    if add:
                        buff_name = i + '.' + j
                        self.data_kernel_ftp[buff_name] = kernel_data[i][j]
                        self.ftp[buff_name] = ''
                        self.errors[i] = {}

    def conn(self, user):
        # create connect if is null
        if self.ftp[user] == '':
            try:
                self.errors[user] = {}
                self.ftp[user] = FTP(host=self.data_kernel_ftp[user]['host'],
                                     user=self.data_kernel_ftp[user]['user'],
                                     passwd=self.data_kernel_ftp[user]['passwd'])
            except:
                self.errors[user]['connect'] = "Can't connect to " + str(self.data_kernel_ftp[user])
            if 'path' in self.data_kernel_ftp[user].keys():
                try:
                    self.ftp[user].cwd(self.data_kernel_ftp[user]['path'])
                except:
                    self.errors[user]['path'] = "Can't select path"

    def li(self, user):
        try:
            self.errors[user] = {}
            ftp.conn(user)
            return self.ftp[user].retrlines('LIST')
        except:
            self.errors[user]['retrlines'] = "Can't use retrlines('LIST')"
        if self.errors is not {}:
            return self.errors


    # list to array
    def l(self, user):
        ftp.conn(user)
        files = []

        def dir_callback(line):
            bits = line.split()
            if 'd' not in bits[0]:
                files.append(bits[-1])

        try:
            self.errors[user] = {}
            self.ftp[user].dir(dir_callback)
        except:
            self.errors[user]['dir'] = "Can't use dir(dir_callback)"
        if self.errors is not {}:
            return self.errors
        return files

    def c(self):
        for i in self.data_kernel_ftp.keys():
            try:
                self.ftp[i].quit()
            except:
                pass
            self.ftp[i] = ''


ftp = MyFTP(kernel)