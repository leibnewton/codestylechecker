#!/usr/bin/python  
#-*- coding: utf-8 -*- 
'''
Created on 2014-12-15
struct声明及其成员必须有注释说明。[必须]
/// MyStruct概要说明
struct MyStruct
{
    char*     name;    ///< 变量name的说明
    int32_t   length;  ///< 变量length的说明
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
    
# struct 之后发现以下符号，说明不是声明
OVERLIST= frozenset([';', ',', ')', '.', '=', '/'])

#返回struct结束;的行和列
def findStructEndLinesAndColumn(rawlines, currentlines, startColumn, string):
    lines = rawlines
    
    endLine = currentlines
    leftBigParenthesis = 1
    rightBigParenthesis = 0
    
    #当前行从Struct开始列 { 开始查找
    for i in range(startColumn, len(string)):
        if '{' == string[i]:
            leftBigParenthesis += 1
        elif '}' == string[i]:
            rightBigParenthesis += 1
            if leftBigParenthesis == rightBigParenthesis:
                return endLine, i
    
    #继续查找 } 
    while endLine + 1 < len(lines):
        endLine += 1
            
        #将把字符串 string 中的 tab 符号转为空格，默认的空格数 tabsize 是 8.此处转换为一个空格
        string = lines[endLine].expandtabs(1)
            
        #去除空行、宏开关行、单行注释行等
        if not common.IsBlankLine(string) \
        and not strcmp.Search(r'^\s*#',string) \
        and not strcmp.Search(r'^\s*//', string):
            for i in range(len(string)):
                if '{' == string[i]:
                    leftBigParenthesis += 1
                elif '}' == string[i]:
                    rightBigParenthesis += 1
                    if leftBigParenthesis == rightBigParenthesis:
                        return endLine, i
    
    return 0, 0
    
def CheckCSC140006(filename, file_extension, clean_lines, rawlines, nesting_state, ruleCheckKey, Error, cpplines, fileErrorCount):
    #只check .c 和 .cpp文件
    if "c" != file_extension and "cpp" != file_extension:
        return
    
    lines = rawlines
    errMessage = "Code Style Rule: Comments should be used to describe the struct and each struct member."
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
        
        #查找 struct关键字
        findStruct = strcmp.Search(r'\bstruct\b', str)
        
        if findStruct:
            if strcmp.Search(r'//', str[:findStruct.start()]) or str[:findStruct.start()].count('"')%2 == 1:
                previousNoteFlag = False
                i += 1
                continue
            
            #是struct的使用，不是声明
            structUserFlag = False
            
            #查找struct的{位置
            startLine = i
            startColumn = 0
            structBracesFlag = False
            
            #查找struct行
            for startColumn in xrange(findStruct.end(), len(str)):
                #定义struct变量 和 以 struct为参数的情况
                if str[startColumn] in OVERLIST:
                    structUserFlag = True
                    structBracesFlag = True
                    break
                elif '{' == str[startColumn]:
                    startColumn += findStruct.start()
                    structBracesFlag = True
                    break
            
            if not structBracesFlag:
                for startLine in xrange(i+1, len(lines)):
                    str = lines[startLine].expandtabs(1)
                    
                    for startColumn in xrange(len(str)):
                        if str[startColumn] in OVERLIST:
                            structUserFlag = True
                            structBracesFlag = True
                            break
                        elif '{' == str[startColumn]:
                            structBracesFlag = True
                            break
                    
                    if structBracesFlag:
                        break
            
            if structUserFlag:
                i += 1
                continue
            
            #struct声明只写了一行时，已经报错了
            errorFlag = False
            
            #1、确定是结构体声明时，向上查找，判断struct是否有注释(6种注释都可以)
            if not previousNoteFlag:
                Error(filename, lines, i, ruleCheckKey, 3, errMessage)
                errorFlag = True
            
            #2、向下查找，判断struct的成员变量，是否有注释
            #根据struct开始{ 的行和列，查找到struct结束;的行和列
            endLine, endColumn = findStructEndLinesAndColumn(rawlines, startLine, startColumn+1, str)
            if 0 == endLine and 0 == endColumn:
                break
            
            #struct声明只写了一行
            if endLine == startLine:
                #在struct的{和}之间查找是否有成员
                if not errorFlag and strcmp.Search(r';', str[startColumn+1:endColumn]) \
                and not strcmp.Search(r'(//\s*\S+)|(/\*\s*\S+)', str[startColumn+1:endColumn]):
                    Error(filename, lines, startLine, ruleCheckKey, 3, errMessage)
            
            #struct声明写了多行
            elif endLine > startLine:
                if startLine > i:
                    str = lines[startLine].expandtabs(1)
                
                #查找 嵌套的   { 所在行
                findEmbed = strcmp.Search(r'{', str[startColumn+1:])
                if findEmbed:
                    startLine, nestingEndColumn = findStructEndLinesAndColumn(rawlines, startLine, findEmbed.end()+startColumn+1, str)
                    if 0 == startLine and 0 == nestingEndColumn:
                        break
                elif strcmp.Search(r';', str[startColumn+1:]) \
                and not previousNoteFlag \
                and not strcmp.Search(r'(//\s*\S+)|(/\*\s*\S+)', str[startColumn+1:]):
                    Error(filename, lines, startLine, ruleCheckKey, 3, errMessage)
                
                #查找 struct的第中间行
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
                                str = lines[j].expandtabs(1)
                                if strcmp.Search(r'\*/', str):
                                    break
                        
                        j += 1
                        continue
                    
                    findEmbed = strcmp.Search(r'{', str)
                    if findEmbed:
                        j, nestingEndColumn = findStructEndLinesAndColumn(rawlines, j, findEmbed.end(), str)
                        if 0 == j and 0 == nestingEndColumn:
                            break
                    else:
                        if j == endLine:
                            # };    or  xxx; };
                            # }aa;  or  xxx; }aa;
                            #在struct的{和}之间查找是否有成员
                            if strcmp.Search(r';', str[:endColumn]) \
                            and not strcmp.Search(r'(//\s*\S+)|(/\*\s*\S+)', str[:endColumn]):
                                Error(filename, lines, j, ruleCheckKey, 3, errMessage)
                        elif strcmp.Search(r';', str) \
                        and not previousNoteFlag \
                        and not strcmp.Search(r'(//)|(/\*)', str):
                            Error(filename, lines, j, ruleCheckKey, 3, errMessage)
                    
                    previousNoteFlag = False
                    j += 1
        else:
            previousNoteFlag = False
        
        i += 1
