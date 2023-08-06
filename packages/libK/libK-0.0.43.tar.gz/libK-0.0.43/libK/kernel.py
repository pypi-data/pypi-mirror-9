# coding=utf-8
import json
import os
import sys

if sys.platform == 'win32':
    HDSlash = '\\'
if sys.platform == 'linux2' or sys.platform == 'darwin':
    HDSlash = '/'
search = True
buff = sys.path[0]
kernel = {}
while search:
    if not buff:
        buff = HDSlash
    if buff[-1] != HDSlash:
        buff += HDSlash
    if os.path.isfile(buff + 'kernel.json'):
        # корень запушеного приложения
        HD = os.path.dirname(os.path.realpath(buff + 'kernel.json')) + HDSlash
        # чтение переменных в kernel
        with open(buff + 'kernel.json') as data_file:
            kernel = json.load(data_file)
            search = False
    else:
        buff = os.path.dirname(os.path.realpath(buff))
    if buff == HDSlash and kernel == {}:
        kernel = {"error": "kernel.json not found"}
        HD = buff
        print kernel
        search = False