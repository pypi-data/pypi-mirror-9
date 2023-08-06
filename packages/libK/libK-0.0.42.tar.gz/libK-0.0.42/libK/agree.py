# coding=utf-8
import re

__author__ = 'negash'


def agree(input, check):
    # if args is empty
    if not input and not check: return False

    for i in check.keys():
        # if this key 'i' not in input keys
        if i not in input.keys(): return False

        # if this key 'i'  in check keys
        if check[i]:
            if check[i] == 'mail':
                check[i] = '^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$'
            if check[i] == '0000-00-00' or check[i] == 'date':
                check[i] = '^([0-9]{4})-(0[1-9]|1[0-2])-(0[1-9]|[1-2][0-9]|3[0-1])$'
            if check[i] == '0000-00-00 00:00:00' or check[i] == 'datetime':
                # regexp fo datetime
                check[i] = '^([0-9]{4})-(0[1-9]|1[0-2])-(0[1-9]|[1-2][0-9]|3[0-1]) (0[0-9]|1[0-9]|2[0-3])\:(0[0-9]|[1-5][0-9])\:(0[0-9]|[1-5][0-9])$'

            p = re.compile(ur'' + check[i])
            # find merged in regexp
            buff = re.search(p, input[i])
            # if null
            if buff is None: return False
            # if not equal
            if buff.group(0) != input[i]:  return False
    return True