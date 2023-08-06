# coding=utf-8
import os

__author__ = 'negash'


def md(directory):
    if not os.path.exists(directory):
        return os.makedirs(directory)