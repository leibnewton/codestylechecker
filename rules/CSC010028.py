#!/usr/bin/python  
#-*- coding: utf-8 -*-
'''
Created on 2015-1-8
在文件名中只能使用下列ASCII字符，其他字符均不允许使用。[必须]
1、半角英文字母（a~z, A~Z）
2、数字（0~9）
3、分割字符：_
@author: panjl
'''
import os
import sys
syspath = os.path.dirname(os.path.dirname(__file__))
if not os.path.join(syspath, "tools") in sys.path:
  sys.path.append(os.path.join(syspath, "tools"))
import common
strcmp = common.StringCompareInfo()

def CheckCSC010028(filename, file_extension, clean_lines, rawlines, nesting_state, ruleCheckKey, Error, cpplines, fileErrorCount):
    errMessage = 'Code Style Rule: The file name can only contain: half-width English letters(a ~ z, A ~ Z), digital(0-9), and the underscore(_).'
    
    #去除文件路径
    filePath, baseName = os.path.split(filename)
    
    #查找文件扩展名
    interception = baseName.rfind('.')
    if -1 == interception:
        #没有扩展名，直接检查
        if strcmp.Search(r'[^a-zA-Z0-9_]', baseName):
            Error(filename, [], 1, ruleCheckKey, 3, errMessage)
    else:
        #去除扩展名，让后检查
        baseName = baseName[:baseName.rfind('.')]
        if not strcmp.Search(r'^[a-zA-Z0-9_]+$', baseName):
            Error(filename, [], 1, ruleCheckKey, 3, errMessage)
