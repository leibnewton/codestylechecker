#!/usr/bin/python  
#-*- coding: utf-8 -*-
'''
Created on 2014-12-8
do...while语句中，do关键字之后留一个空格再跟大括号{
@author: panjl
'''
import os
import sys
syspath = os.path.dirname(os.path.dirname(__file__))
if not os.path.join(syspath, "tools") in sys.path:
  sys.path.append(os.path.join(syspath, "tools"))
import common
strcmp = common.StringCompareInfo()

def CheckCSC030022(filename, file_extension, clean_lines, rawlines, nesting_state, ruleCheckKey, Error, cpplines, fileErrorCount):
    lines = clean_lines.elided
    errMessage = "Code Style Rule: In the 'do' statement, there should be a space between the 'do' keyword and the left curly brace '{'."
    
    i = 0
    while i < clean_lines.NumLines():
        #将把字符串 string 中的 tab 符号转为空格，默认的空格数 tabsize 是 8.
        string = lines[i].expandtabs(1)
        
        if common.IsBlankLine(string):
            i += 1
            continue
        #记录换行前位置
        errorline = 0
        
        #合并换行的行
        while '\\' == string[len(string) - 1].rstrip():
            if i + 1 < len(lines):
                if 0 == errorline:
                    errorline = i
                i += 1
                string = string[:len(string) - 1] + lines[i].expandtabs(1)
            else:
                string = string[:len(string) - 1]
            
        #去除#define 等宏定义
        if not strcmp.Search(r'^\s*#',string):
            #查找关键字  do{
            # do{ 前有任意非空字符，或后有任意非空字符
            finddo = strcmp.Search(r'\bdo\b{', string)
            
            if finddo:
                if 0 == errorline:
                    Error(filename, lines, i, ruleCheckKey, 3, errMessage)
                    fileErrorCount[0] += 1
                    cpplines[i] = cpplines[i].replace("do{", "do {")
                else:
                    Error(filename, lines, errorline, ruleCheckKey, 3, errMessage)
                    fileErrorCount[0] += 1
                    cpplines[errorline] = cpplines[errorline].replace("do{", "do {")
         
        # i < clean_lines.NumLines()
        i += 1
