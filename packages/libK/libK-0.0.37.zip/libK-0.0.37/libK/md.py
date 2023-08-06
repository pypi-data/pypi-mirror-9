import os

__author__ = 'negash'


def md(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)