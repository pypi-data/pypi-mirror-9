# coding=utf-8
__author__ = 'negash'


# convent date from string
def conv_date(date, delimiter, replace=None):
    string = ''
    if not date and not delimiter: return string
    array = {}
    buff = date.split(delimiter)
    i = 0
    for n in buff:
        array[i] = n
        i += 1
    r = {}
    for i in range(0, 6):
        if i in array.keys():
            if array[i]:
                r[i] = array[i]
            else:
                if i == 0:
                    r[i] = '1970'
                elif i in [1, 2]:
                    r[i] = '01'
                else:
                    r[i] = '00'
        else:
            r[i] = '00'
    replacements = {0: '-', 1: '-', 2: ' ', 3: ':', 4: ':'}
    # for r as $k => $d) {
    for k in r.keys():
        if replace != None:
            string += r[k]
            if k in replace.keys():
                string += replace[k]
            else:
                if k in replacements.keys():
                    string += replacements[k]
        else:
            string += r[k]
            if k in replacements.keys():
                string += replacements[k]
    return string