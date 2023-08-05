# coding=utf-8
import os
import re
from libK.kernel import kernel

__author__ = 'Александр'

def in_work(p, g, s=None):
    shell_exec = ''
    if s:
        if s in kernel['servers']:
            shell_exec += 'ssh ' + s + ' '
    if p == '*':
        shell_exec += "ps aux | grep '" + g + "' | grep -v grep | awk '{for(i=1;i<=NF;i++)printf \"%s\\t\",$i (i==NF?ORS:OFS)}'"
        print(os.popen(shell_exec).read())
        string = "\t" +  os.popen(shell_exec).read()
        rows = string.split("\n")
    else:
        toPrint = '"\t"$' + re.sub(" ", '"\\\\t"$', p)
        shell_exec += "ps aux | grep '" + g + "' | grep -v grep | awk '{print "+toPrint+"}'"
        rows = os.popen(shell_exec).read().split("\n")

    rows.pop()
    result = []
    for row in rows:
        result.append(map(str.strip, row.split("\t")[1:]))
    return result