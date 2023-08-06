# coding=utf-8
import hashlib
import os
import unittest
import sys
from libK.curl import curl

__author__ = 'Александр'


class TestCurl(unittest.TestCase):
    def test_curl(self):
        # create trash dir
        HDSlash = ''
        if sys.platform == 'win32':
            HDSlash = '\\'
        if sys.platform == 'linux2' or sys.platform == 'darwin':
            HDSlash = '/'
        homed = sys.path[0] + HDSlash

        if not os.path.exists(homed + 'trash'):
            os.makedirs(homed + 'trash')

        url = 'qwerty'
        html = "Failed to connect to '" + url + "': Connection refused"
        data = curl(url)
        self.assertEqual(data, html)

        # tor
        data = curl(url, tor=True)
        self.assertEqual(data, html)
        # TODO create query to ya.ru

        # post
        data = curl(url, post=[('field1', 'this is a test using httppost & stuff')])
        self.assertEqual(data, html)

        # cookie
        if not os.path.exists(homed + 'trash' + HDSlash + 'cookie'):
            os.makedirs(homed + 'trash' + HDSlash + 'cookie')
        data = curl(url, cookie=True)
        self.assertEqual(data, html)

        # code
        data = curl('ya.ru', code=True, timeout=3)
        # TODO if internet is exits :)
        self.assertNotEqual(data['code'], {'code': -1})

        # cache
        # create dir
        dirName = homed + 'trash' + HDSlash + 'curl'
        if not os.path.exists(dirName):
            os.makedirs(dirName)
        # create file name
        hash_object = hashlib.sha1(url)
        sha1 = hash_object.hexdigest()
        # remove file
        fileName = homed + 'trash' + HDSlash + 'curl' + HDSlash + sha1
        if os.path.isfile(fileName):
            os.remove(fileName)
        # create cache
        data = curl(url, cache=True)
        self.assertEqual(data, html)

        # get cache
        data = curl(url, cache=True, code=True)
        self.assertEqual(data['html'], html)
        os.remove(fileName)
        os.rmdir(homed + 'trash' + HDSlash + 'curl')
        os.rmdir(homed + 'trash' + HDSlash + 'cookie')


if __name__ == '__main__':
    unittest.main()