__author__ = 'negash'
import os


def shell(command):
    if command:
        f = os.popen(command + ' | awk \'{for(i=1;i<=NF;i++)printf "%s\t",$i (i==NF?ORS:OFS)}\'')
        rows = str("\t" + f.read()).split("\n")
        rows.pop()
    else:
        rows = []
    buff = []
    for row in rows:
        buff.append(map(str.strip, row.split("\t")[1:]))
    return buff