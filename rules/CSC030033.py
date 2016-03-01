#!/usr/bin/python  
#-*- coding: utf-8 -*-
'''
Created on 2015-3-16
rule:类的构造函数的初始化列表中的空格遵循下面的规范:':'和表达式之间必须有空格
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

def checkSignLeftRightBlank(line, leftPos, rightPos):

  # 符号有换行
  if len(line) <= rightPos :
    return True
  if (line[leftPos:leftPos + 1] == ' ' or line[leftPos:leftPos + 1] == '\t') and  (line[rightPos:rightPos + 1] == ' ' or line[rightPos:rightPos + 1] == '\t'):
    return True
  return False


def isFunctionDeclare(typeWord, lines, startLineNo):
  ''' 判断当前是函数声明还是函数定义
  
  Args:
    typeWord:关键字
    lines:文件的内容
    rawlines:原始的文件内容
    startLineNo:开始的行数
  Returns:
    integer: -1.发生错误 0.不是函数  1.函数声明  2.函数定义 
    integer: function()中左圆括号所在的行号.
    integer: function()中右圆括号所在的行号.
    integer: function()中 {所在的行号.
    integer: function()中 }所在的行号.
  '''
    
  openCurlyBraceQty = 0
  closeCurlyBraceQty = 0
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
    if i <= skipEndLno:
      continue
    if strcmp.Search(r'^\s*#\s*define\s+', line):
      skipEndLno = getDefineMacroEndLineNo(lines, i) + 1
      continue
    if strcmp.Search(r'^\s*#', line):
      continue
  
    openCurlyBraceQty = openCurlyBraceQty + line.count('{')
    closeCurlyBraceQty = closeCurlyBraceQty + line.count('}')
    openParenthesisQty = openParenthesisQty + line.count('(')
    closeParenthesisQty = closeParenthesisQty + line.count(')')
    
    # 左小括号的行设定
    if openParenthesisQty > 0 and -1 == leftParenthesesLno:
      leftParenthesesLno = i
    
    # 右小括号的行设定
    if rightParenthesesLno == -1 and closeParenthesisQty > 0 and closeParenthesisQty == openParenthesisQty:
      rightParenthesesLno = i
    
    if openCurlyBraceQty > 0 and checkStartLineNo == -1:
      checkStartLineNo = i
      
    #函数的声明
    if line.count(";") > 0 and 0 == openCurlyBraceQty:
      break;
  
    #函数的定义
    if openCurlyBraceQty == closeCurlyBraceQty and rightParenthesesLno > 0 and closeCurlyBraceQty > 0:
      break

  #没有括号，说明不是函数
  if openParenthesisQty < 0:
    return 0, leftParenthesesLno, rightParenthesesLno, checkStartLineNo, endLineNo
    
  #统计的左右圆括号数量不一致，说明代码有问题，不check，返回错误
  if openParenthesisQty != closeParenthesisQty:
    return -1, leftParenthesesLno, rightParenthesesLno, checkStartLineNo, endLineNo

  #统计的左右大括号数量不一致，说明代码有问题，不check，返回错误
  if openCurlyBraceQty != closeCurlyBraceQty:
    return -1, leftParenthesesLno, rightParenthesesLno, checkStartLineNo, endLineNo
  
  #函数的声明
  if line.rstrip().endswith(';'):
    return 1, leftParenthesesLno, rightParenthesesLno, checkStartLineNo, endLineNo

  #函数的声明
  if line.rstrip().endswith(';'):
    return 1, leftParenthesesLno, rightParenthesesLno, checkStartLineNo, endLineNo

  #函数的定义
  if closeCurlyBraceQty > 0 and closeParenthesisQty > 0 :
    return 2, leftParenthesesLno, rightParenthesesLno, checkStartLineNo, endLineNo

  return -1, leftParenthesesLno, rightParenthesesLno, checkStartLineNo, endLineNo

def isBlockDeclareCheck(lines, startLineNo, blockKey):
  ''' 传入struct，enum，union，class关键字，取得相应的{ }的范围
  
  Args:
    lines:文件的内容
    startLineNo:开始的函数
    blockKey:块的关键字
  '''
    
  openCurlyBraceQty = 0
  closeCurlyBraceQty = 0
  lengthOfLines = len(lines)
  skipEndLno = -1
  endLineNo = -1
  checkStartLineNo = -1
  line = ''
  startLine = lines[startLineNo][lines[startLineNo].find(blockKey) + len(blockKey):]
  
  # 结构体初期化的情况
  # eg. struct weston_matrix scale = {
  if -1 != startLine.find('=') :
    return False, checkStartLineNo, endLineNo

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
      skipEndLno = getDefineMacroEndLineNo(lines, i) + 1
      continue
    openCurlyBraceQty = openCurlyBraceQty + line.count('{')
    closeCurlyBraceQty = closeCurlyBraceQty + line.count('}')
    if openCurlyBraceQty > 0 and checkStartLineNo == -1:
      checkStartLineNo = i
    if openCurlyBraceQty == closeCurlyBraceQty and line.rstrip().endswith(';'):
      break
  if openCurlyBraceQty != closeCurlyBraceQty:
    return False, checkStartLineNo, endLineNo
  if openCurlyBraceQty == 0:
    return False, checkStartLineNo, endLineNo
  if not line.rstrip().endswith(';'):
    return False, checkStartLineNo, endLineNo
  return True, checkStartLineNo, endLineNo


def checkBlock(blockKey, filename, lines, rawlines, startLineNo, EndLineNo, ruleCheckKey, Error, cpplines, fileErrorCount):
  ''' 检查区域的代码
  
  Args:
    blockKey:关键字
    filename:文件名
    lines:文件的内容
    rawlines:原始的文件内容
    startLineNo:开始的行数
    EndLineNo:结束的行数
    ruleCheckKey:rule的id
    Error:error的句柄
  '''

  keyName = ''
  #查找class/struct的名称
  m = strcmp.Search(r'(struct|class)\s+(\w+)\b', lines[startLineNo])
  if m:
    if m.group(2) != ' ' and m.group(2) != '{':
      keyName = m.group(2)

  # 匿名的struc不判断
  if keyName == '':
    return

  startLine = lines[startLineNo][lines[startLineNo].find(blockKey) + len(blockKey):]
  i = startLineNo
  while i <= EndLineNo:
    line = lines[i]
    if i == startLineNo:
      line = startLine
    if common.IsBlankLine(line):
      i += 1
      continue

    if strcmp.Search(r'^\s*#\s*define\s+', line):
      i = getDefineMacroEndLineNo(lines, i) + 1
      continue

    if strcmp.Search(r'^\s*#', line):
      i += 1
      continue
  
    if strcmp.Search(r'^(\s*)\bstruct[\s*{;]', line) :
      isBlock, startBlockLineNo, endBlockLineNo = isBlockDeclareCheck(lines, i, 'struct')
      if isBlock and startBlockLineNo != endBlockLineNo:
        checkBlock('struct', filename, lines, rawlines, i, endBlockLineNo, ruleCheckKey, Error, cpplines, fileErrorCount)
        i = endBlockLineNo
        
    elif strcmp.Search(r'^(\s*)\bclass[\s*:{;]', line):
      isClass, startBlockLineNo, endBlockLineNo =common.isClassDeclareCheck(lines, i)
      if isClass:
        checkBlock('class', filename, lines, rawlines, i, endBlockLineNo, ruleCheckKey, Error, cpplines, fileErrorCount)
        i = endBlockLineNo
    else:
      #构造函数的声明或者定义
      pattern = r'\b(' + keyName + ')\s*\('
      m = strcmp.Search(pattern, line)
      if m :
        flg, leftParenthesesLno, rightParenthesesLno, checkStartLineNo, endBlockLineNo = isFunctionDeclare(m.group(1), lines, i)
        if flg > 0 :
          checkInitializerList(i, leftParenthesesLno, filename, lines, ruleCheckKey, Error, cpplines, fileErrorCount)
          i = endBlockLineNo + 1
          continue  
        
    i += 1

def checkInitializerList(defStartLineNo, defEndLineNo, filename, lines, ruleCheckKey, Error, cpplines, fileErrorCount):
  ''' 检查初始化列表的冒号
  
  Args:
    defStartLineNo:声明的开始行
    defEndLineNo:声明的结束行
    filename:文件名
    lines:文件的内容
    ruleCheckKey:rule的id
    Error:error的句柄
  '''
  errorMessage = 'Code Style Rule: There should be a space between the colon ":" and the expression.'
  
  colonLineNo = 0;
  
  line = lines[defStartLineNo];
  line = line.replace('::', ' ')
  if -1 != line.find(':'):
      colonLineNo = defStartLineNo
  i = defStartLineNo + 1    
  while i <= defEndLineNo:
    if common.IsBlankLine(lines[i]):
      i += 1
      continue
    if strcmp.Search(r'^\s*#\s*define\s+', lines[i]):
      i = getDefineMacroEndLineNo(lines, i) + 1
      continue
    if strcmp.Search(r'^\s*#', lines[i]):
      i += 1
      continue
  
    if -1 != lines[i].find(':'):
      colonLineNo = i
    # 拼接声明的字符串
    line += lines[i]

    i += 1

  findIndex = line.find(':')
  if -1 != findIndex:
    findFlg = checkSignLeftRightBlank(line, findIndex - 1, findIndex + 1)
    if not findFlg:
      Error(filename, lines, colonLineNo, ruleCheckKey, 3, errorMessage)
      
      tmp = cpplines[colonLineNo].replace('::', '')
      findIndex = tmp.find(':')
      cpplines[colonLineNo] = cpplines[colonLineNo][0:findIndex] + ' : ' +cpplines[colonLineNo][findIndex + 1:]
      fileErrorCount[0] =  fileErrorCount[0] + 1
  

def CheckCSC030033(filename, file_extension, clean_lines, rawlines, nesting_state, ruleCheckKey, Error, cpplines, fileErrorCount):
  '''类的构造函数的初始化列表中的空格遵循下面的规范:
  ':'和表达式之间必须有空格
  '''
  
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
  
    if strcmp.Search(r'^(\s*)\bstruct[\s*{;]', lines[i]) :
      isBlock, startBlockLineNo, endBlockLineNo = isBlockDeclareCheck(lines, i, 'struct')
      if isBlock and startBlockLineNo != endBlockLineNo:
        checkBlock('struct', filename, lines, rawlines, i, endBlockLineNo, ruleCheckKey, Error, cpplines, fileErrorCount)
        i = endBlockLineNo
    
    elif strcmp.Search(r'^(\s*)\bclass[\s*:{;]', lines[i]):
      isClass, startBlockLineNo, endBlockLineNo =common.isClassDeclareCheck(lines, i)
      if isClass:
        checkBlock('class', filename, lines, rawlines, i, endBlockLineNo, ruleCheckKey, Error, cpplines, fileErrorCount)
        i = endBlockLineNo
      
    else:
      #函数的声明或者定义,不检查
      m = strcmp.Search(r'\b(\w+)::(\w+)\s*\(', lines[i])
      if m and -1 == lines[i][0:m.start()].find("="):
        keyWord = m.group(2)
        flg, leftParenthesesLno, rightParenthesesLno, checkStartLineNo, endBlockLineNo = isFunctionDeclare(keyWord, lines, i)
        if flg > 0 and m.group(1) == m.group(2):
          checkInitializerList(i, leftParenthesesLno, filename, lines, ruleCheckKey, Error, cpplines, fileErrorCount)
          i = endBlockLineNo + 1
          continue  
  
  
    i += 1
  
      