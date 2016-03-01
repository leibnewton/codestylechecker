#!/usr/bin/python  
#-*- coding: utf-8 -*-
'''
Created on 2014-2-10

@author: wangxc
'''
import os
import sys
syspath = os.path.dirname(os.path.dirname(__file__))
if not os.path.join(syspath, "tools") in sys.path:
  sys.path.append(os.path.join(syspath, "tools"))
import common
strcmp = common.StringCompareInfo()

def CheckCSC010007(filename, file_extension, clean_lines, rawlines, nesting_state, ruleCheckKey, Error, cpplines, fileErrorCount):

  lines = clean_lines.elided
  for i in xrange(clean_lines.NumLines()):
    if common.IsBlankLine(lines[i]):
      continue
    m = strcmp.Search(r'^\s*#\s*include\s*([<"])([^>"]*)[>"].*$', lines[i])
    if m:
      include = m.group(2)
      #禁止使用相对路径（含有..的路径）
      if strcmp.Search(r'\.\.[/\\]', include):
        Error(filename, lines, i, ruleCheckKey, 3,"Code Style Rule: Please don\'t use relative path with \"..\" when including a header file.")