# coding=utf-8
import re
import subprocess as sub
from libK.kernel import kernel

__author__ = 'Александр'


def in_work(p, g, s=None):
    shell_exec = ''
    if s:
        if s in kernel['servers']:
            shell_exec += 'ssh ' + s + ' '
    if p == '*':
        shell_exec += "ps aux | grep '" + g + "' | grep -v grep | awk '{for(i=1;i<=NF;i++)printf \"%s\\t\",$i (i==NF?ORS:OFS)}'"
        p = sub.Popen(shell_exec, stdout=sub.PIPE, stderr=sub.PIPE, shell=True)
        output, errors = p.communicate()
        data = errors + output
        string = "\t" + data
        rows = string.split("\n")
    else:
        toPrint = '"\t"$' + re.sub(" ", '"\\\\t"$', p)
        shell_exec += "ps aux | grep '" + g + "' | grep -v grep | awk '{print " + toPrint + "}'"
        p = sub.Popen(shell_exec, stdout=sub.PIPE, stderr=sub.PIPE, shell=True)
        output, errors = p.communicate()
        data = errors + output
        rows = data.split("\n")

    rows.pop()
    if not rows:
        rows = ["\t"]
    result = []
    for row in rows:
        result.append(map(str.strip, row.split("\t")[1:]))
    return result