#!/usr/bin/python  
#-*- coding: utf-8 -*-
'''
Created on 2014-12-11
do...while的写法:
{和do语句写在同一行
}和while语句写在同一行
while的写法:CSC080023
{和while语句写在同一行
}独占一行
@author: panjl
'''
import os
import sys
syspath = os.path.dirname(os.path.dirname(__file__))
if not os.path.join(syspath, "tools") in sys.path:
  sys.path.append(os.path.join(syspath, "tools"))
import common
strcmp = common.StringCompareInfo()

def CheckCSC080010(filename, file_extension, clean_lines, rawlines, nesting_state, ruleCheckKey, Error, cpplines, fileErrorCount):
    lines = clean_lines.elided
    errMessage = '''Code Style Rule: The left curly brace "{" should be in the same line with "do" keyword, and the right curly brace "}" should be in the same line with "while" keyword.'''
    
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
            #查找关键字  do
            # 1、do xxx;         不报               对应 while 不用判断
            # 2、do { xxx;       不报
            # 3、do
            #    xxx;            不报               对应 while 不用判断
            # 4、do
            #    { xxx;          报
            #while情况
            # 1、xxx; } while () 不报
            # 2、xxx; }
            #    while ()        报
            # 3、xxx;
            #    while ()        不报       无{}通过 do排除
            # 4、 xxx; while ()   不报       无{}通过 do排除
            findDo = strcmp.Search(r'(\bdo\b)', string)
            if findDo:
                #判断do后是否有字符
                #do后有字符 1 或 2 
                if strcmp.Search(r'\bdo\b\s*\S', string):
                    #do后有{ 2 
                    findDoAfter = strcmp.Search(r'(\bdo\b\s*{)', string)
                    if findDoAfter:
                        #对do后有   { 的情况，判读对应    } 的位置
                        leftBigParenthesis = 1
                        rightBigParenthesis = 0
                        #先循环本行
                        for j in range(findDoAfter.end(), len(string)):
                            if '{' == string[j]:
                                leftBigParenthesis += 1
                            elif '}' == string[j]:
                                rightBigParenthesis += 1
                                if leftBigParenthesis ==  rightBigParenthesis:
                                    #判断   } 是否与 while在同一行
                                    if not strcmp.Search(r'^\s*\bwhile\b', string[j+1:len(string)]):
                                        Error(filename, lines, i+1, ruleCheckKey, 3, errMessage)
                                        break
                        
                        #如果上面没有匹配结束，就继续向下查找直到匹配结束
                        line = i
                        while leftBigParenthesis !=  rightBigParenthesis:
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
                                            if leftBigParenthesis ==  rightBigParenthesis:
                                                #判断   } 是否与 while在同一行
                                                if not strcmp.Search(r'^\s*\bwhile\b', string[k+1:len(string)]):
                                                    Error(filename, lines, line+1, ruleCheckKey, 3, errMessage)
                                                    break
                            else:
                                break
                # do 后无字符  3 或  4 
                else:
                    #找到下一不为空的行
                    while i + 1 < len(lines):
                        i += 1
                        string = lines[i].expandtabs(1)
                        if common.IsBlankLine(string) and not strcmp.Search(r'^\s*#',string):
                            continue
                        else:
                            break
                    
                    #开头找到  { 的场合报错
                    findLeftBraces = strcmp.Search(r'^\s*{', string)
                    if findLeftBraces:
                        Error(filename, lines, i, ruleCheckKey, 3, errMessage)
                        #查找与此行   { 匹配的    } ，判断   } 是否与 while在同一行
                        leftBigParenthesis = 1
                        rightBigParenthesis = 0
                        #先循环本行
                        for j in range(findLeftBraces.end(), len(string)):
                            if '{' == string[j]:
                                leftBigParenthesis += 1
                            elif '}' == string[j]:
                                rightBigParenthesis += 1
                                if leftBigParenthesis ==  rightBigParenthesis:
                                    #判断   } 是否与 while在同一行
                                    if not strcmp.Search(r'^\s*\bwhile\b', string[j+1:len(string)]):
                                        Error(filename, lines, i+1, ruleCheckKey, 3, errMessage)
                                        break
                        #如果上面没有匹配结束，就继续向下查找直到匹配结束
                        line = i
                        while leftBigParenthesis !=  rightBigParenthesis:
                            if line + 1 < len(lines):
                                line += 1
                                string = lines[line].expandtabs(1)
                                if not common.IsBlankLine(string) and not strcmp.Search(r'^\s*#',string):
                                    for k in range(len(string)):
                                        if '{' == string[k]:
                                            leftBigParenthesis += 1
                                        elif '}' == string[k]:
                                            rightBigParenthesis += 1
                                            if leftBigParenthesis ==  rightBigParenthesis:
                                                #判断   } 是否与 while在同一行
                                                if not strcmp.Search(r'^\s*\bwhile\b', string[k+1:len(string)]):
                                                    Error(filename, lines, line+1, ruleCheckKey, 3, errMessage)
                                                    break
                            else:
                                break
        i += 1
