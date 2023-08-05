# coding=utf-8
from kernel import kernel
from md import md
from kernel import HD
import StringIO
import os
import pycurl
import random
import hashlib
from urlparse import urlparse

__author__ = 'negash'


def curl(url, tor=False, post=None, cookie=False, cache=False, header=False, refer=True, addHead=None, code=False, timeout=10, VERIFYPEER=None):
    # результат
    result = ''

    # функция выполняющая сам запрос
    def query():
        b = StringIO.StringIO()
        a = pycurl.Curl()
        if header:
            a.setopt(pycurl.HEADER, 1)
        a.setopt(pycurl.WRITEFUNCTION, b.write)
        a.setopt(pycurl.URL, url)
        a.setopt(pycurl.USERAGENT, str(random.choice(kernel['user_agent'])))

        a.setopt(pycurl.TIMEOUT, timeout)
        a.setopt(pycurl.TIMEOUT, timeout)
        if addHead != None:
            a.setopt(pycurl.HTTPHEADER, addHead)
        if refer:
            a.setopt(pycurl.AUTOREFERER, 1)
            a.setopt(pycurl.FOLLOWLOCATION, 1)
            a.setopt(pycurl.MAXREDIRS, 5)
        if tor:
            a.setopt(pycurl.PROXY, 'localhost')
            a.setopt(pycurl.PROXYPORT, 9050)
            a.setopt(pycurl.PROXYTYPE, pycurl.PROXYTYPE_SOCKS5)
        if post != None:
            a.setopt(pycurl.POST, 1)
            a.setopt(pycurl.HTTPPOST, post)
        if VERIFYPEER != None:
            a.setopt(pycurl.SSL_VERIFYPEER, VERIFYPEER)
        if cookie:
            md(HD + 'trash')
            md(HD + 'trash/cookie')
            o = urlparse(url)
            a.setopt(pycurl.COOKIEJAR, HD + 'trash/cookie/' + o.netloc + '.txt')
            a.setopt(pycurl.COOKIEFILE, HD + 'trash/cookie/' + o.netloc + '.txt')
        a.perform()
        if code:
            HTTPCode = a.getinfo(pycurl.HTTP_CODE)
        a.close()
        html = b.getvalue()
        if code:
            html = {"code": HTTPCode, "html": html}
        return html

    # Логика curl

    # выполнять запрос или нет
    runQuery = True
    # Если переменная cache = True
    if cache:
        md(HD + 'trash')
        md(HD + 'trash/curl')
        # начинаем искать в кешированных данных страницу
        hash_object = hashlib.sha1(url)
        sha1 = hash_object.hexdigest()

        if os.path.isfile(HD + 'trash/curl/' + sha1):
            with open(HD + 'trash/curl/' + sha1, "r") as text_file:
                result = text_file.read()
                if code:
                    result = {"code": 200, "html": result}
        else:
            result = query()
            text_file = open(HD + 'trash/curl/' + sha1, "w")
            text_file.write(result)
            text_file.close()
        runQuery = False
    # выполняем сам запрос

    if runQuery:
        result = query()
    return result