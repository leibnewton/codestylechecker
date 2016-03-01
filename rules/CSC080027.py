#!/usr/bin/python  
#-*- coding: utf-8 -*-
'''
Created on 2014-12-15
对if/else写法的基本要求：
{前留一个空格
说明：)和{ 中间有空格(CSC030012)
所以此处只check else和{中间是否有空格
@author: panjl
'''
import os
import sys
syspath = os.path.dirname(os.path.dirname(__file__))
if not os.path.join(syspath, "tools") in sys.path:
  sys.path.append(os.path.join(syspath, "tools"))
import common
strcmp = common.StringCompareInfo()

def CheckCSC080027(filename, file_extension, clean_lines, rawlines, nesting_state, ruleCheckKey, Error, cpplines, fileErrorCount):
    lines = clean_lines.elided
    errMessage = "Code Style Rule: Please leave a space between 'else' and the left curly brace '{'."
    
    i = 0
    while i < clean_lines.NumLines():
        string = lines[i]
        #去除空行
        if common.IsBlankLine(string):
            i += 1
            continue
        
        #合并换行的行
        while '\\' == string[len(string) - 1].rstrip():
            if i + 1 < len(lines):
                i += 1
                string = string[:len(string) - 1] + lines[i]
            else:
                string = string[:len(string) - 1]
        
        #去除#define 等宏定义
        if not strcmp.Search(r'^\s*#',string):
            #查找关键字  else{
            findElseLeftBraces = strcmp.Search(r'\belse\b{', string)
            
            if findElseLeftBraces:
                 
                Error(filename, lines, i, ruleCheckKey, 3, errMessage)
                fileErrorCount[0] += 1
                cpplines[i] = cpplines[i].replace("else{", "else {")
            
        i += 1
