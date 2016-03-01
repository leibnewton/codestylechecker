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

def getEndInfoOfCondition(lines, startLineNo, keyWordIndex):
  '''函数功能：查找for,while,if,switch后面的()中）所在的行，及其在所在行的位置
  Args:
    lines:文件中各个行的内容组成的数组（已去完注释，字符串已被清空）
    startLineNo:for,while,if,switch所在的行
    keyWordIndex:for,while,if,switch在行中的index
  Returns:
             右圆括号的lineNo,其位于所在行的位置,如果找不到，则返回-1，-1
  '''
  linesLength = len(lines)
  i = startLineNo
  openParenthesisQty = 0
  closeParenthesisQty = 0
  while i < linesLength:
    #空白行--skip
    if common.IsBlankLine(lines[i]):
      i += 1
      continue
    #宏定义--skip
    if strcmp.Search(r'^\s*#\s*define\s+', lines[i]):
      i = common.getDefineMacroEndLineNo(lines, i) + 1
      continue
    #预定义--skip
    if strcmp.Search(r'^\s*#', lines[i]):
      i = common.getDefineMacroEndLineNo(lines, i) + 1
      continue
    checkStartIndex = 0
    if i == startLineNo:
      checkStartIndex = keyWordIndex
    #逐个字符累计左右圆括号
    for j in xrange(checkStartIndex, len(lines[i])):
      if lines[i][j] == '(':
        openParenthesisQty += 1
      elif lines[i][j] == ')':
        closeParenthesisQty += 1
      #左右圆括号个数相同，则返回最后一个右圆括号的lineNo,其位于所在行的位置
      if openParenthesisQty == closeParenthesisQty and openParenthesisQty > 0:
        return i, j
    i += 1
  return -1, -1

def getEndInfoOfLastForConditionInALine(lines, startLineNo):
  '''函数功能：查找一行中假如一行中写了多个for，查找最后一个for后面的()中）所在的行，及其在所在行的位置
  Args:
    lines:文件中各个行的内容组成的数组（已去完注释，字符串已被清空）
    startLineNo:for,while,if,switch所在的行
    keyWordIndex:for,while,if,switch在行中的index
  Returns:
     
             是否有系统错误,是否有for,右圆括号的lineNo,其位于所在行的位置,如果找不到，则返回-1，-1
  '''
  # 注释没有正确清楚时，不要再check本文件了
  if lines[startLineNo].find('/*') > -1:
    return True, False, -1, -1
  temp = lines[startLineNo][::-1]
  mFor = strcmp.Search(r'\brof\b', temp)
  if not mFor:
    return False, False, -1, -1
  startIndex = len(lines[startLineNo]) -mFor.start() - 2
  endLineNo, endLineIndex = getEndInfoOfCondition(lines, startLineNo, startIndex)
  if endLineNo == -1:
    return True, True, -1, -1
  else:
    return False, True, endLineNo, endLineIndex
  

def CheckCSC020010(filename, file_extension, clean_lines, rawlines, nesting_state, ruleCheckKey, Error, cpplines, fileErrorCount):
  '''函数功能：一行中最多有一条语句。
                                     特殊：for循环除外
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
  errorMessage = 'Code Style Rule: There should be only one statement per line.'
  lines = clean_lines.elided
  i = 0
  closeParenthesisLineNo = -1
  closeParenthesisIndex = -1
  while i < clean_lines.NumLines():
    #空白行--skip
    if common.IsBlankLine(lines[i]):
      i += 1
      continue
    #宏定义--skip
    if strcmp.Search(r'^\s*#\s*define\s+', lines[i]):
      i = common.getDefineMacroEndLineNo(lines, i) + 1
      continue
    #预定义--skip
    if strcmp.Search(r'^\s*#', lines[i]):
      i = common.getDefineMacroEndLineNo(lines, i) + 1
      continue
    findIndex = 0
    preCloseParenthesisIndex = -1
    preCloseParenthesisLineNo = -1
    if closeParenthesisLineNo == i:
      preCloseParenthesisLineNo = closeParenthesisLineNo
      preCloseParenthesisIndex = closeParenthesisIndex
      findIndex = closeParenthesisIndex
    #查找for
    mFor = strcmp.Search(r'\bfor\b', lines[i][findIndex:])
    if mFor:
      #当前行有之前for的)时
      # for (af;adsf;
      # ) { for (
      if preCloseParenthesisLineNo == i:
        Error(filename, lines, i, ruleCheckKey, 3, errorMessage)
        hasSystemError,hasLastFor,closeParenthesisLineNo,closeParenthesisIndex=getEndInfoOfLastForConditionInALine(lines, i)
        if hasSystemError:
          return
        if closeParenthesisLineNo == -1:
          return
        if closeParenthesisLineNo == i:
          i += 1
          continue
        if closeParenthesisLineNo > i:
          i = closeParenthesisLineNo
          continue
      # 当前行没有之前for的)时
      # AAA(); for(i=0;i<1;i++) { 
      if strcmp.Search(r';\s*[^\s\}\)\\/]', lines[i][0:mFor.end()]):
        Error(filename, lines, i, ruleCheckKey, 3, errorMessage)
        #查找本行最后最后一个for的)所在的位置
        hasSystemError,hasLastFor,closeParenthesisLineNo,closeParenthesisIndex=getEndInfoOfLastForConditionInALine(lines, i)
        if hasSystemError:
          return
        if closeParenthesisLineNo == -1:
          return
        if closeParenthesisLineNo == i:
          i += 1
          continue
        if closeParenthesisLineNo > i:
          i = closeParenthesisLineNo
          continue
      # 当前行没有之前for的)时
      #  for(i=0;i<1;i++) { ......
      closeParenthesisLineNo, closeParenthesisIndex = getEndInfoOfCondition(lines, i, findIndex + mFor.start())
      #找不到for的()中）所在的行号
      if closeParenthesisLineNo == -1:
        return
      # for的)在不在本行在后面时,不再check本行了，check)在的行
      #for(i=0;i<1;
      #i++) { ......
      if closeParenthesisLineNo > i:
        i = closeParenthesisLineNo
        continue
      #for的)在本行时
      elif closeParenthesisLineNo == i:
        secondFor = strcmp.Search(r'\bfor\b', lines[i][closeParenthesisIndex:])
        # 本行有两个以上的for时
        # for(i=0;i<1;){ for(i=0
        if secondFor:
          Error(filename, lines, i, ruleCheckKey, 3, errorMessage)
          #查找本行最后最后一个for的)所在的位置
          hasSystemError,hasLastFor,closeParenthesisLineNo,closeParenthesisIndex=getEndInfoOfLastForConditionInALine(lines, i)
          if hasSystemError:
            return
          if closeParenthesisLineNo == -1:
            return
          if closeParenthesisLineNo == i:
            i += 1
            continue
          if closeParenthesisLineNo > i:
            i = closeParenthesisLineNo
            continue
        # 本行有1个for时
        else:
          #查看该行中是否出现这种情况: ;后面有语句
          #1.for () {aaa();bbb()
          #2.for () {aaa();
          mSemicolon = strcmp.Search(r';\s*[^\s\}\)\\/]|[^\s\{\}]\s*;', lines[i][closeParenthesisIndex:])
          if mSemicolon:
            if mSemicolon.start():
              Error(filename, lines, i, ruleCheckKey, 3, errorMessage)
          i += 1
          continue
    #在for的condition表达式之外时
    else:
      # 当前行时下列情形的第二行时
      #   for(int i=0;i<10
      #   i++){ function();
      #   }
      if preCloseParenthesisLineNo == i:
        m = strcmp.Search(r'[^\s\{\}]\s*;', lines[i][preCloseParenthesisIndex + 1:])
        if m:
          #避免下面情形误判.因为既存处理，行末/**/换行时可能无法lines中可能残留注释  
          #   for(int i=0;i<10
          #   i++){  /*function();
          #   }
          if lines[i][preCloseParenthesisIndex + 1:m.start()].find('/*') == -1:
            Error(filename, lines, i, ruleCheckKey, 3, errorMessage)
        i += 1
        continue
      #当前行中没有for的表达式
      #查看该行中是否出现这种情况: ;后面有语句
      mSemicolon = strcmp.Search(r';\s*[^\s\}\)\\/]', lines[i])
      if mSemicolon:
        #当前行没有之前for的)时
        #funtion(); AAA();
        if preCloseParenthesisLineNo < i:
          Error(filename, lines, i, ruleCheckKey, 3, errorMessage)
        #当前行有之前for的)时
        # for (asdf;asdf;
        #     ){ funtion();funtion2();
        if preCloseParenthesisLineNo == i and mSemicolon.start() > preCloseParenthesisIndex:
          Error(filename, lines, i, ruleCheckKey, 3, errorMessage)
        #当前行有之前for的)时
        # for (asdf;
        #     asdf;){ funtion();funtion2();
        elif preCloseParenthesisLineNo == i and mSemicolon.start() < preCloseParenthesisIndex:
          if strcmp.Search(r';\s*[^\s\}\)\\/]', lines[i][preCloseParenthesisIndex:]):
            Error(filename, lines, i, ruleCheckKey, 3, errorMessage)
        
      i += 1
      continue
    


    