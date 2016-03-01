#!/usr/bin/python  
#-*- coding: utf-8 -*- 
'''
Created on 2014-12-16
enum声明及其枚举值必须有注释说明。[必须]
/// 月的枚举定义
enum Month
{
    JAN = 1,       ///<  1月
    FEB,           ///<  2月
    ...
    DEC            ///< 12月
};
@author: panjl
'''
import os
import sys
syspath = os.path.dirname(os.path.dirname(__file__))
if not os.path.join(syspath, "tools") in sys.path:
  sys.path.append(os.path.join(syspath, "tools"))
import common
strcmp = common.StringCompareInfo()
   
# enum 之后发现以下符号，说明不是声明
OVERLIST= frozenset([';', ',', ')', '.'])
   
#返回enum结束;的行和列(返回精确位置的函数可以参照CSC140006中注释掉的部分)
def findStructEndLinesAndColumn(rawlines, currentlines, startColumn):
    
    lines = rawlines
    
    leftBigParenthesis = 0
    rightBigParenthesis = 0
    
    for i in range(currentlines, len(lines)):
        leftBigParenthesis += lines[i].count('{')
        rightBigParenthesis += lines[i].count('}')
        if rightBigParenthesis >= leftBigParenthesis:
            return i
    
    return 0
    
def CheckCSC140005(filename, file_extension, clean_lines, rawlines, nesting_state, ruleCheckKey, Error, cpplines, fileErrorCount):
    #只check .c 和 .cpp文件
    if "c" != file_extension and "cpp" != file_extension:
        return
    
    lines = rawlines
    errMessage = "Code Style Rule: Comments should be used to describe the enum and each enum member."
    #记录上一行是否为注释行
    previousNoteFlag = False
    i = 0
    
    while i < len(rawlines):
        #将把字符串 string 中的 tab 符号转为空格，默认的空格数 tabsize 是 8.此处转换为一个空格
        str = lines[i].expandtabs(1)
        
        #跳过空行
        if common.IsBlankLine(str):
            i += 1
            continue
        
        #合并宏定义的换行
        while '\\' == str[len(str)-1].rstrip():
            if i + 1 < len(lines):
                i += 1
                str = str[0:len(str)-1] + lines[i].expandtabs(1)
            else:
                str = str[:len(str)-1]
        
        #去除#define 等宏定义
        if strcmp.Search(r'^\s*#',str):
            previousNoteFlag = False
            i += 1
            continue
        
        #单行注释写在开头的情况         /// 注释     ///< 注释      // 注释
        if strcmp.Search(r'^\s*//', str):
            previousNoteFlag = True
            i += 1
            continue
        
        #多行注释合并         /** 注释 */   /**< 注释 */   /* 注释 */
        findNote = strcmp.Search(r'^\s*/\*', str)
        if findNote:
            previousNoteFlag = True
            #不考虑一行中间有注释情况，其他规则会报错
            if not strcmp.Search(r'\*/', str[findNote.end():]):
                while i < len(rawlines):
                    i += 1
                    str = lines[i].expandtabs(1)
                    if strcmp.Search(r'\*/', str):
                        break
            
            i += 1
            continue
        
        #查找 enum关键字
        findEnum = strcmp.Search(r'\benum\b', str)
        
        if findEnum:
            if strcmp.Search(r'//', str[:findEnum.start()]) or str[:findEnum.start()].count('"')%2 == 1:
                previousNoteFlag = False
                i += 1
                continue
            
            #是enum的使用，不是声明
            enumUserFlag = False
            
            #查找enum的{位置
            startLine = i
            startColumn = 0
            enumBracesFlag = False
            
            #查找enum行
            for startColumn in xrange(findEnum.end(), len(str)):
                #定义enum变量的情况
                if str[startColumn] in OVERLIST:
                    enumUserFlag = True
                    enumBracesFlag = True
                    break
                elif '{' == str[startColumn]:
                    startColumn += findEnum.start()
                    enumBracesFlag = True
                    break
            
            if not enumBracesFlag:
                for startLine in xrange(i+1, len(lines)):
                    str = lines[startLine].expandtabs(1)
                    
                    for startColumn in xrange(len(str)):
                        if str[startColumn] in OVERLIST:
                            enumUserFlag = True
                            enumBracesFlag = True
                            break
                        elif '{' == str[startColumn]:
                            enumBracesFlag = True
                            break
                    
                    if enumBracesFlag:
                        break
            
            if enumUserFlag:
                i += 1
                continue
            
            #enum声明只写了一行时，已经报错了
            errorFlag = False
            
            #1、向上查找，判断enum是否有注释(6种注释都可以)
            if not previousNoteFlag:
                Error(filename, lines, i, ruleCheckKey, 3, errMessage)
                errorFlag = True
            
            #2、向下查找，判断enum的成员是否有注释
            #根据enum开始{ 的行和列，查找到enum结束;的行和列
            endLine = findStructEndLinesAndColumn(rawlines, startLine, startColumn+1)
            #enum声明只写了一行
            if endLine == startLine:
                #{}找不到注释就报错
                if not errorFlag and strcmp.Search(r'(//)|(/\*)', str[startColumn+1:]):
                    Error(filename, lines, startLine, ruleCheckKey, 3, errMessage)
            
            #enum声明写了多行
            elif endLine > startLine:
                if startLine > i:
                    str = lines[startLine].expandtabs(1)
                
                #查找 { 所在行
                if strcmp.Search(r',', str[startColumn+1:]):
                    # { 之后就定义了变量，则判断之后是否有注释
                    if not strcmp.Search(r'(//)|(/\*)', str[startColumn+1:]):
                        Error(filename, lines, startLine, ruleCheckKey, 3, errMessage)
                else:
                    findEmbed = strcmp.Search(r'{', str[startColumn+1:])
                    if findEmbed:
                        startLine = findStructEndLinesAndColumn(rawlines, startLine, findEmbed.end()+startColumn+1)
                
                #查找 enum的第中间行
                previousNoteFlag = False
                j = startLine + 1
                while j <= endLine:
                    str = lines[j].expandtabs(1)
                    
                    #跳过空行
                    if common.IsBlankLine(str):
                        j += 1
                        continue
                    
                    #合并宏定义的换行
                    while '\\' == str[len(str) - 1].rstrip():
                        j += 1
                        str = str[0:len(str)-1] + lines[j].expandtabs(1)
                    
                    #去除#define 等宏定义
                    if strcmp.Search(r'^\s*#',str):
                        previousNoteFlag = False
                        j += 1
                        continue
                    
                    #单行注释写在开头的情况         /// 注释     ///< 注释      // 注释
                    if strcmp.Search(r'^\s*//', str):
                        previousNoteFlag = True
                        j += 1
                        continue
                    
                    #多行注释合并         /** 注释 */   /**< 注释 */   /* 注释 */
                    findNote = strcmp.Search(r'^\s*/\*', str)
                    if findNote:
                        previousNoteFlag = True
                        #不考虑一行中间有注释情况，其他规则会报错
                        if not strcmp.Search(r'^\s*\*/', str[findNote.end():]):
                            while j < endLine:
                                j += 1
                                str = lines[i].expandtabs(1)
                                if strcmp.Search(r'\*/', str):
                                    break
                        
                        j += 1
                        continue
                    
                    if j == endLine:
                        if strcmp.Search(r'\S+\s*}', str) and not previousNoteFlag and not strcmp.Search(r'(//)|(/\*)', str):
                            Error(filename, lines, j, ruleCheckKey, 3, errMessage)
                    else:
                        if not previousNoteFlag and not strcmp.Search(r'(//)|(/\*)', str):
                            Error(filename, lines, j, ruleCheckKey, 3, errMessage)
                    
                    previousNoteFlag = False
                    j += 1
        else:
            previousNoteFlag = False
        
        i += 1
