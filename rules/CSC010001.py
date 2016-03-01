#!/usr/bin/python  
#-*- coding: utf-8 -*-
'''
Created on 2014-2-11
rule:头文件包含规则:
     使用<>来引用系统头文件，使用“”引用非系统头文件
    所谓的“系统头文件”，一般包括：
    1.C标准库的头文件
    2.操作系统相关的头文件
    3.C++标准库的头文件
    4.非标准库的头文件
    头文件要按照上面的顺序
  (2,4 不check)
@author: wangxc
'''
import os
import sys
syspath = os.path.dirname(os.path.dirname(__file__))
if not os.path.join(syspath, "tools") in sys.path:
  sys.path.append(os.path.join(syspath, "tools"))
import common
strcmp = common.StringCompareInfo()

#C标准库头文件(18)
_C_HEADERS = frozenset([
    'assert.h', 'ctype.h', 'errno.h', 'float.h', 'iso646.h',
    'limits.h', 'locale.h','math.h', 'setjmp.h', 'signal.h', 
    'stdarg.h', 'stddef.h', 'stdio.h', 'stdlib.h','string.h',
    'time.h', 'wchar.h', 'wctype.h'
    ])
#C++标准库头文件(33)
#18 Legacy C Library Headers + 10 stream headers + 4 language support headers
#+ 6 odds and ends headers + 13 STL Library Headers
_CPLUSPLUS_HEADERS = frozenset([
    'cassert', 'cctype', 'cerrno', 'cfloat', 'ciso646',
    'climits', 'clocale', 'cmath', 'csetjmp', 'csignal',
    'cstdarg', 'cstddef', 'cstdio', 'cstdlib', 'cstring',
    'ctime', 'cwchar', 'cwctype',
    'fstream', 'iomanip', 'ios', 'iosfwd', 'iostream',
    'istream', 'ostream', 'sstream', 'streambuf', 'strstream',
    'exception', 'new', 'stdexcept', 'typeinfo',
    'bitset', 'complex', 'limits', 'locale', 'string',
    'valarray',
    'algorithm', 'deque', 'functional', 'iterator', 'list',
    'map', 'memory', 'numeric', 'queue', 'set',
    'stack', 'vector', 'utility'
    ])

def CheckCSC010001(filename, file_extension, clean_lines, rawlines, nesting_state, ruleCheckKey, Error, cpplines, fileErrorCount):
  #非头文件时，不check
  if file_extension != "h":
    return
  lines = clean_lines.elided
  errorMessageHeader = 'Code Style Rule:'
  #使用“”引用系统头文件时的error message
  errMessageIncludeChar = ' Please use bracket < > (not double quotes "") to include system header files.'
  #C标准库的头文件在C++标准库的头文件之后时的error message
  errMessageOrder = ' Please include C Standard library header files before C++ Standard Library header files.'
  firstCppHeaderLineNo = clean_lines.NumLines() + 1
  for i in xrange(clean_lines.NumLines()):
    errorMessage = ''
    isCHeader = False
    isCppHeader = False
    #空白行-- skip
    if common.IsBlankLine(lines[i]):
      continue
    # check include--#include <assert.h> #include <cassert> #include "main.h"
    m = strcmp.Search(r'^\s*#\s*include\s*([<"])([^>"]*)[>"].*$', lines[i])
    if m:
      if m.group(2) in _C_HEADERS:
        #C标准库
        isCHeader = True
      elif m.group(2) in _CPLUSPLUS_HEADERS:
        #C++标准库
        isCppHeader = True
      if (isCHeader or isCppHeader) and m.group(1) == '"':
        #使用“”引用系统头文件(C标准库, C++标准库)报错
        errorMessage = errMessageIncludeChar
      if isCHeader:
        if i > firstCppHeaderLineNo:
          #引用顺序，引用C标准库前引用了C++标准库,报错
          errorMessage += errMessageOrder
      elif isCppHeader:
        if firstCppHeaderLineNo == clean_lines.NumLines() + 1:
          #引用的第一个C++标准库的行号保存
          firstCppHeaderLineNo = i
      if errorMessage:
        errorMessage = errorMessageHeader + errorMessage
        Error(filename, lines, i, ruleCheckKey, 3, errorMessage)
        fileErrorCount[0] += 1
        if errorMessage.find(errMessageIncludeChar) > 0:
            cpplines[i] = cpplines[i].replace('"', '<', 1)
            cpplines[i] = cpplines[i].replace('"', '>')
        elif errorMessage.find(errMessageOrder) > 0:
            strTemp = cpplines[i]
            cpplines[i] = cpplines[firstCppHeaderLineNo]
            cpplines[firstCppHeaderLineNo] = strTemp
            firstCppHeaderLineNo = i
