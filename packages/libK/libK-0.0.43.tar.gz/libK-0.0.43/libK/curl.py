# coding=utf-8
from kernel import kernel, HDSlash
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
        # if use HEADER add this to curl
        if header: a.setopt(pycurl.HEADER, 1)
        a.setopt(pycurl.WRITEFUNCTION, b.write)
        a.setopt(pycurl.URL, url)
        a.setopt(pycurl.USERAGENT, str(random.choice(kernel['user_agent'])))
        a.setopt(pycurl.TIMEOUT, timeout)
        a.setopt(pycurl.TIMEOUT, timeout)
        # if use HTTPHEADER add this to curl
        if addHead is not None: a.setopt(pycurl.HTTPHEADER, addHead)
        if refer:
            a.setopt(pycurl.AUTOREFERER, 1)
            a.setopt(pycurl.FOLLOWLOCATION, 1)
            a.setopt(pycurl.MAXREDIRS, 5)
        # use query with TOR
        if tor:
            a.setopt(pycurl.PROXY, 'localhost')
            a.setopt(pycurl.PROXYPORT, 9050)
            a.setopt(pycurl.PROXYTYPE, pycurl.PROXYTYPE_SOCKS5)
        # if post data in query
        if post is not None:
            a.setopt(pycurl.POST, 1)
            a.setopt(pycurl.HTTPPOST, post)
        if VERIFYPEER is not None: a.setopt(pycurl.SSL_VERIFYPEER, VERIFYPEER)
        if cookie:
            md(HD + 'trash')
            md(HD + 'trash'+HDSlash+'cookie')
            o = urlparse(url)
            a.setopt(pycurl.COOKIEJAR, HD + 'trash'+HDSlash+'cookie'+HDSlash+  o.netloc + '.txt')
            a.setopt(pycurl.COOKIEFILE, HD + 'trash'+HDSlash+'cookie'+HDSlash+ o.netloc + '.txt')
        # CODE of query
        HTTPCode = -1
        try:
            a.perform()
            # if need to return HTTP_CODE
            if code:
                HTTPCode = a.getinfo(pycurl.HTTP_CODE)
            a.close()
            # save result to var
            html = b.getvalue()
        except:
            html = "Failed to connect to '" + url + "': Connection refused"
        # if need to return HTTP_CODE
        if code:
            html = {"code": HTTPCode, "html": html}
        return html

    # Логика curl

    # выполнять запрос или нет
    runQuery = True
    # Если переменная cache = True
    if cache:
        md(HD + 'trash')
        md(HD + 'trash'+HDSlash+'curl')
        # начинаем искать в кешированных данных страницу
        hash_object = hashlib.sha1(url)
        sha1 = hash_object.hexdigest()

        if os.path.isfile(HD + 'trash'+HDSlash+'curl'+HDSlash + sha1):
            with open(HD + 'trash'+HDSlash+'curl'+HDSlash + sha1, "r") as text_file:
                result = text_file.read()
                if code:
                    result = {"code": 200, "html": result}
        else:
            result = query()
            text_file = open(HD + 'trash'+HDSlash+'curl'+HDSlash + sha1, "w")
            text_file.write(result)
            text_file.close()
        runQuery = False
    # выполняем сам запрос

    if runQuery:
        result = query()
    return result