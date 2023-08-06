# coding=utf-8
from db import db
from libK.kernel import kernel

__author__ = 'negash'


def get_kernel(database):
    configs = db.s(kernel['config']['db'], "SELECT * FROM " + kernel['config']['base'] + "." + database)
    if 'key' in configs[0]:
        tmp = {}
        for config in configs:
            tmp[config['key']] = config['value']
    else:
        tmp = []
        for config in configs:
            tmp.append(config['value'])
    return tmp