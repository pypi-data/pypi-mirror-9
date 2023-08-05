__author__ = 'negash'


def array_to_table(data):
    result = '<table>'
    result += '  <tr><td>'
    result += '    </td><td>'.join(data[0].keys())
    result += '  </td></tr>'
    for sublist in data:
        buff = []
        for i in sublist.keys():
            buff.append(str(sublist[i]))
        result += '  <tr><td>'
        result += '    </td><td>'.join(buff)
        result += '  </td></tr>'
    result += '</table>'
    return result