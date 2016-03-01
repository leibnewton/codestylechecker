#!/usr/bin/python  
#-*- coding: utf-8 -*-
'''
Created on 2014-12-10

@author: wangxc
'''
import os
import sys
syspath = os.path.dirname(os.path.dirname(__file__))
if not os.path.join(syspath, "tools") in sys.path:
  sys.path.append(os.path.join(syspath, "tools"))
import common
strcmp = common.StringCompareInfo()

def CheckCSC030028(filename, file_extension, clean_lines, rawlines, nesting_state, ruleCheckKey, Error, cpplines, fileErrorCount):
  '''右大括号}之前如果有内容，请保留一个空格。[必须] 
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
  errMessage = 'Code Style Rule: If there is contents before a right curly brace "}", please leave a space between them.'
  i = 0
  while i < clean_lines.NumLines():
    # null line skip
    if common.IsBlankLine(lines[i]):
      i += 1
      continue
    #define line skip
    if strcmp.Search(r'^\s*#\s*define\s+', lines[i]):
      i = common.getDefineMacroEndLineNo(lines, i) + 1
      continue
    # line start with # skip
    if strcmp.Search(r'^\s*#', lines[i]):
      i += 1
      continue
    m = strcmp.Search(r'[^\s\{]\}', lines[i])
    # 当 } 前面的字符不是空格，也不是{，则报错
    if m:
      Error(filename, lines, i, ruleCheckKey, 3, errMessage)
      fileErrorCount[0] += 1
      cpplines[i] = cpplines[i].replace("}", " }")
      i += 1
      continue
    # 查看}前是否紧跟着多行注释标识符的*/
    m = strcmp.Search(r'\*/\}', rawlines[i])
    # 找不到这种情况，进入下次循环
    if not m:
      i += 1
      continue
    startIndex = m.start()
    endIndex = m.end()
    # */} 是//后面的注释内容则check下一行，不再check本行了
    if rawlines[i][startIndex:].rfind('//') > -1:
      i += 1
      continue
    inSingleQuotesblock = False
    inDoubleQuotesblock = False
    while startIndex != -1:
      # 判断*/}是否在两个单引号中间
      singleQuotesQty = rawlines[i][0:startIndex].count("'")
      if singleQuotesQty % 2 == 1 and rawlines[i][startIndex:].count("'") > 0:
        inSingleQuotesblock = True
      if not inSingleQuotesblock:
        # 判断*/}是否在两个双引号中间
        doubleQuotesQty = rawlines[i][0:startIndex].count('"')
        if doubleQuotesQty % 2 == 1 and rawlines[i][startIndex:].count('"') > 0:
          inDoubleQuotesblock = True
      # */}在两个单引号中间或者在两个双引号中间,需要查找下一个{  }
      if inSingleQuotesblock or inDoubleQuotesblock:
        # 查找下一个*/}
        m = strcmp.Search(r'\*/\}', rawlines[i][endIndex:])
        if m:
          inSingleQuotesblock = False
          inDoubleQuotesblock = False
          startIndex = endIndex + m.start()
          endIndex = endIndex + m.end()
        # 查找不到下一个*/},不再检查本行了，去检查下一行
        else:
          i += 1
          startIndex = -1 
      # */}不是字符串中的字符
      else:
        # */} 不是//后面的注释内容，则报错；如果是//后面的注释内容，则check下一行，不再check本行了
        if rawlines[i][startIndex:].rfind('//') == -1:        
          Error(filename, lines, i, ruleCheckKey, 3, errMessage)
          fileErrorCount[0] += 1
          cpplines[i] = cpplines[i].replace("}", " }")
        i += 1
        startIndex = -1
        