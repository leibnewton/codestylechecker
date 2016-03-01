#!/usr/bin/python  
#-*- coding: utf-8 -*-
'''
Created on 2014-12-12

@author: zhangran
'''
import os
import sys
syspath = os.path.dirname(os.path.dirname(__file__))
if not os.path.join(syspath, "tools") in sys.path:
  sys.path.append(os.path.join(syspath, "tools"))
import common
strcmp = common.StringCompareInfo()

def getDefineMacroEndLineNo(lines, fromLno):
  lengthOfLines = len(lines)
  for i in xrange(fromLno, lengthOfLines):
    if not lines[i].endswith("\\"):
      return i
  return fromLno

def getBlockParenthesisEndLineNo(typeWord, lines, startLineNo):
  ''' 判断当前取得左右圆括号的介绍位置
  
  Args:
    filename:文件名
    lines:文件的内容
    rawlines:原始的文件内容
    startLineNo:开始的行数
    EndLineNo:结束的行数
    ruleCheckKey:rule的id
    Error:error的句柄
  Returns:
    bool: true 正确 false错误 
    integer: Block中右圆括号所在的行号.

  '''
  openParenthesisQty = 0
  closeParenthesisQty = 0
  
  skipEndLno = -1
  checkStartLineNo = -1
  leftParenthesesLno = -1
  rightParenthesesLno = -1
  
  lengthOfLines = len(lines)

  startLine = lines[startLineNo][lines[startLineNo].find(typeWord) + len(typeWord):]
  for i in xrange(startLineNo, lengthOfLines):
    endLineNo = i
    line = lines[i]
    if i == startLineNo:
      line = startLine
    if common.IsBlankLine(line):
      continue
    if strcmp.Search(r'^\s*#', line):
      continue
    if i <= skipEndLno:
      continue
    if strcmp.Search(r'^\s*#\s*define\s+', line):
      skipEndLno = getDefineMacroEndLineNo(lines, i)
      continue
    openParenthesisQty = openParenthesisQty + line.count('(')
    closeParenthesisQty = closeParenthesisQty + line.count(')')

    
    # 左小括号的行设定
    if openParenthesisQty > 0 and -1 == leftParenthesesLno:
      leftParenthesesLno = i
    
    # 右小括号的行设定
    if rightParenthesesLno == -1 and closeParenthesisQty > 0 and closeParenthesisQty == openParenthesisQty:
      rightParenthesesLno = i
      break
  
    # 找到{则终止
    if line.count('{') > 0 :
      break
      
    #没有括号，说明不是函数
  if openParenthesisQty < 0:
    return False, rightParenthesesLno
    
  #统计的左右圆括号数量不一致，说明代码有问题，不check，返回错误
  if openParenthesisQty != closeParenthesisQty:
    return False, rightParenthesesLno

  return True, rightParenthesesLno


def CheckCSC040004(filename, file_extension, clean_lines, rawlines, nesting_state, ruleCheckKey, Error, cpplines, fileErrorCount):
  '''条件表达式中的赋值操作
    禁止在条件表达式中使用赋值语句：

  '''
    
  errorMessage = 'Code Style Rule: There should be no assignment statements in conditional expressions.'
    
  lines = clean_lines.elided
  i = 0
  while i < clean_lines.NumLines():
    if common.IsBlankLine(lines[i]):
      i += 1
      continue
    if strcmp.Search(r'^\s*#\s*define\s+', lines[i]):
      i = getDefineMacroEndLineNo(lines, i) + 1
      continue
    if strcmp.Search(r'^\s*#', lines[i]):
      i += 1
      continue
  
    #查找if/while/for的语句
    m = strcmp.Search(r'\s*(if|while|for)\s*\(', lines[i])
    if m:
      retFLg, endLineNo = getBlockParenthesisEndLineNo(m.group(1), lines, i)
      if retFLg:

        startFindIndex = 0
        endFindIndex = 0
        
        conditionLineStr = ''
        for j in range(i, endLineNo + 1):
          conditionLineStr = conditionLineStr + lines[j]
        
        if len(conditionLineStr) > 3:
        
          startFindIndex = conditionLineStr.find('(')
          findIdx = conditionLineStr.rfind('{')
          if -1 == findIdx:
            endFindIndex = conditionLineStr.rfind(')')
          else :
            #条件语句在同一行
            endFindIndex = conditionLineStr.rfind(')', 0, findIdx)
            
          if m.group(1) == 'for':
            # for的第二个条件
            startFindIndex = conditionLineStr.find(';', startFindIndex, endFindIndex)
            if -1 == startFindIndex:
              i += 1
              continue
            endFindIndex = conditionLineStr.find(';', startFindIndex + 1 ,endFindIndex)
            if -1 == endFindIndex:
              i += 1
              continue
          
          #查找'=','=='例外
          if strcmp.Search(r'\s*[^=!><]=[^=><]\s*', lines[j][startFindIndex:endFindIndex]):
            Error(filename, lines, j, ruleCheckKey, 3, errorMessage)
        i = endLineNo
    
    i += 1 