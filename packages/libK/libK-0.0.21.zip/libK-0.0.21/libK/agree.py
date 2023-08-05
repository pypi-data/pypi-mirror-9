import re

__author__ = 'negash'


def agree(input, check):
    result = True
    if input and check:
        for i in check.keys():
            if i in input:
                if check[i]:
                    if check[i] == 'mail':
                        check[i] = '^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$'
                    if check[i] == '0000-00-00' or check[i] == 'date':
                        check[i] = '^([0-9]{4})-(0[1-9]|1[0-2])-(0[1-9]|[1-2][0-9]|3[0-1])$'
                    if check[i] == '0000-00-00 00:00:00' or check[i] == 'datetime':
                        check[i] = '^([0-9]{4})-(0[1-9]|1[0-2])-(0[1-9]|[1-2][0-9]|3[0-1]) (0[0-9]|1[0-9]|2[0-3])\:(0[0-9]|[1-5][0-9])\:(0[0-9]|[1-5][0-9])$'
                    p = re.compile(ur'' + check[i])
                    buff = re.search(p, input[i])
                    if buff != None:
                        if buff.group(0) != input[i]:
                            result = False
                    else:
                        result = False
            else:
                result = False
    else:
        result = False
    return result