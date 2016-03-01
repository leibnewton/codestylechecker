#!/usr/bin/python  
#-*- coding: utf-8 -*-
'''
Created on 2014-2-11
rule:struct，union，enum，class类型定义后应该用空行隔开
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

def checkStructEnumUnionDeclare(typeWord, lines, startLno):
  lengthOfLines = len(lines)
  index = lines[startLno].find(typeWord)
  line = lines[startLno][index:]
  endlno = -1
  openCurlyBraceQty = 0
  closeCurlyBraceQty = 0
  declareLastCloseBraceLno = -1
  for i in xrange(startLno, lengthOfLines):
    endlno = i
    if common.IsBlankLine(lines[i]):
      line += ' \n'
      continue
    if strcmp.Search(r'^\s*#', lines[i]):
      line += ' \n'
      continue
    tempLine = lines[i]
    if i == startLno:
      line += ' \n'
    else:
      line += tempLine + ' \n'
    openCurlyBraceQty = openCurlyBraceQty + tempLine.count('{')
    closeCurlyBraceQty = closeCurlyBraceQty + tempLine.count('}')
    if openCurlyBraceQty == closeCurlyBraceQty and tempLine.rstrip().endswith(';'):
      break
  templine = line.replace('\n',' ')
  m = strcmp.Search(r'^' + typeWord + r'\s*(\w*)\s*{+', templine.replace('::',''))
  if m:
    if openCurlyBraceQty != closeCurlyBraceQty:
      return True,endlno,False
    return True,endlno,True
  else:
    return False,-1,True

def CheckCSC030005(filename, file_extension, clean_lines, rawlines, nesting_state, ruleCheckKey, Error, cpplines, fileErrorCount):
  #列表clean_lines.elided的内容为['comment',codeLine1,codeLine2,...codeLineN,'comment']
  #codeLineN在clean_lines.elided的index为clean_lines.NumLines()-1
  lines = clean_lines.elided
  errorMessage = 'Code Style Rule: There should be a blank line after the definition of a struct/union/enum/class.'
  i = 0
  endLineNo = clean_lines.NumLines()
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
    #template<...> -- skip
    if strcmp.Search(r'^\s*template\s*<', lines[i]):
      i = getTemplateEndLno(lines, i)
      if i == -1:
        break
      else:
        i += 1
      continue
    #check class
    if strcmp.Search(r'\bclass\b', lines[i]):
      #判断该段代码是否以class为返回值的函数
      if isFunctionDeclare('class', lines, i):
        i += 1
        continue
      #判断是否是类定义
      isClassDeclare,startLineNo,endLineNo = common.isClassDeclareCheck(lines, i)
      if isClassDeclare:
        #如果class定义的最后一行同时是文件的最后一行(请参看lines = clean_lines.elided的注释)时，退出循环，不check了
        if endLineNo >= clean_lines.NumLines() - 2:
          break
        #  下一行只有} or };,skip
        if not common.IsBlankLine(lines[endLineNo + 1]) and lines[endLineNo + 1].strip().replace(' ','') in ['}', '};']:
          i = startLineNo + 1
          continue
        #如果class定义的最后一行的下一行不是空白行 ，报错
        if not common.IsBlankLine(rawlines[endLineNo + 1]):
          Error(filename, lines, endLineNo, ruleCheckKey, 3, errorMessage)
        i = startLineNo + 1
        continue
    #check struct,union,enum
    m = strcmp.Search(r'(\bstruct\b|\bunion\b|\benum\b)', lines[i])
    if m:
      #判断该段代码是否以struct/union/enum为返回值的函数
      if isFunctionDeclare(m.group(1), lines, i):
        i += 1
        continue
      #判断是否是结构体/联合/枚举定义
      isStructUnionEnumDeclare,endLineNo,canFindEndLine = checkStructEnumUnionDeclare(m.group(1), lines, i)
      if isStructUnionEnumDeclare:
        #如果代码不规范而导致无法找到结构体/联合/枚举定义的最后一行，退出循环
        if not canFindEndLine:
          break
        #如果结构体/联合/枚举定义的最后一行同时是文件的最后一行(请参看lines = clean_lines.elided的注释)时，退出循环，不check了
        if endLineNo >= clean_lines.NumLines() - 2:
          break
        #  下一行只有} or };,skip
        if not common.IsBlankLine(lines[endLineNo + 1]) and lines[endLineNo + 1].strip().replace(' ','') in ['}', '};']:
          i = endLineNo + 1
          continue
        #如果结构体/联合/枚举定义的最后一行的下一行不是空白行 且 下一行不是只有}，报错
        if not common.IsBlankLine(rawlines[endLineNo + 1]) and rawlines[endLineNo + 1].strip().replace(' ','') not in ['}', '};']:
          Error(filename, lines, endLineNo, ruleCheckKey, 3, errorMessage)
        i = endLineNo + 1
        continue
    i += 1
  
      