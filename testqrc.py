# -*- coding: utf-8 -*-
"""
Created on Fri Mar  4 17:59:55 2016

@author: navicloud
"""

def testqrc():
    from PyQt4 import QtCore
    import resources_qrc
    names = [':/stylechecker.png', ':/images/stylechecker.png',
             ':/common.py', ':/tools/common.py', ':/codes/common.py']
    for n in names:
        info = QtCore.QFileInfo(n)
        print info.exists(), info.size(), info.absoluteFilePath()

if __name__ == '__main__':
    testqrc()
