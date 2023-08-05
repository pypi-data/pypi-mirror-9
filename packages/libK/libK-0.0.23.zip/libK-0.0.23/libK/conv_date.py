__author__ = 'negash'


def conv_date(date, delimiter, replace=None):
    if date and delimiter:
        str = ''
        array = {}
        buff = date.split(delimiter)
        i = 0
        for n in buff:
            array[i] = n
            i += 1
        r = {}
        for i in range(0, 6):
            if i in array.keys():
                r[i] = array[i]
            else:
                if i == 0:
                    r[i] = '1970'
                elif i in [1, 2]:
                    r[i] = '01'
                else:
                    r[i] = '00'
        replacements = {0: '-', 1: '-', 2: ' ', 3: ':', 4: ':'}
        # for r as $k => $d) {
        for k in r.keys():
            if replace != None:
                str += r[k]
                if k in replace.keys():
                    str += replace[k]
                else:
                    if k in replacements.keys():
                        str += replacements[k]
            else:
                str += r[k]
                if k in replacements.keys():
                    str += replacements[k]
        return str