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

def CheckCSC030015(filename, file_extension, clean_lines, rawlines, nesting_state, ruleCheckKey, Error, cpplines, fileErrorCount):
  lines = clean_lines.elided
  errMessage = 'Code Style Rule: There should be a space after ",". For example: Function(x, y, z).'
  for i in xrange(clean_lines.NumLines()):
    if common.IsBlankLine(lines[i]):
      continue
    m = strcmp.Search(r',[^\s,\\\)\}]', lines[i])
    if m:
      Error(filename, lines, i, ruleCheckKey, 3, errMessage)
      fileErrorCount[0] += 1
      icount = cpplines[i].count(",");
      if cpplines[i].endswith(","):
        icount -= 1
      cpplines[i] = cpplines[i].replace(",", ", ", icount)