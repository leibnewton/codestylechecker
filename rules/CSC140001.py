#!/usr/bin/python  
#-*- coding: utf-8 -*-
'''
Created on 2014-12-15

@author: zhangran
'''
import os
import sys
syspath = os.path.dirname(os.path.dirname(__file__))
if not os.path.join(syspath, "tools") in sys.path:
  sys.path.append(os.path.join(syspath, "tools"))
import common
strcmp = common.StringCompareInfo()

def checkNotBlankLine(rawlines, startLineNo, endLineNo):
  '''检查文件说明

  Args:
    rawlines:原始的文件内容
    startLineNo:起始行
    endLineNo:结束行
  Returns:
    boolean: TRUE:有非空的代码行
    integer: 错误所在的行
  '''
  for i in xrange(startLineNo, endLineNo):
    if common.IsBlankLine(rawlines[i]):
      continue
    else :
      return True, i

  return False, startLineNo

def checkCopyright(rawlines, keyLineNo):
  '''检查版权信息

  Args:
    rawlines:原始的文件内容
    keyLineNo:关键字的所在行
  Returns:
    integer: 版权信息起始行 
    integer: 版权信息结束行.
  '''
  startLineNo = -1
  endLineNo = -1
  
  # 从关键字向上查找
  for i in xrange(keyLineNo - 1, 0, -1):
    if common.IsBlankLine(rawlines[i]):
      continue
  
    if rawlines[i].strip() == '/**':
      startLineNo = i
      break
      
  # 从关键字向下查找
  for i in xrange(keyLineNo + 1, len(rawlines)):
    if common.IsBlankLine(rawlines[i]):
      continue
  
    #结束
    if rawlines[i].strip() == '*/':
      endLineNo = i
      break
    
  return startLineNo, endLineNo

def checkFileDiscription(rawlines, keyLineNo):
  '''检查文件说明

  Args:
    rawlines:原始的文件内容
    keyLineNo:关键字的所在行
  Returns:
    integer: 文件说明起始行 
    integer: 文件说明信息结束行.
  '''
  startLineNo = -1
  endLineNo = -1
  briefTagFlg = False
  
  # 从关键字向上查找
  for i in xrange(keyLineNo - 1, 1, -1):
    if common.IsBlankLine(rawlines[i]):
      continue
  
    if rawlines[i].strip() == '/**':
      startLineNo = i
      break
      
  # 从关键字向下查找
  for i in xrange(keyLineNo + 1, len(rawlines)):
    if common.IsBlankLine(rawlines[i]):
      continue
  
    #结束
    if rawlines[i].strip() == '*/':
      endLineNo = i
      break
    elif -1 != rawlines[i].find('@brief'):
      briefTagFlg = True
  
  #文件说明的格式必须正确
  if not briefTagFlg:
    startLineNo = -1
    endLineNo = -1
    
  return startLineNo, endLineNo

def checkFileProtectedMacro(rawlines, keyLineNo, headerGuardName):
  '''检查头文件保护宏

  Args:
    rawlines:原始的文件内容
    keyLineNo:关键字的所在行
  Returns:
    integer: 头文件保护宏起始行 
    integer: 头文件保护宏结束行.
  '''
  startLineNo = -1
  endLineNo = -1
  
  conditionalCompilationCount = 0
  pairEndifCount = 0
  for i in xrange(keyLineNo,len(rawlines)):
    if common.IsBlankLine(rawlines[i]):
      i += 1
      continue
  
    if strcmp.Search(r'#ifndef\s+%s' % headerGuardName , rawlines[i]):
      startLineNo = i
    
    if startLineNo > 0:
      conditionalCompilationCount = conditionalCompilationCount + rawlines[i].count('#ifndef ')
      conditionalCompilationCount = conditionalCompilationCount + rawlines[i].count('#ifdef ')
      conditionalCompilationCount = conditionalCompilationCount + rawlines[i].count('#if ')
    
      pairEndifCount = pairEndifCount + rawlines[i].count('#endif')
    
    if conditionalCompilationCount == pairEndifCount and pairEndifCount > 0:
      endLineNo = i
      break

  #不相等，错误
  if pairEndifCount != conditionalCompilationCount:
    endLineNo = -1
    
  return startLineNo, endLineNo

def checkCplusplusDiscription(rawlines, keyLineNo):
  '''检查C++头文件声明（如果是C++头文件时）

  Args:
    rawlines:原始的文件内容
    keyLineNo:关键字的所在行
  Returns:
    integer: C++头文件声明起始行 
    integer: C++头文件声明结束行.
  '''
  startLineNo = -1
  endLineNo = -1
  
   # 从关键字向上查找
  for i in xrange(1, keyLineNo):
    if common.IsBlankLine(rawlines[i]):
      continue
  
    if -1 != rawlines[i].strip().find('#ifndef __cplusplus'):
      startLineNo = i
      
    elif -1 != rawlines[i].strip().find('#endif'):
      if startLineNo > 0:
        endLineNo = i
        break
     
  return startLineNo, endLineNo


def CheckCSC140001(filename, file_extension, clean_lines, rawlines, nesting_state, ruleCheckKey, Error, cpplines, fileErrorCount):
  '''头文件开始的注释
     版权信息
    文件说明
    头文件保护宏
    C++头文件声明（如果是C++头文件时）

  Args:
    filename:文件名
    file_extension:文件的扩展名
    clean_lines:文件的内容(不包含注释)
    rawlines:原始的文件内容
    nesting_state:一个NestingState实例，维护有关嵌套块的当前堆栈信息进行解析。
    ruleCheckKey:rule的id
    Error:error的句柄
  '''
    
  # 无文件说明
  errorMessage1 = 'Code Style Rule: There should be \"File Description\" in the header file.'
  # 无C++头文件声明（如果是C++头文件时）
  errorMessage2 = 'Code Style Rule: There should be "__cplusplus" macro in the header file (only for C++ header file).'
  # 这四项内容的顺序不正确
  errorMessage3 = 'Code Style Rule: Each header file should start with: 1.Copyright 2.File description 3.Include guard 4.__cplusplus macro (only for C++ header file) according to the above sequence.'
  # 各项之间有代码或注释
  errorMessage4 = 'Code Style Rule: Each header file should start with: 1.Copyright 2.File description 3.Include guard 4.__cplusplus macro (only for C++ header file). There should be no code or comment between each element listed above.'
  # 头文件结尾不是 EOF
  errorMessage5 ='Code Style Rule: The file should end with \"/* EOF */\". There should be no code between the end of the "include guard" and the \"/* EOF */\".'
  
  if file_extension != "h":
    return
  
  #从下往上查找文件的结尾
  for i in xrange(len(rawlines) - 2 , 1, -1):
    if common.IsBlankLine(rawlines[i]):
      continue
    
    m = strcmp.Search(r'^\s*/\*\s*EOF\s*\*/*', rawlines[i])
    if m:
      if not strcmp.Search(r'^\s*#endif', rawlines[i - 1]):
        Error(filename, [], i, ruleCheckKey, 3, errorMessage5)
        
      break
    else :
      Error(filename, [], i, ruleCheckKey, 3, errorMessage5)
      
      break
  
  #按照路径将文件名和路径分割开
  dirName, fileNameWithoutPath = os.path.split(filename)
  headerGuardName = fileNameWithoutPath.replace('.','_').upper()

  copyrightStartLineNo = 0
  copyrightEndLineNo = 0
  fileDiscriptionStartLineNo = 0
  fileDiscriptionEndLineNo = 0
  fileProtectedMacroStartLineNo = 0
  fileProtectedMacroEndLineNo = 0
  cplusplusDiscriptionStartLineNo = 0
  cplusplusDiscriptionEndLineNo = 0
  
  copyrightKeyLineNo = 0
  fileDiscriptionKeyLineNo = 0
  fileProtectedMacroKeyLineNo = 0
  cplusplusDiscriptionKeyLineNo = 0

  i = 0
  while i < clean_lines.NumLines():
    
    # 判断版权信息
    if strcmp.Search(r'\*\s+Copyright\s+@', rawlines[i]):
      copyrightStartLineNo, copyrightEndLineNo = checkCopyright(rawlines, i)
      if copyrightStartLineNo > 0 and copyrightEndLineNo > 0:
        copyrightKeyLineNo = i
      
    # 判断文件说明
    elif -1 != rawlines[i].find('@file'):
      fileDiscriptionStartLineNo, fileDiscriptionEndLineNo = checkFileDiscription(rawlines, i)
      if fileDiscriptionStartLineNo > 0 and fileDiscriptionEndLineNo > 0:
        fileDiscriptionKeyLineNo = i
      
    # 判断头文件保护宏
    elif strcmp.Search(r'#ifndef\s+%s' % headerGuardName , rawlines[i]):
      fileProtectedMacroStartLineNo, fileProtectedMacroEndLineNo = checkFileProtectedMacro(rawlines, i, headerGuardName)
      if fileProtectedMacroStartLineNo > 0 and fileProtectedMacroEndLineNo > 0:
        fileProtectedMacroKeyLineNo = i
    
    # 判断C++头文件声明
    elif strcmp.Search(r'^(\s*)\bclass[\s*:{;]', rawlines[i]):
      cplusplusDiscriptionStartLineNo, cplusplusDiscriptionEndLineNo = checkCplusplusDiscription(rawlines, i)
      if cplusplusDiscriptionStartLineNo > 0:
        cplusplusDiscriptionKeyLineNo = cplusplusDiscriptionStartLineNo
      else :
        # CC++头文件,但是没有找到对应的声明
        cplusplusDiscriptionKeyLineNo = -1
        
    i += 1

  # 无文件说明
  if fileDiscriptionKeyLineNo <= 0:
    Error(filename, [], 1, ruleCheckKey, 3, errorMessage1)

  # 无C++头文件声明（如果是C++头文件时）
  if cplusplusDiscriptionKeyLineNo == -1:
    Error(filename, [], 1, ruleCheckKey, 3, errorMessage2)
  
  # 各项之间有代码或注释
  if copyrightKeyLineNo > 0 and fileDiscriptionKeyLineNo > 0 and copyrightKeyLineNo < fileDiscriptionKeyLineNo:
    ret, lineNo = checkNotBlankLine(rawlines, copyrightEndLineNo + 1, fileDiscriptionStartLineNo);
    if ret:
      Error(filename, [], lineNo, ruleCheckKey, 3, errorMessage4)
  
  # 各项之间有代码或注释
  if fileDiscriptionKeyLineNo > 0 and fileProtectedMacroKeyLineNo > 0 and  fileDiscriptionKeyLineNo < fileProtectedMacroKeyLineNo:
    ret, lineNo = checkNotBlankLine(rawlines, fileDiscriptionEndLineNo + 1, fileProtectedMacroStartLineNo);
    if ret:
      Error(filename, [], lineNo, ruleCheckKey, 3, errorMessage4)      

  # 这四项内容的顺序不正确
  if fileDiscriptionKeyLineNo > 0 and fileProtectedMacroKeyLineNo > 0:
    if ( (copyrightKeyLineNo <= 0)or
         (copyrightKeyLineNo > fileDiscriptionKeyLineNo) or
         (fileDiscriptionKeyLineNo > fileProtectedMacroKeyLineNo) or
         (cplusplusDiscriptionKeyLineNo > 0 and fileProtectedMacroKeyLineNo > cplusplusDiscriptionKeyLineNo) ) :
      Error(filename, [], fileDiscriptionStartLineNo, ruleCheckKey, 3, errorMessage3)
    
    