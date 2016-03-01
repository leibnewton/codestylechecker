#!/usr/bin/python  
#-*- coding: utf-8 -*-
'''
Created on 2014-12-10
do...while 和  while的写法：
1、do...while分别独占一行
2、while独占一行
@author: panjl
'''
import os
import sys
syspath = os.path.dirname(os.path.dirname(__file__))
if not os.path.join(syspath, "tools") in sys.path:
  sys.path.append(os.path.join(syspath, "tools"))
import common
strcmp = common.StringCompareInfo()

def CheckCSC080003(filename, file_extension, clean_lines, rawlines, nesting_state, ruleCheckKey, Error, cpplines, fileErrorCount):
    lines = clean_lines.elided
    errMessage1 = "Code Style Rule: The 'do' keyword should be in a separate line."
    errMessage2 = "Code Style Rule: The 'while' keyword should be in a separate line."
    
    i = 0
    while i < clean_lines.NumLines():
        #将把字符串 string 中的 tab 符号转为空格，默认的空格数 tabsize 是 8.此处转换为一个空格
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
            #查找关键字  do
            # do 前有任意非空字符的情况: xxxx; do
            dobefore = strcmp.Search(r'\S\s*\bdo\b', string)
            # do 后有任意非空字符的情况 : do { xxx;  or  do xxx;
            doend = strcmp.Search(r'(\bdo\b\s*{\s*\S)|(\bdo\b\s*[^\s{])', string)
            if dobefore or doend:
                if 0 == errorline:
                    Error(filename, lines, i, ruleCheckKey, 3, errMessage1)
                else:
                    Error(filename, lines, errorline, ruleCheckKey, 3, errMessage1)
            
            #查找关键字  while
            # while前有其他代码
            # xxx; while
            # xxx; } while 
            whilebefore = strcmp.Search(r'(\S\s*}\s*\bwhile\b)|([^}\s]\s*\bwhile\b)', string)
            
            # while后有其他代码
            # while (xxx);  xxx;
            # while (xxx) { xxx; 
            # while (xxx) xxx; 这种情况没有 { ，正则无法区分，但是其他规则会报错，所以此处不判断
            #whileend = strcmp.Search(r'\bwhile\b\s*\(\S*\)\s*[;{]\s*\S', string)
            whileend = strcmp.Search(r'\bwhile\b\s*\(.+\)\s*[;{]\s*\S', string)
            if whilebefore or whileend:
                if 0 == errorline:
                    Error(filename, lines, i, ruleCheckKey, 3, errMessage2)
                else:
                    Error(filename, lines, errorline, ruleCheckKey, 3, errMessage2)
            else:
                #查找到关键字 while ，判断条件换行的情况
                # while      1     || while         1
                # (xxx &&    2     || (xxx &&       2
                # )          3     || )             3
                # {/;/空             4     || {/;/空   xxx;   4
                # 不报错                               || 报错
                findWhile = strcmp.Search(r'(\bwhile\b)', string)
                if findWhile:
                    leftParenthesis = 0
                    rightParenthesis = 0
                    for j in range(findWhile.end(), len(string)):
                        if '(' == string[j]:
                            leftParenthesis += 1
                        elif ')' == string[j]:
                            rightParenthesis += 1                                
                        # while (xxx) xxx; 这种情况判断
                        elif 0 != leftParenthesis and leftParenthesis == rightParenthesis \
                         and (' ' != string[j] and '{' != string[j] and ';' != string[j]):
                            if 0 == errorline:
                                Error(filename, lines, i, ruleCheckKey, 3, errMessage2)
                            else:
                                Error(filename, lines, errorline, ruleCheckKey, 3, errMessage2)
                            break
                    
                    #继续查找下一行
                    while (0 != leftParenthesis and leftParenthesis != rightParenthesis)\
                        or (0 == leftParenthesis and 0 == rightParenthesis):
                        
                        if i + 1 < len(lines):
                            errorline = i
                            i += 1                            
                            string = lines[i].expandtabs(1)
                            #去除空行和宏开关行
                            if not common.IsBlankLine(string) and not strcmp.Search(r'^\s*#',string):
                                #合并换行
                                while '\\' == string[len(string) - 1]:
                                    if i + 1 < len(lines):
                                        i += 1
                                        string = string[:len(string) - 1] + lines[i].expandtabs(1)
                                    else:
                                        string = string[:len(string) - 1]
                                
                                for j in range(len(string)):
                                    if '(' == string[j]:
                                        leftParenthesis += 1
                                    elif ')' == string[j]:
                                        rightParenthesis += 1
                                    elif leftParenthesis == rightParenthesis\
                                     and ' ' != string[j] and '{' != string[j] and ';' != string[j]:
                                        Error(filename, lines, errorline, ruleCheckKey, 3, errMessage2)
                                        break
                        else:
                            break
        i += 1
