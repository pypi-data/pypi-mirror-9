# coding=utf-8
__author__ = 'negash'

# convent array with json data to html table
def array_to_table(data):
    result = '<table>'
    result += '<tr><td>'
    # create headers
    result += '</td><td>'.join(data[0].keys())
    result += '</td></tr>'
    for sublist in data:
        buff = []
        for i in sublist.keys():
            buff.append(str(sublist[i]))
        result += '<tr><td>'
        result += '</td><td>'.join(buff)
        result += '</td></tr>'
    result += '</table>'
    return result