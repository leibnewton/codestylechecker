#!/usr/bin/python  
#-*- coding: utf-8 -*-
'''
Created on 2014-12-11
while的写法:
{和while语句写在同一行
}独占一行
do...while的写法:CSC080010
{和do语句写在同一行
}和while语句写在同一行
@author: panjl
'''
import os
import sys
syspath = os.path.dirname(os.path.dirname(__file__))
if not os.path.join(syspath, "tools") in sys.path:
  sys.path.append(os.path.join(syspath, "tools"))
import common
strcmp = common.StringCompareInfo()

def CheckRightBigParenthesis(filename, lines, currentLine, string, inLineNum, ruleCheckKey, Error, cpplines, fileErrorCount):
    errMessage = "Code Style Rule: The left curly brace '{' should be in the same line with 'while'. The right curly brace '}' should be in a separate line."
    
    leftBigParenthesis = 1
    rightBigParenthesis = 0
    #此行查找 }
    for k in range(inLineNum + 1, len(string)):
        if '{' == string[k]:
            leftBigParenthesis += 1
        elif '}' == string[k]:
            rightBigParenthesis += 1
            if leftBigParenthesis == rightBigParenthesis and strcmp.Search(r'[^\s}]', string):
                Error(filename, lines, currentLine, ruleCheckKey, 3, errMessage)
                break
    #下一行继续查找 } 
    line = currentLine
    while leftBigParenthesis != rightBigParenthesis:
        if line + 1 < len(lines):
            line += 1
            string = lines[line].expandtabs(1)
            #去除空行和宏开关行等
            if not common.IsBlankLine(string) and not strcmp.Search(r'^\s*#',string):
                for k in range(len(string)):
                    if '{' == string[k]:
                        leftBigParenthesis += 1
                    elif '}' == string[k]:
                        rightBigParenthesis += 1
                        if leftBigParenthesis == rightBigParenthesis and strcmp.Search(r'[^\s}]', string):
                            Error(filename, lines, line, ruleCheckKey, 3, errMessage)
                            break
        else:
            break

def CheckCSC080023(filename, file_extension, clean_lines, rawlines, nesting_state, ruleCheckKey, Error, cpplines, fileErrorCount):
    lines = clean_lines.elided
    errMessage = "Code Style Rule: The left curly brace '{' should be in the same line with 'while'. The right curly brace '}' should be in a separate line."
    
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
            #查找关键字  while
            # while 前不检查
            # while 后检查如下：
            # 1、while (xxx);      不报
            # 2、while (xxx) {     不报
            # 3、while (xxx) xxx;  不报
            # 4-6、while (xxx
            #            || yyy);/{/xxx;    都不报
            # 7、while (xxx)
            #          ;           不报
            # 8、while (xxx)
            #          {           报
            # 9、while (xxx)
            #          xxx;        不报
            # 找到while条件结束的右括号，判断同行是否有
            findWhile = strcmp.Search(r'(\bwhile\b)', string)
            if findWhile:
                #判断while后是所有字符，直到条件的右括号
                leftParenthesis = 0
                rightParenthesis = 0
                endFlag = False
                for j in range(findWhile.end(), len(string)):
                    if leftParenthesis == rightParenthesis and 0 != leftParenthesis:
                        if ' ' != string[j]:
                            #判断 } 是否独占一行
                            if '{' == string[j]:
                                CheckRightBigParenthesis(filename, lines, i, string, j, ruleCheckKey, Error, cpplines, fileErrorCount)
                            endFlag = True
                            break
                    else:
                        if '(' == string[j]:
                            leftParenthesis += 1
                        elif ')' == string[j]:
                            rightParenthesis += 1
                
                if not endFlag:
                    #继续查找下一行
                    line = i
                    #直到判断到条件右括号的下一位
                    while not endFlag:
                        if line + 1 < len(lines):
                            line += 1
                            string = lines[line].expandtabs(1)
                            #去除空行和宏开关行等
                            if not common.IsBlankLine(string) and not strcmp.Search(r'^\s*#',string):
                                thisLineMatchFlag = False
                                for j in range(len(string)):
                                    if leftParenthesis == rightParenthesis and 0 != leftParenthesis:
                                        if thisLineMatchFlag:
                                            #此行内条件匹配完毕
                                            if ' ' != string[j]:
                                                #判断 } 是否独占一行
                                                if '{' == string[j]:
                                                    CheckRightBigParenthesis(filename, lines, line, string, j, ruleCheckKey, Error, cpplines, fileErrorCount)
                                                endFlag = True
                                                break
                                        else:
                                            #上一行条件已经匹配完毕
                                            if ' ' != string[j]:
                                                if '{' == string[j]:
                                                    Error(filename, lines, line, ruleCheckKey, 3, errMessage)
                                                    #判断 } 是否独占一行
                                                    CheckRightBigParenthesis(filename, lines, line, string, j, ruleCheckKey, Error, cpplines, fileErrorCount)
                                                endFlag = True
                                                break
                                    else:    
                                        if '(' == string[j]:
                                            leftParenthesis += 1
                                        elif ')' == string[j]:
                                            rightParenthesis += 1
                                            if leftParenthesis ==  rightParenthesis:
                                                thisLineMatchFlag = True
                        else:
                            break
        i += 1
