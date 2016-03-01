#!/usr/bin/python  
#-*- coding: utf-8 -*-
'''
Created on 2014-12-8

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

  #函数的定义
  if closeCurlyBraceQty > 0 and closeParenthesisQty > 0 :
    return 2, leftParenthesesLno, rightParenthesesLno, checkStartLineNo, endLineNo
   

def checkStructBlock(filename, lines, rawlines, startLineNo,EndLineNo, ruleCheckKey, Error, cpplines, fileErrorCount):
  ''' 检查struct区域的代码
  
  Args:
    filename:文件名
    lines:文件的内容
    rawlines:原始的文件内容
    startLineNo:开始的行数
    EndLineNo:结束的行数
    ruleCheckKey:rule的id
    Error:error的句柄
  '''
    
  errorMessage = 'Code Style Rule: Definition of "%s" should follow rules: 1.The left curly brace "{" should be in a separate line. 2.The right curly brace "}" should be followed by ";", and they should be in a separate line. 3.Each member should be in a separate line.'
  
  if lines[startLineNo].strip() != '{':
    Error(filename, lines, startLineNo, ruleCheckKey, 3, errorMessage % 'struct')
    
  if lines[EndLineNo].strip() != '};':
    Error(filename, lines, EndLineNo, ruleCheckKey, 3, errorMessage % 'struct')

  startLine = lines[startLineNo][lines[startLineNo].find('struct') + len('struct'):]
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
  
    if strcmp.Search(r'^(\s*)\bstruct[\s*{;]', line) and lines.count('(') == 0 :
      isBlock, startBlockLineNo, endBlockLineNo = isBlockDeclareCheck(lines, i, 'struct')
      if isBlock and startBlockLineNo != endBlockLineNo:
        checkStructBlock(filename, lines, rawlines, startBlockLineNo, endBlockLineNo, ruleCheckKey, Error, cpplines, fileErrorCount)
        i = endBlockLineNo
    elif strcmp.Search(r'^(\s*)\benum[\s*{;]', line):
      isBlock, startBlockLineNo, endBlockLineNo = isBlockDeclareCheck(lines, i, 'enum')
      if isBlock and startBlockLineNo != endBlockLineNo:
        checkEnumBlock(filename, lines, rawlines, startBlockLineNo, endBlockLineNo, ruleCheckKey, Error, cpplines, fileErrorCount)
        i = endBlockLineNo
    elif strcmp.Search(r'^(\s*)\bunion[\s*{;]', line):
      isBlock, startBlockLineNo, endBlockLineNo = isBlockDeclareCheck(lines, i, 'union')
      if isBlock and startBlockLineNo != endBlockLineNo:
        checkUnionBlock(filename, lines, rawlines, startBlockLineNo, endBlockLineNo, ruleCheckKey, Error, cpplines, fileErrorCount)
        i = endBlockLineNo
    else:
      #函数的声明或者定义,不检查
      m = strcmp.Search(r'\b(\w+)\s*\(', line)
      if m :
        flg, leftParenthesesLno, rightParenthesesLno, checkStartLineNo, endBlockLineNo = isFunctionDeclare(m.group(1), lines, i)
        if flg > 0 :
          i = endBlockLineNo + 1
          continue  
      
      # 每个成员单独占一行
      count = line.count(';')
      if count > 1 :
        Error(filename, lines, i, ruleCheckKey, 3, errorMessage % 'struct')
    i += 1
     
    
def checkEnumBlock(filename, lines, rawlines, startLineNo,EndLineNo, ruleCheckKey, Error, cpplines, fileErrorCount):
  ''' 检查enum区域的代码
  
  Args:
    filename:文件名
    lines:文件的内容
    rawlines:原始的文件内容
    startLineNo:开始的行数
    EndLineNo:结束的行数
    ruleCheckKey:rule的id
    Error:error的句柄
  '''
    
  errorMessage = "Code Style Rule: Definition of \"%s\" should follow rules: 1.The left curly brace \"{\" should be in a separate line. 2.The right curly brace \"}\" should be followed by \";\", and they should be in a separate line. 3.Each member should be in a separate line."
  
  if lines[startLineNo].strip() != '{':
    Error(filename, lines, startLineNo, ruleCheckKey, 3, errorMessage % 'enum')
    
  if lines[EndLineNo].strip() != '};':
    Error(filename, lines, EndLineNo, ruleCheckKey, 3, errorMessage % 'enum')

  startLine = lines[startLineNo][lines[startLineNo].find('enum') + len('enum'):]
  for i in xrange(startLineNo, EndLineNo + 1):
    line = lines[i]
    if i == startLineNo:
      line = startLine
    if common.IsBlankLine(line):
      continue

    if strcmp.Search(r'^\s*#\s*define\s+', line):
      skipEndLno = getDefineMacroEndLineNo(lines, i)
      continue

    if strcmp.Search(r'^\s*#', line):
      continue
  
    # 每个成员单独占一行
    count = line.count(',')
    if count > 1 :
      lineTemp = line
      #例外情况
      #enum NHIF_FUNCTIONID {
      #NHIF_FUNCTIONID_NISYSCTRLHANDLER_FIRST = NH_FUNCTION_ID(NH_DEVICE_ID_SYS, NH_HANDLER_ID_SYSCTRL, 0),
      strarBrackets = lineTemp.find('(')
      evelBrackets = 0
      if -1 != strarBrackets:
        end = len(lineTemp) + 1
        j = strarBrackets
        while j <= end:
          if lineTemp[j:j + 1] == '(':
            evelBrackets += 1
            if evelBrackets == 1:
              strarBrackets = j
          elif lineTemp[j:j + 1] == ')':
            evelBrackets -= 1
            
          if evelBrackets == 0:
            #删除宏定义的括号中间的部分
            lineTemp = lineTemp.replace(lineTemp[strarBrackets : j + 1], '')
            strarBrackets = lineTemp.find('(')
            if -1 != strarBrackets:
              j = strarBrackets
            else :
              break
          elif evelBrackets < 0:
            # 异常
            break
        
          j += 1
        
        if lineTemp.count(',') > 1:
          Error(filename, lines, i, ruleCheckKey, 3, errorMessage % 'enum')
          
      else :
        Error(filename, lines, i, ruleCheckKey, 3, errorMessage % 'enum')
  


def checkUnionBlock(filename, lines, rawlines, startLineNo,EndLineNo, ruleCheckKey, Error, cpplines, fileErrorCount):
  ''' 检查union区域的代码
  
  Args:
    filename:文件名
    lines:文件的内容
    rawlines:原始的文件内容
    startLineNo:开始的行数
    EndLineNo:结束的行数
    ruleCheckKey:rule的id
    Error:error的句柄
  '''
  errorMessage = "Code Style Rule: Definition of \"%s\" should follow rules: 1.The left curly brace \"{\" should be in a separate line. 2.The right curly brace \"}\" should be followed by \";\", and they should be in a separate line. 3.Each member should be in a separate line."
  
  if lines[startLineNo].strip() != '{':
    Error(filename, lines, startLineNo, ruleCheckKey, 3, errorMessage % 'union')
    
  if lines[EndLineNo].strip() != '};':
    Error(filename, lines, EndLineNo, ruleCheckKey, 3, errorMessage % 'union')

  startLine = lines[startLineNo][lines[startLineNo].find('union') + len('union'):]
  for i in xrange(startLineNo, EndLineNo + 1):
    line = lines[i]
    if i == startLineNo:
      line = startLine
    if common.IsBlankLine(line):
      continue

    if strcmp.Search(r'^\s*#\s*define\s+', line):
      skipEndLno = getDefineMacroEndLineNo(lines, i) + 1
      continue

    if strcmp.Search(r'^\s*#', line):
      continue
  
    if strcmp.Search(r'^(\s*)\bstruct[\s*{;]', line) and lines.count('(') == 0 :
      isBlock, startBlockLineNo, endBlockLineNo = isBlockDeclareCheck(lines, i, 'struct')
      if isBlock and startBlockLineNo != endBlockLineNo:
        checkStructBlock(filename, lines, rawlines, startBlockLineNo, endBlockLineNo, ruleCheckKey, Error, cpplines, fileErrorCount)
        i = endBlockLineNo
    elif strcmp.Search(r'^(\s*)\benum[\s*{;]', line):
      isBlock, startBlockLineNo, endBlockLineNo = isBlockDeclareCheck(lines, i, 'enum')
      if isBlock and startBlockLineNo != endBlockLineNo:
        checkEnumBlock(filename, lines, rawlines, startBlockLineNo, endBlockLineNo, ruleCheckKey, Error, cpplines, fileErrorCount)
        i = endBlockLineNo
    else:
      # 每个成员单独占一行
      count = line.count(';')
      if count > 1 :
        Error(filename, lines, i, ruleCheckKey, 3, errorMessage % 'union')
        


def checkClassBlock(filename, lines, rawlines, startLineNo,EndLineNo, ruleCheckKey, Error, cpplines, fileErrorCount):
  ''' 检查class区域的代码
  
  Args:
    filename:文件名
    lines:文件的内容
    rawlines:原始的文件内容
    startLineNo:开始的行数
    EndLineNo:结束的行数
    ruleCheckKey:rule的id
    Error:error的句柄
  '''
    
  errorMessage = "Code Style Rule: Definition of \"%s\" should follow rules: 1.The left curly brace \"{\" should be in a separate line. 2.The right curly brace \"}\" should be followed by \";\", and they should be in a separate line. 3.Each member should be in a separate line."
  
  if lines[startLineNo].strip() != '{':
    Error(filename, lines, startLineNo, ruleCheckKey, 3, errorMessage % 'class')
    
  if lines[EndLineNo].strip() != '};':
    Error(filename, lines, EndLineNo, ruleCheckKey, 3, errorMessage % 'class')

  startLine = lines[startLineNo][lines[startLineNo].find('class') + len('class'):]
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
    
    if strcmp.Search(r'^(\s*)\bstruct[\s*{;]', line) and lines.count('(') == 0 :
      isBlock, startBlockLineNo, endBlockLineNo = isBlockDeclareCheck(lines, i, 'struct')
      if isBlock and startBlockLineNo != endBlockLineNo:
        checkStructBlock(filename, lines, rawlines, startBlockLineNo, endBlockLineNo, ruleCheckKey, Error, cpplines, fileErrorCount)
        i = endBlockLineNo
    elif strcmp.Search(r'^(\s*)\benum[\s*{;]', line):
      isBlock, startBlockLineNo, endBlockLineNo = isBlockDeclareCheck(lines, i, 'enum')
      if isBlock and startBlockLineNo != endBlockLineNo:
        checkEnumBlock(filename, lines, rawlines, startBlockLineNo, endBlockLineNo, ruleCheckKey, Error, cpplines, fileErrorCount)
        i = endBlockLineNo
    elif strcmp.Search(r'^(\s*)\bunion[\s*:{;]', line):
      isBlock, startBlockLineNo, endBlockLineNo = isBlockDeclareCheck(lines, i, 'union')
      if isBlock and startBlockLineNo != endBlockLineNo:
        checkUnionBlock(filename, lines, rawlines, startBlockLineNo, endBlockLineNo, ruleCheckKey, Error, cpplines, fileErrorCount)
        i = endBlockLineNo
    else:
      #函数的声明或者定义,不检查
      m = strcmp.Search(r'\b(\w+)\s*\(', line)
      if m :
        flg, leftParenthesesLno, rightParenthesesLno, checkStartLineNo, endBlockLineNo = isFunctionDeclare(m.group(1), lines, i)
        if flg > 0 :
          i = endBlockLineNo + 1
          continue
      
      # 每个成员单独占一行
      count = line.count(';')
      if count > 1 :
        Error(filename, lines, i, ruleCheckKey, 3, errorMessage % 'class')

    i += 1


def CheckCSC020011(filename, file_extension, clean_lines, rawlines, nesting_state, ruleCheckKey, Error, cpplines, fileErrorCount):
  '''像struct，enum，union，class等含有成员的定义，需要遵循下面的规范：
   {单独占一行
   }和;写在一起，并单独占一行
      每个成员单独占一行
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

    if strcmp.Search(r'^(\s*)\bstruct[\s*{;]', lines[i]) and lines[i].count('(') == 0 :
      isBlock, startBlockLineNo, endBlockLineNo = isBlockDeclareCheck(lines, i, 'struct')
      if isBlock and startBlockLineNo != endBlockLineNo:
        checkStructBlock(filename, lines, rawlines, startBlockLineNo, endBlockLineNo, ruleCheckKey, Error, cpplines, fileErrorCount)
        i = endBlockLineNo

    elif strcmp.Search(r'^(\s*)\benum[\s*{;]', lines[i]) :
      isBlock, startBlockLineNo, endBlockLineNo = isBlockDeclareCheck(lines, i, 'enum')
      if isBlock and startBlockLineNo != endBlockLineNo:
        checkEnumBlock(filename, lines, rawlines, startBlockLineNo, endBlockLineNo, ruleCheckKey, Error, cpplines, fileErrorCount)
        i = endBlockLineNo
      
    elif strcmp.Search(r'^(\s*)\bunion[\s*{;]', lines[i]):
      isBlock, startBlockLineNo, endBlockLineNo = isBlockDeclareCheck(lines, i, 'union')
      if isBlock and startBlockLineNo != endBlockLineNo:
        checkUnionBlock(filename, lines, rawlines, startBlockLineNo, endBlockLineNo, ruleCheckKey, Error, cpplines, fileErrorCount)
        i = endBlockLineNo
      
    elif strcmp.Search(r'^(\s*)\bclass[\s*:{;]', lines[i]):
      isClass, startBlockLineNo, endBlockLineNo =common.isClassDeclareCheck(lines, i)
      if isClass:
        checkClassBlock(filename, lines, rawlines, startBlockLineNo, endBlockLineNo, ruleCheckKey, Error, cpplines, fileErrorCount)
        i = endBlockLineNo
    
    i += 1