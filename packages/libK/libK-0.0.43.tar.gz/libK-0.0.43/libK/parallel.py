# coding=utf-8
__author__ = 'Александр'
from multiprocessing.dummy import Pool
from functools import partial


def parallel(parms, processes=None):
    result = {}
    if processes == None:
        processes = len(parms)
    # количество процессов
    pool = Pool(processes=processes)
    # переконвертируем данные в dict
    conventParms = {}
    if isinstance(parms, dict):
        conventParms = parms
    elif isinstance(parms, list):
        i = 0
        for buff in parms:
            conventParms[i] = buff
            i += 1
    for k in conventParms.keys():
        data = conventParms[k]
        # callback для добавление результата в ключ
        def pCallback(buff, k):
            result[k] = buff

        # забивание ключа - магия) так как в кэлбеке будет передаваться одно значение но уже для выбраного ключа
        new_callback_function = partial(pCallback, k=k)
        if isinstance(data, dict):
            func = data['f']
            if 'p' in data.keys():
                if isinstance(data['p'], tuple):
                    args = data['p']
                else:
                    args = (data['p'],)
                pool.apply_async(func, args=args, callback=new_callback_function)
            else:
                pool.apply_async(func, callback=new_callback_function)
        elif isinstance(data, list):
            func = data[0]
            if len(data) == 2:
                if isinstance(data[1], tuple):
                    args = data[1]
                else:
                    args = (data[1],)
                pool.apply_async(func, args=args, callback=new_callback_function)
            elif len(data) == 1:
                pool.apply_async(func, callback=new_callback_function)
    pool.close()
    pool.join()
    return result