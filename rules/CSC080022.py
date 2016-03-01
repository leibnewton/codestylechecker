#!/usr/bin/python  
#-*- coding: utf-8 -*-
'''
Created on 2014-12-10
do..while必须有{}(CSC080022)
while必须有{}
@author: panjl
'''
import os
import sys
syspath = os.path.dirname(os.path.dirname(__file__))
if not os.path.join(syspath, "tools") in sys.path:
  sys.path.append(os.path.join(syspath, "tools"))
import common
strcmp = common.StringCompareInfo()

def CheckCSC080022(filename, file_extension, clean_lines, rawlines, nesting_state, ruleCheckKey, Error, cpplines, fileErrorCount):
    lines = clean_lines.elided
    errMessage = "Code Style Rule: Statements in while should be enclosed in braces: while (condition) { statements; }."
    
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
            #查找关键字  while
            # while 前不检查
            
            # while 后检查（一行情况）
            # 1、while (xxx);  xxx; 不报错
            # 2、while (xxx) { xxx; 不报错
            # 3、while (xxx) xxx;   报错
            
            # while 后检查（多行情况）
            # while      1     || while         1
            # (x &&      2     || (x &&         2
            # y)         3     || y)            3
            # {/;        4     ||  xxx;         4
            # 4、不报错                      || 5、报错
            findWhile = strcmp.Search(r'(\bwhile\b)', string)
            if findWhile:
                leftParenthesis = 0
                rightParenthesis = 0
                for j in range(findWhile.end(), len(string)):
                    if '(' == string[j]:
                        leftParenthesis += 1
                    elif ')' == string[j]:
                        rightParenthesis += 1
                    # 情况 4 
                    elif 0 != leftParenthesis and leftParenthesis == rightParenthesis:
                        if ' ' == string[j]:
                            continue
                        elif '{' != string[j] and ';' != string[j]:
                            if 0 == errorline:
                                Error(filename, lines, i, ruleCheckKey, 3, errMessage)
                            else:
                                Error(filename, lines, errorline, ruleCheckKey, 3, errMessage)
                        break
                
                #记录下while的行
                errorline = i
                
                #继续查找下一行(多行情况判断)
                while (0 != leftParenthesis and leftParenthesis != rightParenthesis)\
                   or (0 == leftParenthesis and 0 == rightParenthesis):
                    
                    if i + 1 < len(lines):
                        i += 1                            
                        string = lines[i].expandtabs(1)
                        #去除空行和宏开关行等
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
                                elif 0 != leftParenthesis and leftParenthesis == rightParenthesis:
                                    if ' ' == string[j]:
                                        continue
                                    elif '{' != string[j] and ';' != string[j]:
                                        Error(filename, lines, errorline, ruleCheckKey, 3, errMessage)
                                    break
                    else:
                        break
        
        i += 1
