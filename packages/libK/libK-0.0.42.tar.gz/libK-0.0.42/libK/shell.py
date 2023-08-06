# coding=utf-8
__author__ = 'negash'
import subprocess as sub


def shell(command):
    if command:
        p = sub.Popen(command + ' | awk \'{for(i=1;i<=NF;i++)printf "%s\t",$i (i==NF?ORS:OFS)}\'', stdout=sub.PIPE, stderr=sub.PIPE, shell=True)
        output, errors = p.communicate()
        data = errors + output
        rows = str("\t" + data).split("\n")
        rows.pop()
    else:
        rows = ["\t"]
    buff = []
    for row in rows:
        buff.append(map(str.strip, row.split("\t")[1:]))
    return buff