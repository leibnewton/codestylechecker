#!/usr/bin/python  
#-*- coding: utf-8 -*-
'''
Created on 2014-6-30

@author: zhangran
'''
import os
import sys
syspath = os.path.dirname(os.path.dirname(__file__))
if not os.path.join(syspath, "tools") in sys.path:
  sys.path.append(os.path.join(syspath, "tools"))
import common
strcmp = common.StringCompareInfo()


#C标准库头文件(18)
MACRO_KEY = frozenset([
    'include','define', 'if', 'ifdef', 'ifndef', 'else',
    'elif', 'endif','undef'
    ])

def CheckCSC010015(filename, file_extension, clean_lines, rawlines, nesting_state, ruleCheckKey, Error, cpplines, fileErrorCount):
  lines = rawlines
  errMessage = 'Code Style Rule: The hash mark that starts a preprocessor directive should always be at the beginning of the line.'
  
  for i in xrange(len(rawlines)):
    
    #空白行-- skip
    if common.IsBlankLine(rawlines[i]):
      continue
  
    # 针对下面的关键字列表，使用python就可以判断了。
    # #define, #if, #ifdef, #ifndef, #else, #elif, #endif, #undef
    m = strcmp.Search(r'\s+#\s*(\w+)\b', rawlines[i])
    if m:
      if m.group(1) in MACRO_KEY:
        if -1 == rawlines[i][:rawlines[i].find(m.group(1))].find('//') and -1 == rawlines[i][:rawlines[i].find(m.group(1))].find('*'):
          Error(filename, lines, i, ruleCheckKey, 3, errMessage)
          cpplines[i] = cpplines[i].lstrip()
          fileErrorCount[0] =  fileErrorCount[0] + 1
          