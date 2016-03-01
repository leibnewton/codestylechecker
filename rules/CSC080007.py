#!/usr/bin/python  
#-*- coding: utf-8 -*-
'''
Created on 2014-6-6
if/else/else if 必须有{}
@author: panjl
'''
import os
import sys
syspath = os.path.dirname(os.path.dirname(__file__))
if not os.path.join(syspath, "tools") in sys.path:
    sys.path.append(os.path.join(syspath, "tools"))
import common
strcmp = common.StringCompareInfo()

def CheckCSC080007(filename, file_extension, clean_lines, rawlines, nesting_state, ruleCheckKey, Error, cpplines, fileErrorCount):
    lines = clean_lines.elided
    
    i = 0
    while i < clean_lines.NumLines():
        #将把字符串 string 中的 tab 符号转为空格，默认的空格数 tabsize 是 8.
        string = lines[i].expandtabs(1)
        
        #跳过空行
        if common.IsBlankLine(lines[i]):
            i += 1
            continue
        
        #合并带换行符的行
        while '\\' == string[len(string) - 1].rstrip():
            if i + 1 < len(lines):
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
            #查找 else if () xxx; 的情况
            melseif = strcmp.Search(r'(\belse\s*if\b)', string)
            if melseif:
                findFlag = True
                loopFlag = True
                matchFlag = False
                leftParenthesis = 0
                rightParenthesis = 0
                for j in range(melseif.end(), len(string)):
                    if not matchFlag:
                        if '(' == string[j]:
                            leftParenthesis += 1
                        elif ')' == string[j]:
                            rightParenthesis += 1
                            if leftParenthesis == rightParenthesis:
                                matchFlag = True
                    else:
                        #空格的场合
                        if ' ' == string[j]:
                            continue
                        elif '{' == string[j]:
                            loopFlag = False
                            break
                        else:
                            Error(filename, lines, i, ruleCheckKey, 3,"Code Style Rule: Statements in if/else should be enclosed in braces: if (condition) { statements; }.")
                            loopFlag = False
                            break
                #继续查找下一行
                #else if ( a &&
                #         b ) xxx; //报错
                #或
                #else if ()
                # xxx;    //报错
                errorline = i
                while (not matchFlag) or loopFlag:
                    if i + 1 < len(lines):
                        i += 1
                        string = lines[i].expandtabs(1)
                        if not strcmp.Search(r'^\s*#', string):
                            for j in range(len(string)):
                                if not matchFlag:
                                    if '(' == string[j]:
                                        leftParenthesis += 1
                                    elif ')' == string[j]:
                                        rightParenthesis += 1
                                        if leftParenthesis == rightParenthesis:
                                            matchFlag = True
                                            errorline = i
                                else:
                                    #空格或换行符的场合
                                    if ' ' == string[j]:
                                        continue
                                    elif '{' == string[j]:
                                        loopFlag = False
                                        break
                                    else:
                                        loopFlag = False
                                        Error(filename, lines, errorline, ruleCheckKey, 3,"Code Style Rule: Statements in if/else should be enclosed in braces: if (condition) { statements; }.")
                                        break
                    else:
                        break
            #查找 else
            if not findFlag:
                # else xxx; // 报错
                #或
                #else
                #   xxx;    // 报错
#                melse = strcmp.Search(r'belse\b', string)
#                if melse:
                
                # 查找 else xxx; 这种情况    
                elseend = strcmp.Search(r'\belse\b\s*[^\s{]', string)
                # 直接查找 换行的情况
#                elseend2 = strcmp.Search(r'\belse\b\s*.*\s*[^\s{]'.string)
                if elseend:
                    findFlag = True
                    Error(filename, lines, i, ruleCheckKey, 3,"Code Style Rule: Statements in if/else should be enclosed in braces: if (condition) { statements; }.")
                else:
                    #查找多行的情况
                    #else
                    #   xxx;
                    melse = strcmp.Search(r'(\belse\b)', string)
                    if melse:
                        #1、去除 else {  xxx; 这种情况
                        #2、去除 else {
                        #          xxx;      这种情况
                        #3、去除 else 
                        #       {  xxx;      这种情况等
                        findFlag = True
                        loopFlag = True
                        for j in range(melse.end(), len(string)):
                            #空格或换行符的场合
                            if ' ' == string[j]:
                                continue
                            elif '{' == string[j]:
                                loopFlag = False
                                break
                            else:
                                loopFlag = False
                                Error(filename, lines, i, ruleCheckKey, 3,"Code Style Rule: Statements in if/else should be enclosed in braces: if (condition) { statements; }.")
                                break
                        #没找到满足的情况，继续判断下一行
                        errorline = i
                        while loopFlag:
                            if i + 1 < len(lines):
                                i += 1
                                string = lines[i].expandtabs(1)
                                if not strcmp.Search(r'^\s*#', string):
                                    for j in range(len(string)):
                                        #空格或换行符的场合
                                        if ' ' == string[j]:
                                            continue
                                        elif '{' == string[j]:
                                            loopFlag = False
                                            break
                                        else:
                                            #去除下面这种情况
                                            # else 
                                            # if { 
                                            loopFlag = False
                                            if not strcmp.Search(r'^\s*\bif\b', string):
                                                Error(filename, lines, errorline, ruleCheckKey, 3,"Code Style Rule: Statements in if/else should be enclosed in braces: if (condition) { statements; }.")
                                            else:
                                                #为了下次从  if { 行开始循环
                                                i -= 1
                                            break
                            else:
                                break
            #查找 if
            if not findFlag:
                #查找 if () xxx; 的情况
                mif = strcmp.Search(r'(\bif\b)', string)
                if mif:
                    loopFlag = True
                    matchFlag = False
                    leftParenthesis = 0
                    rightParenthesis = 0
                    for j in range(mif.end(), len(string)):
                        if not matchFlag:
                            if '(' == string[j]:
                                leftParenthesis += 1
                            elif ')' == string[j]:
                                rightParenthesis += 1
                                if leftParenthesis == rightParenthesis:
                                    matchFlag = True
                            #防止testMacroDefine1一直循环到文件结尾而异常
                            #当 /**/ 共通问下修改后此处处理可以删除
                            elif 0 == leftParenthesis and ' ' != string[j] and '{' != string[j]:
                                matchFlag = True
                                loopFlag = False
                                break
                        else:
                            #空格或换行符的场合
                            if ' ' == string[j]:
                                continue
                            elif '{' == string[j]:
                                loopFlag = False
                                break
                            else:
                                loopFlag = False
                                Error(filename, lines, i, ruleCheckKey, 3,"Code Style Rule: Statements in if/else should be enclosed in braces: if (condition) { statements; }.")
                                break
                    #继续查找下一行
                    #if ( a &&
                    #         b ) xxx; //报错
                    #或
                    #if ()
                    # xxx;    //报错
                    errorline = i
                    while (not matchFlag) or loopFlag:
                        if i + 1 < len(lines):
                            i += 1
                            string = lines[i].expandtabs(1)
                            if not strcmp.Search(r'^\s*#', string):
                                for j in range(len(string)):
                                    if not matchFlag:
                                        if '(' == string[j]:
                                            leftParenthesis += 1
                                        elif ')' == string[j]:
                                            rightParenthesis += 1
                                            if leftParenthesis == rightParenthesis:
                                                matchFlag = True
                                                errorline = i

                                    else:
                                        #空格或换行符的场合
                                        if ' ' == string[j]:
                                            continue
                                        elif '{' == string[j]:
                                            loopFlag = False
                                            break
                                        else:
                                            loopFlag = False
                                            Error(filename, lines, errorline, ruleCheckKey, 3,"Code Style Rule: Statements in if/else should be enclosed in braces: if (condition) { statements; }.")
                                            break
                        else:
                            break
        i += 1