#!/usr/bin/python  
#-*- coding: utf-8 -*-
'''
Created on 2014-12-08

@author: wangxc
'''
import os
import sys
syspath = os.path.dirname(os.path.dirname(__file__))
if not os.path.join(syspath, "tools") in sys.path:
  sys.path.append(os.path.join(syspath, "tools"))
import common
strcmp = common.StringCompareInfo()

def CheckCSC030025(filename, file_extension, clean_lines, rawlines, nesting_state, ruleCheckKey, Error, cpplines, fileErrorCount):
  '''函数功能：右括号)和左大括号{之间留一个空格。
  Args:
    filename:文件名
    file_extension:文件扩展名
    clean_lines:Holds 3 copies of all lines with different preprocessing applied to them
                 1) elided member contains lines without strings and comments,
                 2) lines member contains lines without comments, and
                 3) raw_lines member contains all the lines without processing.（行首以/*开头的多行注释被替换成空白）
    rawlines：all the lines without processing
    nesting_state: Holds states related to parsing braces.(cpplint中的对象，暂时未使用)
    startLineNo:for,while,if,switch所在的行
    ruleCheckKey:ruleid
    Error: error output method
  '''
  lines = clean_lines.elided
  errMessage = 'Code Style Rule: Please leave a space between the right parenthesis ")" and the left curly brace "{" if they are in the same line.'
  for i in xrange(clean_lines.NumLines()):
    if common.IsBlankLine(lines[i]):
      continue
    m = strcmp.Search(r'\)(\s*)\{', lines[i])
    if m:
      if not m.group(1):
        Error(filename, lines, i, ruleCheckKey, 3, errMessage)
        fileErrorCount[0] += 1
        cpplines[i] = cpplines[i].replace("){", ") {")
      continue