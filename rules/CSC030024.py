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

def getMultiCommentEndLno(lines, startLine, linestartLno):
  '''查找多行注释
  Args:
    lines:所有行
    startLine:/*所在行的/*后的字符串
    linestartLno:/*所在行的line number
  Returns:
            返回离/*最近的*/所在的line number；如果查不到*/，则返回-1
  '''
  # 查找离/*最近的*/所在的line number
  if startLine.find('*/') > -1:
    return linestartLno
  i = linestartLno + 1
  while i < len(lines):
    if lines[i].find('*/') > -1:
      return i
    i = i + 1
  # 如果查不到*/，则返回-1，说明文件有问题，不要再check该文件了
  return -1

def CheckCSC030024(filename, file_extension, clean_lines, rawlines, nesting_state, ruleCheckKey, Error, cpplines, fileErrorCount):
  '''行末注释不允许有换行。
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
  errMessage = 'Code Style Rule: An end-of-line comment begins with "/*" is not allowed to wrap.'
  commentEndLno = -1
  for i in xrange(clean_lines.NumLines()):
    # 多行注释,中间的行不做check
    if i < commentEndLno:
      continue
    # 空行（或者该行全是注释）不用check
    if common.IsBlankLine(lines[i]):
      continue
    # 查找当行是否有注释标识符
    # 查找当行是否有注释标识符
    # 当前行是多行注释的*/所在的行时,即当前行是下面例子中的第2行时,从第2行的*/后面开始查找
    # String a; /* 1111 */ String b; /* 2222
    #                                /* 2222 */ String C; /* 333333
    startIndex = -1
    endIndex = -1
    if commentEndLno == i:
      commentEndLno = -1
      startIndex = rawlines[i].find('*/')
      if startIndex == -1:
        break
      m = strcmp.Search(r'/\*', rawlines[i][startIndex + 2:])
      if m:
        endIndex = startIndex + 2 + m.end()
        startIndex = startIndex + 2 + m.start()
    # 当前行的开头不是注释时
    else:
      m = strcmp.Search(r'/\*', rawlines[i])
      if m:
        startIndex = m.start()
        endIndex = m.end()
    if not m:
      continue
    inSingleQuotesblock = False
    inDoubleQuotesblock = False
    while startIndex != -1:
      # 判断注释标识符是否在两个单引号中间
      singleQuotesQty = rawlines[i][0:startIndex].count("'")
      if singleQuotesQty % 2 == 1 and rawlines[i][startIndex:].count("'") > 0:
        inSingleQuotesblock = True
      if not inSingleQuotesblock:
        # 判断注释标识符是否在两个双引号中间
        doubleQuotesQty = rawlines[i][0:startIndex].count('"')
        if doubleQuotesQty % 2 == 1 and rawlines[i][startIndex:].count('"') > 0:
          inDoubleQuotesblock = True
      # 注释标识符在两个单引号中间或者在两个双引号中间,查找下一个注释标识符
      if inSingleQuotesblock or inDoubleQuotesblock:
        pass
      # 注释标识符的确是注释的标志，而不是字符串中的字符
      else:
        singleCommentIndex = rawlines[i][:startIndex].find('//')
        # String a; //----  /*adsfaf /*是注释不需要check
        if singleCommentIndex > -1:
          startIndex = -1
          continue
        # 行末注释不允许有换行,否则报错
        endCommentIndex = rawlines[i][endIndex:].find('*/')
        if endCommentIndex == -1:
          Error(filename, lines, i, ruleCheckKey, 3, errMessage)
          # 查找注释结束的行号
          commentEndLno = getMultiCommentEndLno(rawlines, rawlines[i][endIndex:], i)
          # 如果返回-1，说明查不到*/,文件有问题，不要再check该文件了
          if commentEndLno == -1:
            return
          startIndex = -1
          continue
        else:
          endIndex = endIndex + endCommentIndex + 2
        # String a="fadsf"; /* 111111 */ i++ /*222222*/
        # 第一个/*有对应的*/时，查看该*/后有没有/*,没有则不再check本行，否则继续检查        
      m = strcmp.Search(r'/\*', rawlines[i][endIndex:])
      if m:
        inSingleQuotesblock = False
        inDoubleQuotesblock = False
        startIndex = endIndex + m.start()
        endIndex = endIndex + m.end()
        continue
      else:
        startIndex = -1