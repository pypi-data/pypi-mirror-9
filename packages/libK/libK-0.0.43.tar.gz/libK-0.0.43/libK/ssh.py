# coding=utf-8
import paramiko
from kernel import kernel

__author__ = 'negash'


class MySSH:
    ssh = {}
    data_kernel_ssh = {}
    transport = {}
    errors = {}

    # create connection vars
    def __init__(self, kernel_data):
        for i in ['client', 'ssh']:
            if i in kernel_data:
                for j in kernel_data[i].keys():
                    add = True
                    if 'method' in kernel_data[i][j]:
                        if kernel_data[i][j]['method'] == 'ssh':
                            add = True
                        else:
                            add = False
                    if add:
                        buff_name = 'ssh.' + j
                        self.data_kernel_ssh[buff_name] = kernel_data[i][j]
                        self.ssh[buff_name] = ''
                        self.errors[buff_name] = {}

    def conn(self, user):
        # create connect if is null
        if self.ssh[user] == '':
            # select port
            port = 22
            if 'port' in self.data_kernel_ssh[user]:
                port = self.data_kernel_ssh[user]
            # create transport
            try:
                self.errors[user] = {}
                self.ssh[user] = paramiko.SSHClient()
                self.ssh[user].set_missing_host_key_policy(paramiko.AutoAddPolicy())
            except:
                self.errors[user]['Transport'] = "Can't Transport to " + str(
                    self.data_kernel_ssh[user]['host']) + ":" + str(port)
            # authorize
            if 'key_filename' in self.data_kernel_ssh[user]:
                try:
                    pkey = paramiko.RSAKey.from_private_key_file(self.data_kernel_ssh[user]['key_filename'])
                    self.ssh[user].connect(self.data_kernel_ssh[user]['host'],
                                           username=self.data_kernel_ssh[user]['user'],
                                           pkey=pkey,
                                           port=port)
                except:
                    self.errors[user]['connect'] = "Can't connect by key_filename"
            elif 'passwd' in self.data_kernel_ssh[user]:
                try:
                    self.ssh[user].connect(self.data_kernel_ssh[user]['host'],
                                           username=self.data_kernel_ssh[user]['user'],
                                           password=self.data_kernel_ssh[user]['passwd'],
                                           port=port)
                except:
                    self.errors[user]['connect'] = "Can't connect by passwd"

    def shell(self, user, command):
        try:
            ssh.conn(user)
            stdin, stdout, stderr = self.ssh[user].exec_command(command)
            return stdout.read() + stderr.read()
        except:
            self.errors[user]['exec_command'] = "Can't use exec_command(command)"
        if self.errors is not {}:
            return self.errors

    def c(self):
        for i in self.data_kernel_ssh.keys():
            try:
                self.ssh[i].close()
            except:
                pass
            self.ssh[i] = ''


ssh = MySSH(kernel)