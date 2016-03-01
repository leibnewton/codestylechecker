#!/usr/bin/python  
#-*- coding: utf-8 -*-
'''
Created on 2014-12-12
赋值语句中如果出现较长的运算符表达式，需要进行换行时，按照下面规则换行:
以运算符为起点进行换行。[必须]
新行可以采用下面两种缩进方式。[必须]
    1、新行跟=后第一个操作数对齐
    2、新行缩进4个空格
@author: panjl
'''
import os
import sys
syspath = os.path.dirname(os.path.dirname(__file__))
if not os.path.join(syspath, "tools") in sys.path:
    sys.path.append(os.path.join(syspath, "tools"))
import common
strcmp = common.StringCompareInfo()

# 赋值表达式中可以使用并且可以再之前换行的运算符
OPERATORSLIST= frozenset([
    '/', '*', '%', '+', '-',
    '>', '<','=', '!',
    '&', '^', '|'
    ])

def CheckCSC020008(filename, file_extension, clean_lines, rawlines, nesting_state, ruleCheckKey, Error, cpplines, fileErrorCount):
    lines = clean_lines.elided
    errMessage = "Code Style Rule: If an assignment expression is too long, it should be wrapped before an operator, and the new line should: 1.indent four spaces or 2.align with the first operand after '='."
    
    i = 0
    while i <  clean_lines.NumLines():
        #此规则不能转换tab为空格
        str = lines[i]
        
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
        if not strcmp.Search(r'(^\s*#)|(\btemplate\b)', str):
            # 查找赋值运算符：= （包括：/=、+=、<<=、>>=、&= 等等）
            #去除 !=、==、<=、>=     [^!=><]=[^=]
            #找到 >>= <<=            (>>=)|(<<=)
            #=在行首的情况                             (^=[^=])       本身代码设计就有问题不处理
            findAssign = strcmp.Search(r'([^!=><]=[^=])|(>>=)|(<<=)', str)
            # =运算符重载
            findExcept = strcmp.Search(r'\boperator\b\s*=', str)
            # = 在行尾
            #findEnd = strcmp.Search(r'=\s*$', str)
            if findAssign and not findExcept and not strcmp.Search(r'[!=><]=', str):
                #记录 = 后的第一为空字符的列数
                columnsNum = 0
                findAssignFlag = False
                endFlag = False
                lastChar = ''
                
                #当前行检查
                for j in range(findAssign.start(), len(str)):
                    if findAssignFlag:
                        # 同一行不能写多条语句，其他规则会报错
                        if ';' == str[j] or ',' == str[j] or '{' == str[j] or '}' == str[j] or ':' == str[j]:
                            endFlag = True
                            break;
                        if ' ' != str[j]:
                            lastChar = str[j] 
                            if 0 == columnsNum:
                                columnsNum = j
                    else:  
                        if '=' == str[j]:
                            lastChar = str[j]
                            findAssignFlag = True
                
                if not endFlag:
                    findFirst = strcmp.Search(r'\S',str)
                    # 缩进为4空格时
                    defaultBlank = findFirst.start() + 4
                    
                    while not endFlag:
                        if i + 1 < len(lines):
                            i += 1                            
                            str = lines[i]
                            #去除空行和宏开关行等
                            if not common.IsBlankLine(str) and not strcmp.Search(r'^\s*#',str):
                                #合并换行
                                countLines = 0
                                while '\\' == str[len(str) - 1]:
                                    if i + 1 < len(lines):
                                        countLines += 1
                                        i += 1
                                        str = str[:len(str) - 1] + lines[i]
                                    else:
                                        str = str[:len(str) - 1]
                                
                                #记录当前列数
                                count = 0
                                firstCharFlag = True
                                for j in range(len(str)):
                                    if ';' == str[j] or ',' == str[j] or '{' == str[j] or '}' == str[j] or ':' == str[j]:
                                        endFlag = True
                                        break;
                                    elif ' ' == str[j]:
                                        count += 1
                                    elif str[j] in OPERATORSLIST or '=' == lastChar:
                                        if firstCharFlag:
                                            #  4空格缩进
                                            if count == defaultBlank:
                                                columnsNum = defaultBlank
                                            # 跟=后第一个操作数对齐
                                            elif count == columnsNum and 0 != count:
                                                defaultBlank = columnsNum
                                            else:
                                                Error(filename, lines, i-countLines, ruleCheckKey, 3, errMessage)
                                                endFlag = True
                                                break
                                            
                                            firstCharFlag = False
                                    else:
                                        if firstCharFlag:
                                            if lastChar in OPERATORSLIST:
                                                Error(filename, lines, i-countLines, ruleCheckKey, 3, errMessage)
                                            endFlag = True
                                            break
                        else:
                            break
        
        i += 1
