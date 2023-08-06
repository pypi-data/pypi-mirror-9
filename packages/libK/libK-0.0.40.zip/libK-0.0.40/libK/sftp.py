import paramiko
from kernel import kernel

__author__ = 'negash'


class MySFTP:
    sftp = {}
    data_kernel_sftp = {}
    transport = {}

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
                        buff_name = i + '.' + j
                        self.data_kernel_sftp[buff_name] = kernel_data[i][j]
                        self.sftp[buff_name] = ''

    # connect to some sftp
    def conn(self, user):
        # create connect if is null
        if self.sftp[user] == '':
            # select port
            port = 22
            if 'port' in self.data_kernel_sftp[user]:
                port = self.data_kernel_sftp[user]
            # create transport
            self.transport[user] = paramiko.Transport((self.data_kernel_sftp[user]['host'], port))
            # authorize
            if 'key_filename' in self.data_kernel_sftp[user]:
                pkey = paramiko.RSAKey.from_private_key_file(self.data_kernel_sftp[user]['key_filename'])
                self.transport[user].connect(username=self.data_kernel_sftp[user]['user'], pkey=pkey)
            elif 'passwd' in self.data_kernel_sftp[user]:
                self.transport[user].connect(username=self.data_kernel_sftp[user]['user'],
                                             password=self.data_kernel_sftp[user]['passwd'])
            self.sftp[user] = paramiko.SFTPClient.from_transport(self.transport[user])

    # list in dir
    def l(self, user, dir='./'):
        sftp.conn(user)
        return self.sftp[user].listdir(dir)

    # get file
    def get(self, user, remote, local):
        sftp.conn(user)
        return self.sftp[user].get(remote, local)

    # get file
    def put(self, user, local, remote):
        sftp.conn(user)
        return self.sftp[user].put(local, remote)

    # close all connections
    def c(self):
        for i in self.data_kernel_sftp.keys():
            if self.sftp[i] != '':
                self.sftp[i].close()
                self.sftp[i] = ''


sftp = MySFTP(kernel)