__author__ = 'negash'
from kernel import kernel
from ftplib import FTP


class MyFTP:
    ftp = {}
    data_kernel_ftp = {}

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

    def conn(self, user):
        # create connect if is null
        if self.ftp[user] == '':
            self.ftp[user] = FTP(host=self.data_kernel_ftp[user]['host'],
                                 user=self.data_kernel_ftp[user]['user'],
                                 passwd=self.data_kernel_ftp[user]['passwd'])
            if 'path' in self.data_kernel_ftp[user]:
                self.ftp[user].cwd(self.data_kernel_ftp[user]['path'])

    def li(self, user):
        ftp.conn(user)
        return self.ftp[user].retrlines('LIST')

    # list to array
    def l(self, user):
        ftp.conn(user)
        files = []

        def dir_callback(line):
            bits = line.split()
            if 'd' not in bits[0]:
                files.append(bits[-1])

        self.ftp[user].dir(dir_callback)
        return files

    def c(self):
        for i in self.data_kernel_ftp.keys():
            if self.ftp[i] != '':
                self.ftp[i].quit()
                self.ftp[i] = ''


ftp = MyFTP(kernel)