#!/usr/bin/python  
#-*- coding: utf-8 -*-
'''
Created on 2014-12-11
do...while的写法:
此规则：}和while之间留一个空格
CSC080010：{和do语句写在同一行
           }和while语句写在同一行
所以只要检查}和while在一行且无空格隔得情况
@author: panjl
'''
import os
import sys
syspath = os.path.dirname(os.path.dirname(__file__))
if not os.path.join(syspath, "tools") in sys.path:
  sys.path.append(os.path.join(syspath, "tools"))
import common
strcmp = common.StringCompareInfo()

def CheckCSC080019(filename, file_extension, clean_lines, rawlines, nesting_state, ruleCheckKey, Error, cpplines, fileErrorCount):
    lines = clean_lines.elided
    errMessage = "Code Style Rule: In the 'do' statement, there should be a space between the right curly brace '}' and the 'while' keyword."
    
    i = 0
    while i < clean_lines.NumLines():
        #将把字符串 string 中的 tab 符号转为空格，默认的空格数 tabsize 是 8.此处转换为一个空格
        string = lines[i].expandtabs(1)
        
        if common.IsBlankLine(string):
            i += 1
            continue
        
        #合并换行的行
        while '\\' == string[len(string) - 1].rstrip():
            if i + 1 < len(lines):
                i += 1
                string = string[:len(string) - 1] + lines[i].expandtabs(1)
            else:
                string = string[:len(string) - 1]
        
        #去除#define 等宏定义
        if not strcmp.Search(r'^\s*#',string):
            #查找关键字    }while
            if strcmp.Search(r'}\bwhile\b', string):
                Error(filename, lines, i, ruleCheckKey, 3, errMessage)
                fileErrorCount[0] += 1
                cpplines[i] = cpplines[i].replace("}while", "} while")
        
        i += 1
