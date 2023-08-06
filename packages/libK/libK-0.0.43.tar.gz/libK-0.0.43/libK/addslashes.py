# coding=utf-8
__author__ = 'Александр'


def addslashes(s):
    # convent elements in str
    d = {
        '"': '\\"',
        "\0": "\\\0",
        "\\": "\\\\"
    }
    return ''.join(d.get(c, c) for c in s)