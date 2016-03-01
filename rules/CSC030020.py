#!/usr/bin/python  
#-*- coding: utf-8 -*-
'''
Created on 2014-12-12

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

def checkWhetherHasCodeAfterComment(lines, startLine, linestartLno):
  '''check 注释后是否有代码
  Args:
    lines:所有行
    startLine:/*所在行的/*后的字符串
    linestartLno:/*所在行的line number
  Returns:
            是否有代码(True:yes,False:no),注释结束的
  '''
  hasCode = False
  commentEndLno = -1
  commentEndLno = getMultiCommentEndLno(lines, startLine[2:], linestartLno)
  if commentEndLno == -1:
    return False, -1
  # /*对应的*/不在本行时,说明/*是该行最后一个注释
  if commentEndLno > linestartLno:
    return False, commentEndLno
  # /*对应的*/不在本行时
  endIndex = startLine[2:].find('*/')
  if endIndex == -1:
    return False, -1
  endIndex = endIndex + 4
  tempLine = startLine[endIndex:].strip()
  # */后为空白(or换行符or//),说明/**/后没有代码
  if (not tempLine) or tempLine == '\\' or tempLine.startswith('//'):
    return False, linestartLno
  if tempLine.startswith('/*'):
    hasCode, commentEndLno = checkWhetherHasCodeAfterComment(lines, tempLine, linestartLno)
    return hasCode,commentEndLno
  else:
    return True, linestartLno
  

def CheckCSC030020(filename, file_extension, clean_lines, rawlines, nesting_state, ruleCheckKey, Error, cpplines, fileErrorCount):
  '''语句行末的注释之前，至少保留一个空格。
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
  errMessage = "Code Style Rule: There should be at least one space in front of the end-of-line comment."
  commentEndLno = -1
  for i in xrange(clean_lines.NumLines()):
    # 多行注释,中间的行不做check
    if i < commentEndLno:
      continue
    # 空行（或者该行全是注释）不用check
    if common.IsBlankLine(lines[i]):
      continue
    # 查找当行是否有注释标识符
    # 当前行是多行注释的*/所在的行时,即当前行是下面例子中的第2行时,从第2行的*/后面开始查找
    # String a; /* 1111 */ String b; /* 2222
    #                                /* 2222 */ String C; // 333333
    startIndex = -1
    endIndex = -1
    
    if commentEndLno == i:
      commentEndLno = -1
      startIndex = rawlines[i].find('*/')
      if startIndex == -1:
        break
      m = strcmp.Search(r'(/\*|//)', rawlines[i][startIndex + 2:])
      if m:
        endIndex = startIndex + 2 + m.end()
        startIndex = startIndex + 2 + m.start()
    
          
      startIndex2 = cpplines[i].find('*/')
      m2 = strcmp.Search(r'(/\*|//)', cpplines[i][startIndex2 + 2:])

    # 当前行的开头不是注释时
    else:
      m = strcmp.Search(r'(/\*|//)', rawlines[i])
      if m:
        startIndex = m.start()
        endIndex = m.end()
    
      m2 = strcmp.Search(r'(/\*|//)', cpplines[i])

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
        # 查找注释结束的行号
        # //时，不再检测本行
        if m.group(1) == '//':
          # int a;/*xxx \n xxx*/ //xxxxx----当前行是第二行时，不check第二行了
          tempLine = rawlines[i][:startIndex].strip()
          if (not tempLine) or tempLine.endswith('*/'):
            commentEndLno = i
            break
          # 语句行末的注释之前，至少保留一个空格,否则报错
          if rawlines[i][startIndex - 1:startIndex] not in [' ','\t']:
            Error(filename, lines, i, ruleCheckKey, 3, errMessage)
            cpplines[i] = cpplines[i].replace(m.group(1), ' ' + m.group(1))
            fileErrorCount[0] =  fileErrorCount[0] + 1
            
          commentEndLno = i
          break
        else:
          commentEndLno = getMultiCommentEndLno(rawlines, rawlines[i][endIndex:], i)
          # 如果返回-1，说明查不到*/,文件有问题，不要再check该文件了
          if commentEndLno == -1:
            return
      # /*对应的*/不在本行时,说明/*是该行最后一个注释
      if commentEndLno > i:
        # 语句行末的注释之前，至少保留一个空格,否则报错
        if rawlines[i][startIndex - 1:startIndex] not in [' ','\t']:
          Error(filename, lines, i, ruleCheckKey, 3, errMessage)
          cpplines[i] = cpplines[i].replace(m.group(1), ' ' + m.group(1))
          fileErrorCount[0] =  fileErrorCount[0] + 1
        break
      # 查找/*对应的*/的位置，用于查找后面的/*
      # String A; /* 1111 */ String B;/* 2222
      #                                asdfs */
      elif commentEndLno == i and m.group(1) == '/*':
        endIndex = endIndex + rawlines[i][endIndex:].find('*/') + 2
        tempLine = rawlines[i][endIndex:].strip()
        # */后为空白(or换行符or//),说明/*是该行最后一个注释
        if (not tempLine) or tempLine == '\\' or tempLine.startswith('//'):
          # 语句行末的注释之前，至少保留一个空格,否则报错
          if rawlines[i][startIndex - 1:startIndex] not in [' ','\t']:
            Error(filename, lines, i, ruleCheckKey, 3, errMessage)
            cpplines[i] = cpplines[i].replace(m.group(1), ' ' + m.group(1))
            fileErrorCount[0] =  fileErrorCount[0] + 1
            
          commentEndLno = i
          break
        elif tempLine.startswith('/*'):
          hasCode, tempCommentEndLno = checkWhetherHasCodeAfterComment(rawlines, tempLine, i)
          if tempCommentEndLno == -1:
            return
          # */没有代码
          if not hasCode:
            # 语句行末的注释之前，至少保留一个空格,否则报错
            if rawlines[i][startIndex - 1:startIndex] not in [' ','\t']:
              Error(filename, lines, i, ruleCheckKey, 3, errMessage)
              cpplines[i] = cpplines[i].replace(m.group(1), ' ' + m.group(1))
              fileErrorCount[0] =  fileErrorCount[0] + 1
            
            if tempCommentEndLno > i:
              commentEndLno = tempCommentEndLno
            break
      # 查找下一个注释标识符
      m = strcmp.Search(r'(/\*|//)', rawlines[i][endIndex:])
      if m:
        inSingleQuotesblock = False
        inDoubleQuotesblock = False
        startIndex = endIndex + m.start()
        endIndex = endIndex + m.end()
        continue
      else:
        commentEndLno = -1
        startIndex = -1