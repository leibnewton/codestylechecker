#!/usr/bin/python  
#-*- coding: utf-8 -*-
'''
Created on 2014-6-5
Rule: Usage of functions strcpy, sprintf, strcat is forbidden. Please use strncpy, snprintf, strncat instead.
@author: zhangran
'''
import os
import sys
syspath = os.path.dirname(os.path.dirname(__file__))
if not os.path.join(syspath, "tools") in sys.path:
  sys.path.append(os.path.join(syspath, "tools"))
import common
strcmp = common.StringCompareInfo()

def CheckCSC110006(filename, file_extension, clean_lines, rawlines, nesting_state, ruleCheckKey, Error, cpplines, fileErrorCount):
  lines = clean_lines.elided
  errMessage = "Code Style Rule: Usage of functions strcpy, sprintf, strcat is forbidden. Please use strncpy, snprintf, strncat instead."
  
  i = 0
  endLineNo = clean_lines.NumLines()
  while i < clean_lines.NumLines():
    #空白行--skip
    if common.IsBlankLine(lines[i]):
      i += 1
      continue
    #宏定义--skip
    if strcmp.Search(r'^\s*#\s*define\s+', lines[i]):
      i = common.getDefineMacroEndLineNo(lines, i) + 1
      continue
    #预定义--skip
    if strcmp.Search(r'^\s*#', lines[i]):
      i += 1
      continue

    if (strcmp.Search(r'(\b^\.*strcpy\b\s*\()|(\b^\.*sprintf\b\s*\()|(\b^\.*strcat\b\s*\()', lines[i])):
      Error(filename, lines, i, ruleCheckKey, 3, errMessage)
      i += 1
      continue
  
    i += 1
