# *-* coding: UTF8 -*-
#==============================================================================
"""
[sys.py] - Mempire System Management module

이 모듈은 시스템을 관리하기 위해 필요한 유틸리티 기능을 구현한 모듈입니다.

"""
__author__ = 'Herokims'
__ver__ = '150114'
__since__ = '2006-10-01'
__copyright__ = 'Copyright (c) TreeInsight.org'
__engine__ = 'Python 3.4.1'
#==============================================================================


import os


def getCurdir():
    return os.getcwd()


def isExist(pathName):
    return os.path.exists(pathName)


def makeDir(pathName):
    try:
        os.makedirs(pathName)
        return True
    except:
        return False

