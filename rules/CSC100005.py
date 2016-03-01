#!/usr/bin/python  
#-*- coding: utf-8 -*-
'''
Created on 2014-2-11
rule:类定义中，请遵循以下排列规律：
     public在前，protected其次，private最后
@author: wangxc
'''
import os
import sys
syspath = os.path.dirname(os.path.dirname(__file__))
if not os.path.join(syspath, "tools") in sys.path:
  sys.path.append(os.path.join(syspath, "tools"))
import common
strcmp = common.StringCompareInfo()

def getTemplateEndLno(lines, startLno):
  #查找template<...>中>所在的行
  lengthOfLines = len(lines)
  leftAngleBracketQty = 0
  rightAngleBracketQty = 0
  for i in xrange(startLno, lengthOfLines):
    if common.IsBlankLine(lines[i]):
      continue
    if strcmp.Search(r'^\s*#', lines[i]):
      continue
    leftAngleBracketQty = leftAngleBracketQty + lines[i].count('<')
    rightAngleBracketQty = rightAngleBracketQty + lines[i].count('>') - lines[i].count('->')
    if leftAngleBracketQty == rightAngleBracketQty:
      return i
  return -1

def isFunctionDeclare(typeWord, lines, startLno):
  # 从当前行开始累计左右大括号数目，当数目相同时找到以分号结尾的行的行号
  openCurlyBraceQty = 0
  closeCurlyBraceQty = 0
  lengthOfLines = len(lines)
  index = lines[startLno].find(typeWord)
  line = lines[startLno][index:]
  for i in xrange(startLno, lengthOfLines):
    if common.IsBlankLine(lines[i]):
      continue
    if strcmp.Search(r'^\s*#', lines[i]):
      continue
    if i != startLno:
      line += lines[i]
      openCurlyBraceQty = openCurlyBraceQty + lines[i].count('{')
      closeCurlyBraceQty = closeCurlyBraceQty + lines[i].count('}')
    else:
      openCurlyBraceQty = openCurlyBraceQty + line.count('{')
      closeCurlyBraceQty = closeCurlyBraceQty + line.count('}')
    if openCurlyBraceQty == closeCurlyBraceQty and lines[i].rstrip().endswith(';'):
      break
  openParenthesisIndex = line.find('(')
  # 没有圆括号，说明不是函数
  if openParenthesisIndex == -1:
    return False
  # 圆括号前有大括号，说明不是函数
  if line[0:openParenthesisIndex].find('{') > -1:
    return False
  # 圆括号前有逗号，说明不是函数
  if line[0:openParenthesisIndex].find(',') > -1:
    return False
  if line[0:openParenthesisIndex].find('=') > -1:
    if line[0:openParenthesisIndex].find('operator') > -1:
      #操作符重载时，说明是函数
      return True
    #圆括号前有等号，说明不是函数
    return False
  return True

def checkClassBlock(filename, lines, startLineNo, startLine, endLineNo, ruleCheckKey, Error, cpplines, fileErrorCount):
  #check 类定义
  currentAccess = 'default'
  acessList = []
  i = startLineNo
  errorMessage = 'Code Style Rule: In Class definitions, please put the access specifiers in the following order: first "public", second "protected", and finally "private".'
  skipEndLno = -1
  line = ''
  openCurlyBraceQty = 0
  closeCurlyBraceQty = 0
  tempOpenCurlyBraceQty = 0
  tempCloseCurlyBraceQty = 0
  while i <= endLineNo:
    line = lines[i]
    #空白行--skip
    if common.IsBlankLine(line):
      i += 1
      continue
    #宏定义--skip
    if strcmp.Search(r'^\s*#\s*define\s+', line):
      i = common.getDefineMacroEndLineNo(lines, i) + 1
      continue
    #预定义--skip
    if strcmp.Search(r'^\s*#', line):
      i += 1
      continue
    #template<...> -- skip
    if strcmp.Search(r'^\s*template\s*<', lines[i]):
      i = getTemplateEndLno(lines, i)
      if i == -1:
        break
      else:
        i += 1
      continue
    tempOpenCurlyBraceQty = openCurlyBraceQty
    tempCloseCurlyBraceQty = closeCurlyBraceQty
    openCurlyBraceQty = openCurlyBraceQty + line.count('{')
    closeCurlyBraceQty = closeCurlyBraceQty + line.count('}')
    if i == startLineNo:
      #startLineNo是class第一个左大括号所在的行
      line = startLine[startLine.find('{') + 1:]
    m = strcmp.Search(r'^\s*(\bpublic\b|\bprivate\b|\bprotected\b)\s*:', line)
    if m:
      line = line[line.find(':') + 1:]
      currentAccess = m.group(1)
      # check是否满足public,protected,private这样的顺序
      if currentAccess == 'public':
        if 'protected' in acessList or 'private' in acessList:
          Error(filename, lines, i, ruleCheckKey, 3, errorMessage)
          break
      elif currentAccess == 'protected':
        if 'private' in acessList:
          Error(filename, lines, i, ruleCheckKey, 3, errorMessage)
          break
      acessList.append(currentAccess)
    # check当前行是否是内部类
    if strcmp.Search(r'^\s*\bclass\b', line.replace('{', '')):
      if isFunctionDeclare('class', lines, i):
        # class a function();
        # 当前行是返回值为class的函数--skip
        i += 1
        continue
      #判断是否是类定义
      isClassDeclare,nestStartLineNo,nestEndLineNo = common.isClassDeclareCheck(lines, i)
      #当class的类定义中，所有的代码都是在同一行时,没必要check
      if nestStartLineNo == nestEndLineNo:
        i = nestEndLineNo + 1
        continue
      # check 内部类
      if isClassDeclare:
        if i == nestStartLineNo:
          nestStartLine = line[line.find('class'):]
        else:
          nestStartLine = lines[nestStartLineNo]
        checkClassBlock(filename, lines, nestStartLineNo, nestStartLine, nestEndLineNo, ruleCheckKey, Error, cpplines, fileErrorCount)
      i = nestEndLineNo + 1
      continue
    i += 1

def CheckCSC100005(filename, file_extension, clean_lines, rawlines, nesting_state, ruleCheckKey, Error, cpplines, fileErrorCount):
  lines = clean_lines.elided
  i = 0
  isClassDeclare = False
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
      i += 1
      continue
    #template<...> -- skip
    if strcmp.Search(r'^\s*template\s*<', lines[i]):
      i = getTemplateEndLno(lines, i)
      if i == -1:
        break
      else:
        i += 1
      continue
    #行是以"几个空格+class"或者"class"开头时，check class
    if strcmp.Search(r'^(\s*)\bclass\b', lines[i]):
      #判断该段代码是否以class为返回值的函数
      if isFunctionDeclare('class', lines, i):
        i += 1
        continue
      #判断是否是类定义
      isClassDeclare,startLineNo,endLineNo = common.isClassDeclareCheck(lines, i)
      #当class的类定义中，所有的代码都是在同一行时,没必要check
      if startLineNo == endLineNo:
        i = endLineNo + 1
        continue
      #check 类定义
      if isClassDeclare:
        checkClassBlock(filename, lines, startLineNo, lines[startLineNo], endLineNo, ruleCheckKey, Error, cpplines, fileErrorCount)
      i = endLineNo
    i += 1
  
      