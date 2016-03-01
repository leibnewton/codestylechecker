#!/usr/bin/python  
#-*- coding: utf-8 -*- 
'''
Created on 2014-12-31
namespace的定义，需要遵循下面的规范。[必须]
每个成员单独占一行
@author: panjl
'''
import os
import sys
syspath = os.path.dirname(os.path.dirname(__file__))
if not os.path.join(syspath, "tools") in sys.path:
  sys.path.append(os.path.join(syspath, "tools"))
import common
strcmp = common.StringCompareInfo()
  
#根据namespace找到{和}的行
def findNameSpaceArea(clean_lines, currentlines):
    
    lines = clean_lines.elided
    startLine = 0
    endLine = 0
    startFlag = False
    leftBigParenthesis = 0
    rightBigParenthesis = 0
    
    for i in range(currentlines, len(lines)):
        leftBigParenthesis += lines[i].count('{')
        rightBigParenthesis += lines[i].count('}')
        
        if not startFlag and leftBigParenthesis > 0:
            startLine = i
            startFlag = True
        
        if rightBigParenthesis > 0 and rightBigParenthesis >= leftBigParenthesis:
            endLine = i
            break
    
    return startLine, endLine
  
def CheckCSC020013(filename, file_extension, clean_lines, rawlines, nesting_state, ruleCheckKey, Error, cpplines, fileErrorCount):
    lines = clean_lines.elided
    errMessage = "Code Style Rule: In the namespace, each member should be in a separate line."
 
    i = 0
    while i < clean_lines.NumLines():
        #将把字符串 string 中的 tab 符号转为空格，默认的空格数 tabsize 是 8.此处转换为一个空格
        str = lines[i].expandtabs(1)
        
        #跳过空行
        if common.IsBlankLine(str):
            i += 1
            continue
        
        #合并宏定义的换行
        while '\\' == str[len(str) - 1].rstrip():
            if i + 1 < len(lines):
                i += 1
                str = str[0:len(str)-1] + lines[i].expandtabs(1)
            else:
                str = str[:len(str)-1]
        
        #去除#define等宏定义 和宏开关等
        if not strcmp.Search(r'^\s*#', str):
            #查找 namespace关键字
            findNamespace = strcmp.Search(r'\bnamespace\b', str)
            findUsingNamespace = strcmp.Search(r'\busing\b\s*\bnamespace\b', str)
            
            if findNamespace and not findUsingNamespace:
                
                startLine, endLine = findNameSpaceArea(clean_lines, i)
                #namespace声明只写了一行
                #if endLine == startLine:
                    #CSC020012会报错，此处不处理
                if endLine > startLine:
                    #查找namespace的第中间行
                    j = startLine + 1
                    while j < endLine:
                        str = lines[j].expandtabs(1)
                        
                        #跳过空行
                        if common.IsBlankLine(str):
                            j += 1
                            continue
                        
                        #合并宏定义的换行
                        while '\\' == str[len(str) - 1].rstrip():
                            j += 1
                            str = str[0:len(str)-1] + lines[j].expandtabs(1)
                                
                        #去除#define 等宏定义 和注释行
                        if not strcmp.Search(r'^\s*#',str):
                            if 0 == str.count('{'):
                                if (str.count(';') > 1 or strcmp.Search(r',[^)];',str)) and not strcmp.Search(r'\bfor\b', str):
                                    Error(filename, lines, j, ruleCheckKey, 3, errMessage)
                            else:
                                tempStartLine, j = findNameSpaceArea(clean_lines, j)
                                if 0 == tempStartLine and 0 == j:
                                    j = endLine
                                    break
                            
                        j += 1
        
        i += 1
