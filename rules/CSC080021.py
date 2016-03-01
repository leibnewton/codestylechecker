#!/usr/bin/python  
#-*- coding: utf-8 -*- 
'''
Created on 2014-12-8
for必须有{}
{和for语句写在同一行           其他规则check
{前留一个空格                             其他规则check  ')'和‘{’之间有空格
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
  
def CheckCSC080021(filename, file_extension, clean_lines, rawlines, nesting_state, ruleCheckKey, Error, cpplines, fileErrorCount):
    lines = clean_lines.elided
    errMessage1 = "Code Style Rule: Statements in 'for' should be enclosed in braces: for (;;) { statements; }."
    errMessage2 = "Code Style Rule: The right curly brace '}' of the 'for' statement should be in a separate line."
 
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
        
        #去除#if/#else 的情况
        #去除"           #if/esle" 的情况,提高检查速度
        #去除#define 等宏定义
        if not strcmp.Search(r'^\s*#', str):
            #查找 for 关键字
            #for前可能还有其他代码
            #for后可能直接换行，（）写到下一行
            findfor = strcmp.Search(r'\bfor\b', str)
            
            if findfor:
                # findFlag   0 初始值:()条件匹配
                #            1 ()条件匹配结束
                #            2 {}匹配中
                #            3 结束
                findFlag = 0
                leftParenthesis = 0
                rightParenthesis = 0
                leftBigParenthesis = 0
                rightBigParenthesis = 0
                
                #先在当前行查找
                for current in range(findfor.end(), len(str)):
                    if 0 == findFlag:
                        #取得匹配小括号的右括号
                        if '(' == str[current]:
                            leftParenthesis += 1
                        elif ')' == str[current]:
                            rightParenthesis += 1
                            if leftParenthesis == rightParenthesis:
                                findFlag = 1
                    elif 1 == findFlag:
                        if '{' == str[current]:
                            leftBigParenthesis += 1
                            findFlag = 2
                        elif ' ' != str[current]:
                            if strcmp.Search(r'\)', str[:current]):
                                Error(filename, lines, i, ruleCheckKey, 3, errMessage1)
                            else:
                                Error(filename, lines, i-1, ruleCheckKey, 3, errMessage1)
                            findFlag = 3
                            break
                    elif 2 == findFlag:
                        if '{' == str[current]:
                            leftBigParenthesis += 1
                        elif '}' == str[current]:
                            rightBigParenthesis += 1
                            Error(filename, lines, i, ruleCheckKey, 3, errMessage2)
                            findFlag = 3
                            break
                
                if 3 == findFlag:
                    i += 1
                    continue
                
                #从i+1行开始再做一个循环查找
                j = i + 1
                while j < clean_lines.NumLines():
                    #将把字符串 string 中的 tab 符号转为空格，默认的空格数 tabsize 是 8.此处转换为一个空格
                    strSub = lines[j].expandtabs(1)
                    
                    #跳过空行
                    if common.IsBlankLine(strSub):
                        j += 1
                        continue
                    
                    #合并宏定义的换行
                    while '\\' == strSub[len(strSub) - 1].rstrip():
                        if j + 1 < len(lines):
                            j += 1
                            strSub = strSub[0:len(strSub)-1] + lines[j].expandtabs(1)
                        else:
                            strSub = strSub[:len(strSub)-1]
                    
                    #跳过宏定义行
                    if strcmp.Search(r'^\s*#', strSub):
                        j += 1
                        continue
                    
                    for line in xrange(len(strSub)):
                        if 0 == findFlag:
                            #取得匹配小括号的右括号
                            if '(' == strSub[line]:
                                leftParenthesis += 1
                            elif ')' == strSub[line]:
                                rightParenthesis += 1
                                if leftParenthesis == rightParenthesis:
                                    findFlag = 1
                        elif 1 == findFlag:
                            if '{' == strSub[line]:
                                leftBigParenthesis += 1
                                findFlag = 2
                            elif ' ' != strSub[line]:
                                if strcmp.Search(r'\)', strSub[:line]):
                                    Error(filename, lines, j, ruleCheckKey, 3, errMessage1)
                                else:
                                    Error(filename, lines, j-1, ruleCheckKey, 3, errMessage1)
                                findFlag = 3
                                break
                        elif 2 == findFlag:
                            if '{' == strSub[line]:
                                leftBigParenthesis += 1
                            elif '}' == strSub[line]:
                                rightBigParenthesis += 1
                                if leftBigParenthesis == rightBigParenthesis:
                                    if strcmp.Search(r'[^} ]', strSub):
                                        Error(filename, lines, j, ruleCheckKey, 3, errMessage2)
                                    findFlag = 3
                                    break
                    
                    if 3 == findFlag:
                        break
                    
                    j += 1
        
        i += 1
