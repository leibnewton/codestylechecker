#!/usr/bin/python  
#-*- coding: utf-8 -*-
'''
Created on 2014-2-11

@author: wangxc
'''
import os
import sys
syspath = os.path.dirname(os.path.dirname(__file__))
if not os.path.join(syspath, "tools") in sys.path:
  sys.path.append(os.path.join(syspath, "tools"))
import common
strcmp = common.StringCompareInfo()
import re

def getDefineMacroEndLineNo(lines, fromLno):
  lengthOfLines = len(lines)
  for i in xrange(fromLno, lengthOfLines):
    if not lines[i].endswith("\\"):
      return i
  return fromLno

def CheckCSC020001(filename, file_extension, clean_lines, rawlines, nesting_state, ruleCheckKey, Error, cpplines, fileErrorCount):
  lines = clean_lines.elided
  skipDefineEndLno = -1
  for i in xrange(clean_lines.NumLines()):
    #null line skip
    if common.IsBlankLine(lines[i]):
      continue
    #define line skip
    if i <= skipDefineEndLno:
      continue 
    if strcmp.Search(r'^\s*#\s*define\s+', lines[i]):
      skipDefineEndLno = getDefineMacroEndLineNo(lines, i)
      continue
    # line start with # skip
    if strcmp.Search(r'^\s*#', lines[i]):
      continue
    m = strcmp.Search(r'^(\s*)\S', lines[i])
    if m:
      indentWords = m.group(1)
      if indentWords.find('\t') > -1:
        Error(filename, lines, i, ruleCheckKey, 3,'Code Style Rule: Tab found. Please use 4 spaces for indentation.')
        fileErrorCount[0] += 1
        cpplines[i] = cpplines[i].expandtabs(4)
        continue
#  因为CSC020007（新行可以有两种缩进方式：相对首行缩进4个空格；新行从首行左括号处开始缩进），故不在check缩进的空格数是否是4的倍数
#     if len(indentWords) % 4 != 0:
#       Error(filename, lines, i, ruleCheckKey, 2,'Code Style Rule: Please use 4 spaces for indentation.')
  
      