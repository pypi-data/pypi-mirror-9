# coding=utf-8
import unittest
from libK.parallel import parallel

__author__ = 'Александр'


class TestParallel(unittest.TestCase):
    def test_parallel(self):
        def testFun(num, num2=None):
            if num2 is None:
                num2 = 2
            return num * num2

        def testFun2():
            return 2 * 4

        params = [
            {"p": 2, "f": testFun},
            {"p": 2, "f": testFun},
            {"p": 2, "f": testFun},
            {"p": 2, "f": testFun}
        ]
        self.assertEqual(parallel(params), {0: 4, 1: 4, 2: 4, 3: 4})

        params = [
            [testFun, 2],
            [testFun, 2],
            [testFun, 2],
            [testFun, 2]
        ]
        self.assertEqual(parallel(params), {0: 4, 1: 4, 2: 4, 3: 4})

        params = {
            "p1": {"p": (2, 3), "f": testFun},
            "p2": {"p": (2, 3), "f": testFun},
            "p3": {"p": (2, 3), "f": testFun},
            "p4": {"p": (2, 3), "f": testFun}
        }
        self.assertEqual(parallel(params), {'p1': 6, 'p2': 6, 'p3': 6, 'p4': 6})

        params = {
            "p1": [testFun, (2, 3)],
            "p2": [testFun, (2, 3)],
            "p3": [testFun, (2, 3)],
            "p4": [testFun, (2, 3)]
        }
        self.assertEqual(parallel(params), {'p1': 6, 'p2': 6, 'p3': 6, 'p4': 6})

        params = {
            "p1": [testFun2],
            "p2": [testFun2],
            "p3": [testFun2],
            "p4": [testFun2]
        }
        self.assertEqual(parallel(params), {'p1': 8, 'p2': 8, 'p3': 8, 'p4': 8})

        params = {
            "p1": {"f": testFun2},
            "p2": {"f": testFun2},
            "p3": {"f": testFun2},
            "p4": {"f": testFun2}
        }
        self.assertEqual(parallel(params), {'p1': 8, 'p2': 8, 'p3': 8, 'p4': 8})


if __name__ == '__main__':
    unittest.main()