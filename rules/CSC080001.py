#!/usr/bin/python  
#-*- coding: utf-8 -*-
'''
Created on 2014-6-5
if/else分别独占一行
@author: panjl
'''
import os
import sys
syspath = os.path.dirname(os.path.dirname(__file__))
if not os.path.join(syspath, "tools") in sys.path:
    sys.path.append(os.path.join(syspath, "tools"))
import common
strcmp = common.StringCompareInfo()

def CheckCSC080001(filename, file_extension, clean_lines, rawlines, nesting_state, ruleCheckKey, Error, cpplines, fileErrorCount):
    lines = clean_lines.elided
    
    i = 0
#    specialFlag = False
    while i < clean_lines.NumLines():
        #将把字符串 string 中的 tab 符号转为空格，默认的空格数 tabsize 是 8.
        string = lines[i].expandtabs(1)
        
        #去除空行
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
        
        #去除#if/#else 的情况
        #去除"           #if/esle" 的情况,提高检查速度
        #去除#define 等宏定义
        if not strcmp.Search(r'^\s*#',string):
            #查找关键字 if/else/else if
            findFlag = False
            #查找 else if 
            # xxxx; } else if  前有任意非空字符的情况
            elseifbefore = strcmp.Search(r'\S\s*\belse\s+if\b', string)
            #else if () { xxxx; 后有任意非空字符的情况
            elseifend = strcmp.Search(r'\belse\s+if\s*\(.+\)\s*{\s*\S', string)
            if elseifbefore or elseifend:
                findFlag = True
                if 0 == errorline:
                    Error(filename, lines, i, ruleCheckKey, 3,'''Code Style Rule: Every if/else statement should start a new line: if/else should be the first word in the line.The left curly brace in a line should be the last character of the line (except for comments).In "else if ( condition ) {", the "else" and "if" should be in the same line.''')
                else:
                    Error(filename, lines, errorline, ruleCheckKey, 3,'''Code Style Rule: Every if/else statement should start a new line: if/else should be the first word in the line.The left curly brace in a line should be the last character of the line (except for comments).In "else if ( condition ) {", the "else" and "if" should be in the same line.''')
            else:
                #查找 else if，判断条件换行的情况
                #else if ( a &&
                #         b ) { xxx; //报错
                #}
                melseif = strcmp.Search(r'(\belse\s*if\b)', string)
                if melseif:
                    findFlag = True
                    leftParenthesis = 0
                    rightParenthesis = 0
                    for j in range(melseif.end(), len(string)):
                        if '(' == string[j]:
                            leftParenthesis += 1
                        elif ')' == string[j]:
                            rightParenthesis += 1
                        # else if () xxxx; 这种情况判断
                        elif 0 != leftParenthesis and leftParenthesis == rightParenthesis \
                        and (' ' != string[j] and '{' != string[j]):
                            if 0 == errorline:
                                Error(filename, lines, i, ruleCheckKey, 3,'''Code Style Rule: Every if/else statement should start a new line: if/else should be the first word in the line.The left curly brace in a line should be the last character of the line (except for comments).In "else if ( condition ) {", the "else" and "if" should be in the same line.''')
                            else:
                                Error(filename, lines, errorline, ruleCheckKey, 3,'''Code Style Rule: Every if/else statement should start a new line: if/else should be the first word in the line.The left curly brace in a line should be the last character of the line (except for comments).In "else if ( condition ) {", the "else" and "if" should be in the same line.''')
                            break
                    #继续查找下一行
                    while (0 != leftParenthesis and leftParenthesis != rightParenthesis)\
                        or (0 == leftParenthesis and 0 == rightParenthesis):
                        if i + 1 < len(lines):
                            i += 1
                            string = lines[i].expandtabs(1)
                            for j in range(len(string)):
                                if '(' == string[j]:
                                    leftParenthesis += 1
                                elif ')' == string[j]:
                                    rightParenthesis += 1
                                elif leftParenthesis == rightParenthesis and ' ' != string[j] and '{' != string[j]:
                                    if 0 == errorline:
                                        Error(filename, lines, i, ruleCheckKey, 3,'''Code Style Rule: Every if/else statement should start a new line: if/else should be the first word in the line.The left curly brace in a line should be the last character of the line (except for comments).In "else if ( condition ) {", the "else" and "if" should be in the same line.''')
                                    else:
                                        Error(filename, lines, errorline, ruleCheckKey, 3,'''Code Style Rule: Every if/else statement should start a new line: if/else should be the first word in the line.The left curly brace in a line should be the last character of the line (except for comments).In "else if ( condition ) {", the "else" and "if" should be in the same line.''')
                                    break
                        else:
                            break
            #查找 else
            if not findFlag:
                # xxx; } else  前有任意非空字符（\S）时报错
                elsebefore = strcmp.Search(r'\S\s*\belse\b', string)
                # else { xxx;  后有任意非空字符时报错
                # else xxx;    无   { 的情况
                elseend = strcmp.Search(r'(\belse\b\s*{\s*\S)|(\belse\b\s*[^\s{])', string)
                #if elsebefore or elseend:\
                if elsebefore or elseend:
                    findFlag = True
                    if 0 == errorline:
                        Error(filename, lines, i, ruleCheckKey, 3,'''Code Style Rule: Every if/else statement should start a new line: if/else should be the first word in the line.The left curly brace in a line should be the last character of the line (except for comments).In "else if ( condition ) {", the "else" and "if" should be in the same line.''')
                    else:
                        Error(filename, lines, errorline, ruleCheckKey, 3,'''Code Style Rule: Every if/else statement should start a new line: if/else should be the first word in the line.The left curly brace in a line should be the last character of the line (except for comments).In "else if ( condition ) {", the "else" and "if" should be in the same line.''')
            #查找 if
            if not findFlag:
                # if / else if
                # xxx; if  前有任意非空字符（\S）时报错
                #ifbefore = strcmp.Search(r'\S\s*\bif\s\(', string)
                ifbefore = strcmp.Search(r'\S\s*\bif\b', string)
                # if (xxxx) { 后有任意非空字符时报错
                ifend = strcmp.Search(r'\bif\s*\(.+\)\s*{\s*\S', string)
                if ifbefore or ifend:
                    if 0 == errorline:
                        Error(filename, lines, i, ruleCheckKey, 3,'''Code Style Rule: Every if/else statement should start a new line: if/else should be the first word in the line.The left curly brace in a line should be the last character of the line (except for comments).In "else if ( condition ) {", the "else" and "if" should be in the same line.''')
                    else:
                        Error(filename, lines, errorline, ruleCheckKey, 3,'''Code Style Rule: Every if/else statement should start a new line: if/else should be the first word in the line.The left curly brace in a line should be the last character of the line (except for comments).In "else if ( condition ) {", the "else" and "if" should be in the same line.''')
                else:
                    #查找到关键字 if ，判断条件换行的情况
                    #if ( a
                    #   && b ) {  xxx; // 报错
                    #}
                    #m = strcmp.Search(r'(\bif\s\()', string)  #CSC030012 中会检查
                    m = strcmp.Search(r'(\bif\b)', string)
                    if m:
                        leftParenthesis = 0
                        rightParenthesis = 0
                        for j in range(m.end(), len(string)):
                            if '(' == string[j]:
                                leftParenthesis += 1
                            elif ')' == string[j]:
                                rightParenthesis += 1
                            # if () xxxx; 这种情况判断
                            elif 0 != leftParenthesis and leftParenthesis == rightParenthesis \
                            and (' ' != string[j] and '{' != string[j]):
                                if 0 == errorline:
                                    Error(filename, lines, i, ruleCheckKey, 3,'''Code Style Rule: Every if/else statement should start a new line: if/else should be the first word in the line.The left curly brace in a line should be the last character of the line (except for comments).In "else if ( condition ) {", the "else" and "if" should be in the same line.''')
                                else:
                                    Error(filename, lines, errorline, ruleCheckKey, 3,'''Code Style Rule: Every if/else statement should start a new line: if/else should be the first word in the line.The left curly brace in a line should be the last character of the line (except for comments).In "else if ( condition ) {", the "else" and "if" should be in the same line.''')
                                break
                        #继续查找下一行
                        while (0 != leftParenthesis and leftParenthesis != rightParenthesis)\
                            or (0 == leftParenthesis and 0 == rightParenthesis):
                            if i + 1 < len(lines):
                                i += 1
                                string = lines[i].expandtabs(1)
                                for j in range(len(string)):
                                    if '(' == string[j]:
                                        leftParenthesis += 1
                                    elif ')' == string[j]:
                                        rightParenthesis += 1
                                    elif leftParenthesis == rightParenthesis and ' ' != string[j] and '{' != string[j]:
                                        if 0 == errorline:
                                            Error(filename, lines, i, ruleCheckKey, 3,'''Code Style Rule: Every if/else statement should start a new line: if/else should be the first word in the line.The left curly brace in a line should be the last character of the line (except for comments).In "else if ( condition ) {", the "else" and "if" should be in the same line.''')
                                        else:
                                            Error(filename, lines, errorline, ruleCheckKey, 3,'''Code Style Rule: Every if/else statement should start a new line: if/else should be the first word in the line.The left curly brace in a line should be the last character of the line (except for comments).In "else if ( condition ) {", the "else" and "if" should be in the same line.''')
                                        break
                            else:
                                break
        i += 1
