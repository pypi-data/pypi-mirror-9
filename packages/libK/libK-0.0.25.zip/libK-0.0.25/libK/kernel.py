# coding=utf-8
import json
import os
import sys

search = True
buff = sys.path[0]
kernel = {}
while search:
    if not buff:
        buff = '/'
    if buff[-1] != '/':
        buff += '/'
    if os.path.isfile(buff + 'kernel.json'):
        # корень запушеного приложения
        HD = os.path.dirname(os.path.realpath(buff + 'kernel.json')) + '/'
        # чтение переменных в kernel
        with open(buff + 'kernel.json') as data_file:
            kernel = json.load(data_file)
            search = False
    else:
        buff = os.path.dirname(os.path.realpath(buff))
    if buff == '/' and kernel == {}:
        kernel = {"error": "kernel.json not found"}
        HD = buff
        print kernel
        search = False