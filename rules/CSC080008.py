#!/usr/bin/python  
#-*- coding: utf-8 -*-
'''
Created on 2014-6-6
‘{’和if/else写在同一行，‘}’独占一行
@author: panjl
'''
import os
import sys
syspath = os.path.dirname(os.path.dirname(__file__))
if not os.path.join(syspath, "tools") in sys.path:
    sys.path.append(os.path.join(syspath, "tools"))
import common
strcmp = common.StringCompareInfo()

def CheckCSC080008(filename, file_extension, clean_lines, rawlines, nesting_state, ruleCheckKey, Error, cpplines, fileErrorCount):
    lines = clean_lines.elided
    
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
        removalSpecial = strcmp.Search(r'^\s*#',str)
        if not removalSpecial:
            #查找关键字 if/else/else if
            findFlag = False
            #以下  6 种情况
            #else if () {          不报错
            #else if () xxx;       不报错
            #else if () { xxx;     不报错
            #esle if ()            不报错
            #  xxx;
            #else if ()            报错
            #{
            #else if ()            报错
            #{ xxx;
            melseif = strcmp.Search(r'(\belse\s*if\b)', str)
#            多行查找可以查找换行符
#            melseif2 = strcmp.Search(r'\belse\s*\n*\s*\bif\b', lines[i]+lines[i+1])
            if melseif:
                findFlag = True
                matchFlag = False
                nextLineFlag = True
                leftParenthesis = 0
                rightParenthesis = 0
                for j in range(melseif.end(), len(str)):
                    if '(' == str[j]:
                        leftParenthesis += 1
                    elif ')' == str[j]:
                        rightParenthesis += 1
                        if leftParenthesis == rightParenthesis:
                            matchFlag = True
                            str = str[j+1:]
                            if strcmp.Search(r'^\s*\S', str):
                                nextLineFlag = False
                                #查找到else if ()后面有任意非空字符(如下三中情况)，不需要在查找下一行
                                #else if () {
                                #else if () xxx;
                                #else if () { xxx;
                                
                                #如果else if () 后面有 { ，则查找到与else if () { 相对应的 }，判读    } 是否单独为一行
                                m = strcmp.Search(r'^\s*{', str)
                                if m:
                                    leftBigParenthesis = 1
                                    rightBigParenthesis = 0
                                    #先循环本行
                                    for k in range(m.end(), len(str)):
                                        if '{' == str[k]:
                                            leftBigParenthesis += 1
                                        elif '}' == str[k]:
                                            rightBigParenthesis += 1
                                            #同一行找到匹配的    } ，报错
                                            if leftBigParenthesis ==  rightBigParenthesis:
                                                Error(filename, lines, i, ruleCheckKey, 3,'''Code Style Rule: The left curly brace "{"'" should be in the same line with if/else, and the right curly brace "}" should be in a single line.''')
                                                break
                                    #如果上面没有匹配结束，就继续向下查找直到匹配结束
                                    n = i    
                                    while leftBigParenthesis !=  rightBigParenthesis:
                                        if n + 1 < len(lines):
                                            n += 1
                                            string = lines[n].expandtabs(1)
                                            for k in range(len(string)):
                                                if '{' == string[k]:
                                                    leftBigParenthesis += 1
                                                elif '}' == string[k]:
                                                    rightBigParenthesis += 1
                                                    if leftBigParenthesis ==  rightBigParenthesis:
                                                        #判断 } 是否为单独一行
                                                        #只有 }; 的情况由CSC080017报错
                                                        if strcmp.Search(r'[^\s};]', string):
                                                            Error(filename, lines, n, ruleCheckKey, 3,'''Code Style Rule: The left curly brace "{"'" should be in the same line with if/else, and the right curly brace "}" should be in a single line.''')
                                                        break
                                        else:
                                            break
                            break
                    #防止testMacroDefine2中一直遍历到文件结尾
                    elif 0 == leftParenthesis and ' ' != str[j] and '{' != str[j]:
                        nextLineFlag = False
                        break
                #继续查找下一行
                while nextLineFlag:
                    if i + 1 < len(lines):
                        i += 1
                        str = lines[i].expandtabs(1)
                        #空行的场合
                        if common.IsBlankLine(str):
                            continue
                        for j in range(len(str)):
                            if not matchFlag:
                                if '(' == str[j]:
                                    leftParenthesis += 1
                                elif ')' == str[j]:
                                    rightParenthesis += 1
                                    if leftParenthesis == rightParenthesis:
                                        matchFlag = True
                                        str = str[j+1:]
                                        if strcmp.Search(r'^\s*\S', str):
                                            nextLineFlag = False
                                            #查找到else if ()后面有任意非空字符(如下三中情况)，不需要在查找下一行
                                            #else if ( a 
                                            #        && b ) {
                                            #else if ( a
                                            #        && b ) xxx;
                                            #else if ( a
                                            #        && b ) { xxx;
                                            #如果else if () 后面有 { ，则查找到与else if () { 相对应的 }，判读    } 是否单独为一行
                                            m = strcmp.Search(r'^\s*{', str)
                                            if m:
                                                leftBigParenthesis = 1
                                                rightBigParenthesis = 0
                                                #先循环本行
                                                for k in range(m.end(), len(str)):
                                                    if '{' == str[k]:
                                                        leftBigParenthesis += 1
                                                    elif '}' == str[k]:
                                                        rightBigParenthesis += 1
                                                        #同一行找到匹配的    } ，报错
                                                        if leftBigParenthesis ==  rightBigParenthesis:
                                                            Error(filename, lines, i, ruleCheckKey, 3,'''Code Style Rule: The left curly brace "{"'" should be in the same line with if/else, and the right curly brace "}" should be in a single line.''')
                                                            break
                                                #如果上面没有匹配结束，就继续向下查找直到匹配结束
                                                n = i    
                                                while leftBigParenthesis !=  rightBigParenthesis:
                                                    n += 1
                                                    string = lines[n].expandtabs(1)
                                                    for k in range(len(string)):
                                                        if '{' == string[k]:
                                                            leftBigParenthesis += 1
                                                        elif '}' == string[k]:
                                                            rightBigParenthesis += 1
                                                            if leftBigParenthesis ==  rightBigParenthesis:
                                                                #判断 } 是否为单独一行
                                                                #只有 }; 的情况由CSC080017报错
                                                                if strcmp.Search(r'[^\s};]', string):
                                                                    Error(filename, lines, n, ruleCheckKey, 3,'''Code Style Rule: The left curly brace "{"'" should be in the same line with if/else, and the right curly brace "}" should be in a single line.''')
                                                                break
                                        break
                            else:
                                #else if ()            不报错
                                #  xxx;
                                #else if ()            报错
                                #{
                                #else if ()            报错
                                #{ xxx;
                                
                                #找到  { 的场合报错
                                m = strcmp.Search(r'^\s*{', str)
                                if m:
                                    Error(filename, lines, i, ruleCheckKey, 3,'''Code Style Rule: The left curly brace "{"'" should be in the same line with if/else, and the right curly brace "}" should be in a single line.''')
                                    #查找与此行   { 匹配的    } ，判断   } 是否单独占一行
                                    leftBigParenthesis = 1
                                    rightBigParenthesis = 0
                                    #先循环本行
                                    for k in range(m.end(), len(str)):
                                        if '{' == str[k]:
                                            leftBigParenthesis += 1
                                        elif '}' == str[k]:
                                            rightBigParenthesis += 1
                                            #同一行找到匹配的    } ，报错
                                            if leftBigParenthesis ==  rightBigParenthesis:
                                                Error(filename, lines, i, ruleCheckKey, 3,'''Code Style Rule: The left curly brace "{"'" should be in the same line with if/else, and the right curly brace "}" should be in a single line.''')
                                                break
                                    #如果上面没有匹配结束，就继续向下查找直到匹配结束
                                    n = i    
                                    while leftBigParenthesis !=  rightBigParenthesis:
                                        n += 1
                                        string = lines[n].expandtabs(1)
                                        for k in range(len(string)):
                                            if '{' == string[k]:
                                                leftBigParenthesis += 1
                                            elif '}' == string[k]:
                                                rightBigParenthesis += 1
                                                if leftBigParenthesis ==  rightBigParenthesis:
                                                    #判断 } 是否为单独一行
                                                    #只有 }; 的情况由CSC080017报错
                                                    if strcmp.Search(r'[^\s};]', string):
                                                        Error(filename, lines, n, ruleCheckKey, 3,'''Code Style Rule: The left curly brace "{"'" should be in the same line with if/else, and the right curly brace "}" should be in a single line.''')
                                                    break
                                nextLineFlag = False
                                break
                    else:
                        break
            #查找 else
            #以下  6 种情况
            #else {          不报错
            #else xxx;       不报错
            #else { xxx;     不报错
            #esle            不报错
            #  xxx;
            #else            报错
            #{
            #else            报错
            #{ xxx;
            if not findFlag:
                melse = strcmp.Search(r'(\belse\b)', lines[i])
                if melse:
                    findFlag = True
                    #查找以下三种情况
                    #else {          不报错
                    #else xxx;       不报错
                    #else { xxx;     不报错
                    if strcmp.Search(r'\belse\b\s*\S', str):
                        #对else后有   { 的情况，判读对应    } 的位置
                        m = strcmp.Search(r'\belse\b\s*{', str)
                        if m:
                            leftBigParenthesis = 1
                            rightBigParenthesis = 0
                            #先循环本行
                            for k in range(m.end(), len(str)):
                                if '{' == str[k]:
                                    leftBigParenthesis += 1
                                elif '}' == str[k]:
                                    rightBigParenthesis += 1
                                    #同一行找到匹配的    } ，报错
                                    if leftBigParenthesis ==  rightBigParenthesis:
                                        Error(filename, lines, i, ruleCheckKey, 3,'''Code Style Rule: The left curly brace "{"'" should be in the same line with if/else, and the right curly brace "}" should be in a single line.''')
                                        break
                            #如果上面没有匹配结束，就继续向下查找直到匹配结束
                            n = i    
                            while leftBigParenthesis !=  rightBigParenthesis:
                                if n + 1 < len(lines):
                                    n += 1
                                    string = lines[n].expandtabs(1)
                                    for k in range(len(string)):
                                        if '{' == string[k]:
                                            leftBigParenthesis += 1
                                        elif '}' == string[k]:
                                            rightBigParenthesis += 1
                                            if leftBigParenthesis ==  rightBigParenthesis:
                                                #判断 } 是否为单独一行
                                                #只有 }; 的情况由CSC080017报错
                                                if strcmp.Search(r'[^\s};]', string):
                                                    Error(filename, lines, n, ruleCheckKey, 3,'''Code Style Rule: The left curly brace "{"'" should be in the same line with if/else, and the right curly brace "}" should be in a single line.''')
                                                break
                                else:
                                    break
                    #esle            不报错
                    #  xxx;
                    #else            报错
                    #{
                    #else            报错
                    #{ xxx;
                    
                    #注意下面这种情况，此处判断下一行时为 if 所以不会报错
                    # else 
                    # if {    为了下次查找 该行 所以 i 要 减回来
                    else:
                        #找到下一不为空的行
                        while True:
                            i += 1
                            str = lines[i].expandtabs(1)
                            if common.IsBlankLine(str):
                                continue
                            else:
                                break
                        #开头不是 { 的场合，有可能是  if ，是if时使用continue，后面i++不执行，继续检查该行
                        if strcmp.Search(r'^\s*\bif\b', str):
                            continue
                        #开头找到  { 的场合报错
                        m = strcmp.Search(r'^\s*{', str)
                        if m:
                            Error(filename, lines, i, ruleCheckKey, 3,'''Code Style Rule: The left curly brace "{"'" should be in the same line with if/else, and the right curly brace "}" should be in a single line.''')
                            #查找与此行   { 匹配的    } ，判断   } 是否单独占一行
                            leftBigParenthesis = 1
                            rightBigParenthesis = 0
                            #先循环本行
                            for k in range(m.end(), len(str)):
                                if '{' == str[k]:
                                    leftBigParenthesis += 1
                                elif '}' == str[k]:
                                    rightBigParenthesis += 1
                                    #同一行找到匹配的    } ，报错
                                    if leftBigParenthesis ==  rightBigParenthesis:
                                        Error(filename, lines, i, ruleCheckKey, 3,'''Code Style Rule: The left curly brace "{"'" should be in the same line with if/else, and the right curly brace "}" should be in a single line.''')
                                        break
                            #如果上面没有匹配结束，就继续向下查找直到匹配结束
                            n = i    
                            while leftBigParenthesis !=  rightBigParenthesis:
                                if  + 1 < len(lines):
                                    n += 1
                                    string = lines[n].expandtabs(1)
                                    for k in range(len(string)):
                                        if '{' == string[k]:
                                            leftBigParenthesis += 1
                                        elif '}' == string[k]:
                                            rightBigParenthesis += 1
                                            if leftBigParenthesis ==  rightBigParenthesis:
                                                #判断 } 是否为单独一行
                                                #只有 }; 的情况由CSC080017报错
                                                if strcmp.Search(r'[^\s};]', string):
                                                    Error(filename, lines, n, ruleCheckKey, 3,'''Code Style Rule: The left curly brace "{"'" should be in the same line with if/else, and the right curly brace "}" should be in a single line.''')
                                                break
                                else:
                                    break
                            #else 没有{ 的情况就不需要处理了 
            #查找 if()  与  else if () 处理非常类似
            if not findFlag:
                #以下  6 种情况
                #if () {          不报错
                #if () xxx;       不报错
                #if () { xxx;     不报错
                #if ()            不报错
                #  xxx;
                #if ()            报错
                #{
                #if ()            报错
                #{ xxx;
                mif = strcmp.Search(r'(\bif\b)', str)
                if mif:
                    findFlag = True
                    matchFlag = False
                    nextLineFlag = True
                    leftParenthesis = 0
                    rightParenthesis = 0
                    for j in range(mif.end(), len(str)):
                        if '(' == str[j]:
                            leftParenthesis += 1
                        elif ')' == str[j]:
                            rightParenthesis += 1
                            if leftParenthesis == rightParenthesis:
                                matchFlag = True
                                str = str[j+1:]
                                if strcmp.Search(r'^\s*\S', str):
                                    nextLineFlag = False
                                    #查找到if ()后面有任意非空字符(如下三中情况)，不需要在查找下一行
                                    #if () {
                                    #if () xxx;
                                    #if () { xxx;
                                    
                                    #如果if () 后面有 { ，则查找到与if () { 相对应的 }，判读    } 是否单独为一行
                                    m = strcmp.Search(r'^\s*{', str)
                                    if m:
                                        leftBigParenthesis = 1
                                        rightBigParenthesis = 0
                                        #先循环本行
                                        for k in range(m.end(), len(str)):
                                            if '{' == str[k]:
                                                leftBigParenthesis += 1
                                            elif '}' == str[k]:
                                                rightBigParenthesis += 1
                                                #同一行找到匹配的    } ，报错
                                                if leftBigParenthesis ==  rightBigParenthesis:
                                                    Error(filename, lines, i, ruleCheckKey, 3,'''Code Style Rule: The left curly brace "{"'" should be in the same line with if/else, and the right curly brace "}" should be in a single line.''')
                                                    break
                                        #如果上面没有匹配结束，就继续向下查找直到匹配结束
                                        n = i    
                                        while leftBigParenthesis !=  rightBigParenthesis:
                                            if n + 1 < len(lines):
                                                n += 1
                                                string = lines[n].expandtabs(1)
                                                for k in range(len(string)):
                                                    if '{' == string[k]:
                                                        leftBigParenthesis += 1
                                                    elif '}' == string[k]:
                                                        rightBigParenthesis += 1
                                                        if leftBigParenthesis ==  rightBigParenthesis:
                                                            #判断 } 是否为单独一行
                                                            #只有 }; 的情况由CSC080017报错
                                                            if strcmp.Search(r'[^\s};]', string):
                                                                Error(filename, lines, n, ruleCheckKey, 3,'''Code Style Rule: The left curly brace "{"'" should be in the same line with if/else, and the right curly brace "}" should be in a single line.''')
                                                            break
                                            else:
                                                break
                                break
                    #继续查找下一行
                    while nextLineFlag:
                        if i + 1 < len(lines):
                            i += 1
                            str = lines[i].expandtabs(1)
                            #空行的场合
                            if common.IsBlankLine(str):
                                continue
                            for j in range(len(str)):
                                if not matchFlag:
                                    if '(' == str[j]:
                                        leftParenthesis += 1
                                    elif ')' == str[j]:
                                        rightParenthesis += 1
                                        if leftParenthesis == rightParenthesis:
                                            matchFlag = True
                                            str = str[j+1:]
                                            if strcmp.Search(r'^\s*\S', str):
                                                nextLineFlag = False
                                                #查找到if ()后面有任意非空字符(如下三中情况)，不需要在查找下一行
                                                #if () {
                                                #if () xxx;
                                                #if () { xxx;
                                                
                                                #如果if () 后面有 { ，则查找到与if () { 相对应的 }，判读    } 是否单独为一行
                                                m = strcmp.Search(r'^\s*{', str)
                                                if m:
                                                    leftBigParenthesis = 1
                                                    rightBigParenthesis = 0
                                                    #先循环本行
                                                    for k in range(m.end(), len(str)):
                                                        if '{' == str[k]:
                                                            leftBigParenthesis += 1
                                                        elif '}' == str[k]:
                                                            rightBigParenthesis += 1
                                                            #同一行找到匹配的    } ，报错
                                                            if leftBigParenthesis ==  rightBigParenthesis:
                                                                Error(filename, lines, i, ruleCheckKey, 3,'''Code Style Rule: The left curly brace "{"'" should be in the same line with if/else, and the right curly brace "}" should be in a single line.''')
                                                                break
                                                    #如果上面没有匹配结束，就继续向下查找直到匹配结束
                                                    n = i    
                                                    while leftBigParenthesis !=  rightBigParenthesis:
                                                        n += 1
                                                        string = lines[n].expandtabs(1)
                                                        for k in range(len(string)):
                                                            if '{' == string[k]:
                                                                leftBigParenthesis += 1
                                                            elif '}' == string[k]:
                                                                rightBigParenthesis += 1
                                                                if leftBigParenthesis ==  rightBigParenthesis:
                                                                    #判断 } 是否为单独一行
                                                                    #只有 }; 的情况由CSC080017报错
                                                                    if strcmp.Search(r'[^\s};]', string):
                                                                        Error(filename, lines, n, ruleCheckKey, 3,'''Code Style Rule: The left curly brace "{"'" should be in the same line with if/else, and the right curly brace "}" should be in a single line.''')
                                                                    break
                                            break
                                    #防止testMacroDefine2中一直遍历到文件结尾
                                    elif 0 == leftParenthesis and ' ' != str[j] and '{' != str[j]:
                                        nextLineFlag = False
                                        break    
                                else:
                                    #if ()            不报错
                                    #  xxx;
                                    #if ()            报错
                                    #{
                                    #if ()            报错
                                    #{ xxx;
                                    
                                    #找到  { 的场合报错
                                    m = strcmp.Search(r'^\s*{', str)
                                    if m:
                                        Error(filename, lines, i, ruleCheckKey, 3,'''Code Style Rule: The left curly brace "{"'" should be in the same line with if/else, and the right curly brace "}" should be in a single line.''')
                                        #查找与此行   { 匹配的    } ，判断   } 是否单独占一行
                                        leftBigParenthesis = 1
                                        rightBigParenthesis = 0
                                        #先循环本行
                                        for k in range(m.end(), len(str)):
                                            if '{' == str[k]:
                                                leftBigParenthesis += 1
                                            elif '}' == str[k]:
                                                rightBigParenthesis += 1
                                                #同一行找到匹配的    } ，报错
                                                if leftBigParenthesis ==  rightBigParenthesis:
                                                    Error(filename, lines, i, ruleCheckKey, 3,'''Code Style Rule: The left curly brace "{"'" should be in the same line with if/else, and the right curly brace "}" should be in a single line.''')
                                                    break
                                        #如果上面没有匹配结束，就继续向下查找直到匹配结束
                                        n = i    
                                        while leftBigParenthesis !=  rightBigParenthesis:
                                            n += 1
                                            string = lines[n].expandtabs(1)
                                            for k in range(len(string)):
                                                if '{' == string[k]:
                                                    leftBigParenthesis += 1
                                                elif '}' == string[k]:
                                                    rightBigParenthesis += 1
                                                    if leftBigParenthesis ==  rightBigParenthesis:
                                                        #判断 } 是否为单独一行
                                                        #只有 }; 的情况由CSC080017报错
                                                        if strcmp.Search(r'[^\s};]', string):
                                                            Error(filename, lines, n, ruleCheckKey, 3,'''Code Style Rule: The left curly brace "{"'" should be in the same line with if/else, and the right curly brace "}" should be in a single line.''')
                                                        break
                                    nextLineFlag = False
                                    break
                        else:
                            break
        i += 1