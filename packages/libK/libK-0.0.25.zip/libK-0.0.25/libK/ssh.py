import paramiko
from kernel import kernel

__author__ = 'negash'


class MySSH:
    ssh = {}
    data_kernel_ssh = {}
    transport = {}

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
                        buff_name = i + '.' + j
                        self.data_kernel_ssh[buff_name] = kernel_data[i][j]
                        self.ssh[buff_name] = ''

    def conn(self, user):
        # create connect if is null
        if self.ssh[user] == '':
            # select port
            port = 22
            if 'port' in self.data_kernel_ssh[user]:
                port = self.data_kernel_ssh[user]
            # create transport
            self.ssh[user] = paramiko.SSHClient()
            self.ssh[user].set_missing_host_key_policy(paramiko.AutoAddPolicy())
            # authorize
            if 'key_filename' in self.data_kernel_ssh[user]:
                pkey = paramiko.RSAKey.from_private_key_file(self.data_kernel_ssh[user]['key_filename'])
                self.ssh[user].connect(self.data_kernel_ssh[user]['host'],
                                       username=self.data_kernel_ssh[user]['user'],
                                       pkey=pkey,
                                       port=port)
            elif 'passwd' in self.data_kernel_ssh[user]:
                self.ssh[user].connect(self.data_kernel_ssh[user]['host'],
                                       username=self.data_kernel_ssh[user]['user'],
                                       password=self.data_kernel_ssh[user]['passwd'],
                                       port=port)

    def shell(self, user, command):
        ssh.conn(user)
        stdin, stdout, stderr = self.ssh[user].exec_command(command)
        return stdout.read() + stderr.read()

    def c(self):
        for i in self.data_kernel_ssh.keys():
            if self.ssh[i] != '':
                self.ssh[i].close()
                self.ssh[i] = ''


ssh = MySSH(kernel)