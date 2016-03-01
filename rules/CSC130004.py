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

def CheckCSC130004(filename, file_extension, clean_lines, rawlines, nesting_state, ruleCheckKey, Error, cpplines, fileErrorCount):
  '''
    源文件结尾的注释
  /* EOF */

  Args:
    filename:文件名
    file_extension:文件的扩展名
    clean_lines:文件的内容(不包含注释)
    rawlines:原始的文件内容
    nesting_state:一个NestingState实例，维护有关嵌套块的当前堆栈信息进行解析。
    ruleCheckKey:rule的id
    Error:error的句柄
  '''
  if file_extension != "cpp":
    return

  errorMessage = 'Code Style Rule: The file should end with /* EOF */.'
  
  for i in range(len(rawlines)-2, 0, -1):
    if common.IsBlankLine(rawlines[i]):
      continue
    
    m = strcmp.Search(r'^\s*/\*\s*EOF\s*\*/*', rawlines[i])
    if not m:
      Error(filename, [], i, ruleCheckKey, 3, errorMessage)
      cpplines.append('/* EOF */')
      fileErrorCount[0] =  fileErrorCount[0] + 1
      return
    else :
      return
  