# coding=utf-8
import paramiko
from kernel import kernel

__author__ = 'negash'


class MySFTP:
    sftp = {}
    data_kernel_sftp = {}
    transport = {}
    errors = {}

    # create connection vars
    def __init__(self, kernel_data):
        for i in ['client', 'sftp', 'ssh']:
            if i in kernel_data:
                for j in kernel_data[i].keys():
                    add = True
                    if 'method' in kernel_data[i][j]:
                        if kernel_data[i][j]['method'] == 'sftp':
                            add = True
                        else:
                            add = False
                    if add:
                        buff_name = 'sftp.' + j
                        self.data_kernel_sftp[buff_name] = kernel_data[i][j]
                        self.sftp[buff_name] = ''
                        self.errors[buff_name] = {}

    # connect to some sftp
    def conn(self, user):
        # create connect if is null
        if self.sftp[user] == '':
            # select port
            port = 22
            if 'port' in self.data_kernel_sftp[user]:
                port = self.data_kernel_sftp[user]
            # create transport
            try:
                self.errors[user] = {}
                self.transport[user] = paramiko.Transport((self.data_kernel_sftp[user]['host'], port))
            except:
                self.errors[user]['Transport'] = "Can't Transport to " + str(
                    self.data_kernel_sftp[user]['host']) + ":" + str(port)
            # authorize
            if 'key_filename' in self.data_kernel_sftp[user]:
                try:
                    pkey = paramiko.RSAKey.from_private_key_file(self.data_kernel_sftp[user]['key_filename'])
                    self.transport[user].connect(username=self.data_kernel_sftp[user]['user'], pkey=pkey)
                except:
                    self.errors[user]['connect'] = "Can't connect by key_filename"
            elif 'passwd' in self.data_kernel_sftp[user]:
                try:
                    self.transport[user].connect(username=self.data_kernel_sftp[user]['user'],
                                                 password=self.data_kernel_sftp[user]['passwd'])
                except:
                    self.errors[user]['connect'] = "Can't connect by passwd"
            try:
                self.sftp[user] = paramiko.SFTPClient.from_transport(self.transport[user])
            except:
                self.errors[user]['SFTPClient'] = "Can't create SFTPClient.from_transport"

    # list in dir
    def l(self, user, dir='./'):
        try:
            self.errors[user] = {}
            sftp.conn(user)
            return self.sftp[user].listdir(dir)
        except:
            self.errors[user]['listdir'] = "Can't use listdir(dir)"
        if self.errors is not {}:
            return self.errors

    # get file
    def get(self, user, remote, local):
        try:
            self.errors[user] = {}
            sftp.conn(user)
            return self.sftp[user].get(remote, local)
        except:
            self.errors[user]['get'] = "Can't use get(remote, local)"
        if self.errors is not {}:
            return self.errors

    # get file
    def put(self, user, local, remote):
        try:
            self.errors[user] = {}
            sftp.conn(user)
            return self.sftp[user].put(local, remote)
        except:
            self.errors[user]['put'] = "Can't use put(local, remote)"
        if self.errors is not {}:
            return self.errors

    # close all connections
    def c(self):
        for i in self.data_kernel_sftp.keys():
            try:
                self.sftp[i].close()
            except:
                pass
            self.sftp[i] = ''


sftp = MySFTP(kernel)