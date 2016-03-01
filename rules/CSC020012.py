#!/usr/bin/python  
#-*- coding: utf-8 -*- 
'''
Created on 2014-12-29
namespace的定义，需要遵循下面的规范。[必须]
{和}各单独占一行
namespace mynamespace
{
    ...
}
@author: panjl
'''
import os
import sys
syspath = os.path.dirname(os.path.dirname(__file__))
if not os.path.join(syspath, "tools") in sys.path:
  sys.path.append(os.path.join(syspath, "tools"))
import common
strcmp = common.StringCompareInfo()
  
def CheckCSC020012(filename, file_extension, clean_lines, rawlines, nesting_state, ruleCheckKey, Error, cpplines, fileErrorCount):
    lines = clean_lines.elided
    errMessage = '''Code Style Rule: The left curly brace "{" and right curly brace "}" in a namespace definition should be both in a separate line.'''
 
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
        #去除"   #if/esle" 的情况,提高检查速度
        #去除#define 等宏定义
        if not strcmp.Search(r'^\s*#', str):
            #查找 namespace关键字
            findNamespace = strcmp.Search(r'\bnamespace\b', str)
            findUsingNamespace = strcmp.Search(r'\busing\b\s*\bnamespace\b', str)
            
            if findNamespace and not findUsingNamespace:
                leftBigParenthesis = 0
                rightBigParenthesis = 0
                endFlag = False
                
                #先在当前行查找
                for current in range(findNamespace.end(), len(str)):
                    if '{' == str[current]:
                        leftBigParenthesis += 1
                        if 1 == leftBigParenthesis:
                            Error(filename, lines, i, ruleCheckKey, 3, errMessage)
                    elif '}' == str[current]:
                        rightBigParenthesis += 1
                        if leftBigParenthesis == leftBigParenthesis:
                            #此行已经报错了，所以此处不报了
                            #Error(filename, lines, i, ruleCheckKey, 3, errMessage)
                            endFlag = True
                            break
                
                if endFlag:
                    i += 1
                    break
                
                #从i+1行开始再做一个循环查找
                j = i + 1
                while j < clean_lines.NumLines():
                    #将把字符串 string 中的 tab 符号转为空格，默认的空格数 tabsize 是 8.此处转换为一个空格
                    strSub = lines[j].expandtabs(1)
                    
                    #跳过空行和宏定义行
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
                    
                    #跳过空行和宏定义行
                    if strcmp.Search(r'^\s*#', str):
                        j += 1
                        continue
                    
                    if 0 == leftBigParenthesis:
                        leftBigParenthesis += strSub.count('{')
                        rightBigParenthesis += strSub.count('}')
                        if leftBigParenthesis > 0:
                            if strcmp.Search(r'[^{\s]', strSub):
                                Error(filename, lines, j, ruleCheckKey, 3, errMessage)
                            if rightBigParenthesis >= leftBigParenthesis:
                                #该行还找到了匹配的},但是此行已经报错了，所以此处不报了
                                #if strcmp.Search(r'[^}\s]', strSub):
                                    #Error(filename, lines, i, ruleCheckKey, 3, errMessage)
                                break
                    else:
                        leftBigParenthesis += strSub.count('{')
                        rightBigParenthesis += strSub.count('}')
                        if rightBigParenthesis >= leftBigParenthesis:
                            if strcmp.Search(r'[^}\s]', strSub):
                                Error(filename, lines, j, ruleCheckKey, 3, errMessage)
                            break
                    
                    j += 1
        
        i += 1
