#!/usr/bin/python  
#-*- coding: utf-8 -*- 
'''
Created on 2014-3-24

@author: zhangran
'''
import os
import sys
syspath = os.path.dirname(os.path.dirname(__file__))
if not os.path.join(syspath, "tools") in sys.path:
  sys.path.append(os.path.join(syspath, "tools"))
import common
strcmp = common.StringCompareInfo()

def getParenthesisEndLineNo(lines, startLno):
  lengthOfLines = len(lines)
  leftAngleParenthesisQty = 0
  rightAngleParenthesisQty = 0
  for i in xrange(startLno, lengthOfLines):
    if common.IsBlankLine(lines[i]):
      continue
    if strcmp.Search(r'^\s*#', lines[i]):
      continue
    leftAngleParenthesisQty = leftAngleParenthesisQty + lines[i].count('(')
    rightAngleParenthesisQty = rightAngleParenthesisQty + lines[i].count(')')
    if leftAngleParenthesisQty == rightAngleParenthesisQty:
      return i
  return -1

#‘{’与for同行
def CheckCSC080005(filename, file_extension, clean_lines, rawlines, nesting_state, ruleCheckKey, Error, cpplines, fileErrorCount):
  lines = clean_lines.elided
  errMessage = "Code Style Rule: Please put the opening curly brace of a for loop on the same line with the for keyword."
  
  i = 0
  while i < clean_lines.NumLines():
    
    #define line skip
    if strcmp.Search(r'^\s*#\s*define\s+', lines[i]):
      i = common.getDefineMacroEndLineNo(lines, i) + 1
      continue
  
    if strcmp.Search(r'^\s*for\s*\(', lines[i]):
      lineNo = getParenthesisEndLineNo(lines, i)
      if lineNo != -1:
          i = lineNo
          if not lines[i].strip().endswith('{'):
            Error(filename, lines, i, ruleCheckKey, 3, errMessage)
            i = i + 1
            continue
    
    i += 1