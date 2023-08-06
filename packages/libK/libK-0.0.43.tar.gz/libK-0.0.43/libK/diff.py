# coding=utf-8
__author__ = 'negash'

# function for difference array's
def diff(a, b):
    b = set(b)
    return [aa for aa in a if aa not in b]