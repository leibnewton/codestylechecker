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

def getDefineMacroEndLineNo(lines, fromLno):
  lengthOfLines = len(lines)
  for i in xrange(fromLno, lengthOfLines):
    if not lines[i].endswith("\\"):
      return i
  return fromLno

def getNextNotNullLineNo(lines, startLno):
  '''从startLno向下查找第一个非空的行
  Args:
    lines:a copy of all lines without strings and comments
    startLno:目标行
  Returns:
           第一个非空的行的行号
  '''
  lengthOfLines = len(lines)
  i = startLno + 1
  while i < lengthOfLines:
    if common.IsBlankLine(lines[i]):
      i += 1
      continue
    elif strcmp.Search(r'^\s*#', lines[i]):
      i = getDefineMacroEndLineNo(lines, i) + 1
      continue
    else:
      break
  if i < lengthOfLines:
    return i
  else:
    return lengthOfLines - 1

def findClassNameWithTheSameName(lines, startLno, functionName):
  '''从startLno向上查找与functionName同名的class
  Args:
    lines:a copy of all lines without strings and comments
    startLno:函数名所在的行
    functionName: 函数名
  Returns:
           class所在的行号（-1:没找到同名的class）
  '''
  i = 0
  while i <= startLno:
    if common.IsBlankLine(lines[i]):
      i += 1
      continue
    elif strcmp.Search(r'^\s*#', lines[i]):
      i = getDefineMacroEndLineNo(lines, i) + 1
      continue
    m = strcmp.Search(r'\bclass\b', lines[i])
    if not m:
      i += 1
      continue
    currentLine = ''
    if lines[i].endswith('\\'):
      currentLine = lines[i][:len(lines[i]) - 1]
    else:
      currentLine = lines[i]
    # 当前行的后一个非空行
    nextLine = lines[getNextNotNullLineNo(lines, i)]
    # 当前行和后一个非空行组成的字符串中能否找到class 单词
    if strcmp.Search(r'\bclass\b\s+\b' + functionName + r'\b', currentLine[m.start():] + nextLine):
      return i
    else:
      i += 1
  return -1

def checkDestructor(lines, checkStartLine, startLno, checkStartIndex):
  '''check ~单词是不是析构函数
  Args:
    lines:a copy of all lines without strings and comments
    checkStartLine:需要check的行
    startLno:需要check的行的行号
    checkStartIndex: ~所在的位置
  Returns:
           0:析构函数,1:不是析构函数, -1:system error
  '''
  lengthOfLines = len(lines)
  # 当前行的后一个非空行
  nextLine = lines[getNextNotNullLineNo(lines, startLno)]
  # 当前行
  checkLine = checkStartLine + nextLine
  m = strcmp.Search(r'^\s*~\s+\b(\w+)\b\s*', checkLine[checkStartIndex:])
  if not m:
    return -1
  # 单词，单词后无括号，说明不是析构函数
  if m.end() == len(checkLine[checkStartIndex:]):
    return 1
  # ~单词，单词后无括号，说明不是析构函数
  if checkLine[checkStartIndex:][m.end()] != '(':
    return 1
  # ~单词  前有class 单词,说明是析构函数
  if strcmp.Search(r'\bclass\b\s+\b' + m.group(1) + r'\b', checkStartLine[:checkStartIndex]):
    return 0
  # 从startLno向上查找与~单词同名的class
  # 找不到，说明是不是析构函数
  if findClassNameWithTheSameName(lines, startLno, m.group(1)) == -1:
    return 1
  # 找到，说明是析构函数
  else:
    return 0

def checkWave(lines, targetLineNo, previousLine):
  '''check “~”后不加空格
  析构函数中的“~”不check(
  class XXX {~XXX();}
  XXX::~XXX()(;|{})
  xxx.~XXX();
  )
  Args:
    lines:a copy of all lines without strings and comments
    targetLineNo:需要check的行的行号
    previousLine: targetLineNo的前一个非空行
  Returns:
           true: “~”后有空格；false:“~”后无空格
  '''
  lengthOfLines = len(lines)
  waveIndex = -1
  endIndex = -1
  checkLine = ''
  if lines[targetLineNo].endswith('\\'):
    checkLine = lines[targetLineNo][:len(lines[targetLineNo]) - 1]
  else:
    checkLine = lines[targetLineNo]
  # ~ 单词是一行的开头时
  m = strcmp.Search(r'^\s*~\s+\w+', checkLine)
  if not m:
    m = strcmp.Search(r'~\s+\w+', checkLine)
    if not m:
      return False
  waveIndex = len(previousLine) + m.start()
  endIndex = len(previousLine) + m.end()
  checkLine = previousLine + checkLine
  while waveIndex > -1:
    # XXX::~ XXX(), xxx.~ XXX, xxx->~ XXX, private:~ XXX ----skip 
    # 析构函数,check next "~ 单词"
    if strcmp.Search(r'(\w|\.|->|::)\s*$', checkLine[:waveIndex]) or \
       strcmp.Search(r'(public|protected|private)\s*:\s*$', checkLine[:waveIndex]):
      m = strcmp.Search(r'~\s+\w+', checkLine[endIndex:])
      if not m:
        return False
      waveIndex = endIndex + m.start()
      endIndex = endIndex + m.end()
    # 如果~前有运算符，说明其一定不是析构函数,报错
    if strcmp.Search(r'[\+\-\*/%\>\<=\&\|\~]\s*$', checkLine[:waveIndex]):
      return True
    checkDestructorResult = checkDestructor(lines, checkLine, targetLineNo, waveIndex)
    if checkDestructorResult == -1:
      return False
    # 不是析构函数,“~”后有空格报错
    elif checkDestructorResult == 1:
      return True
    # 析构函数,check next "~ 单词"
    elif checkDestructorResult == 0:
      m = strcmp.Search(r'~\s+\w+', checkLine[endIndex:])
      if not m:
        return False
      waveIndex = endIndex + m.start()
      endIndex = endIndex + m.end()
  return False


def makeCodeCorrect(searchStr, lines, lineNo, cpplines, fileErrorCount):
    replaceStr = searchStr.replace(' ', '')
    cpplines[lineNo] = cpplines[lineNo].replace(searchStr, replaceStr)
    fileErrorCount[0] =  fileErrorCount[0] + 1


def CheckCSC030019(filename, file_extension, clean_lines, rawlines, nesting_state, ruleCheckKey, Error, cpplines, fileErrorCount):
  '''一元操作符如“!” “~” “++” “--” “&” （地址运算符）等前后不加空格。
             像 “.” “->”这类操作符前后不加空格。
    []的[的前后，]的前面均不加空格。
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
  errMessage = "Code Style Rule: There should be no blank in front of (or behind) the unary operator"
  closeSquareBracketsErrMessage = "Code Style Rule: There should be no blank in front of the unary operator"
  skipEndLineNo = -1
  prevLine = ''
  for i in xrange(clean_lines.NumLines()):
    if i < skipEndLineNo:
      continue
    if common.IsBlankLine(lines[i]):
      continue
    if strcmp.Search(r'^\s*#', lines[i]):
      skipEndLineNo = getDefineMacroEndLineNo(lines, i)
      continue
    # check “~”
    m = strcmp.Search(r'~\s+\w+', lines[i])
    if m:
      if checkWave(lines, i, prevLine):
        Error(filename, lines, i, ruleCheckKey, 3, errMessage + ' "~".')
        makeCodeCorrect(m.group(0), lines, i, cpplines, fileErrorCount)
        
    m = strcmp.Search(r'(!)\s+\w+', lines[i])
    if m:
      Error(filename, lines, i, ruleCheckKey, 3, errMessage + ' "%s".' %m.group(1))
      makeCodeCorrect(m.group(0), lines, i, cpplines, fileErrorCount)
      
    m = strcmp.Search(r'((\b\w+\b)\s+(\+\+|\-\-))', lines[i].replace('return', ''))
    if m:
      Error(filename, lines, i, ruleCheckKey, 3, errMessage + ' "%s".' %m.group(3))
      makeCodeCorrect(m.group(0), lines, i, cpplines, fileErrorCount)
      
    else:
      m = strcmp.Search(r'((\+\+|\-\-)\s+(\b\w+\b))', lines[i])
      if m:
        Error(filename, lines, i, ruleCheckKey, 3, errMessage + ' "%s".' %m.group(2))
        makeCodeCorrect(m.group(0), lines, i, cpplines, fileErrorCount)
        
    m = strcmp.Search(r'(\s*)(\->)(\s*)', lines[i])
    if m:
      if m.group(1) or m.group(3):
        Error(filename, lines, i, ruleCheckKey, 3, errMessage + ' "%s".' %m.group(2))
        makeCodeCorrect(m.group(0), lines, i, cpplines, fileErrorCount)
        
    # 排除以下情况的.,然后check.的前后是否有空格
    # a = 1. /get();
    # b = get()/ .754
    tempLineForCheckPoint = strcmp.Sub(r'\s+\.\d+','',lines[i].replace('...',''))
    tempLineForCheckPoint = strcmp.Sub(r'^\s*\d+\.\s+','',tempLineForCheckPoint)
    tempLineForCheckPoint = strcmp.Sub(r'\W\d+\.\s+','',tempLineForCheckPoint)
    m = strcmp.Search(r'(\s*)(\.)(\s*)', tempLineForCheckPoint)
    if m:
      if m.group(1) or m.group(3):
        Error(filename, lines, i, ruleCheckKey, 3, errMessage + ' "%s".' %m.group(2))
        makeCodeCorrect(m.group(0), lines, i, cpplines, fileErrorCount)
        
    m = strcmp.Search(r'(\s*)(\[)(\s*)', lines[i])
    if m:
      if m.group(1) or m.group(3):
        Error(filename, lines, i, ruleCheckKey, 3, errMessage + ' "%s".' %m.group(2))
        makeCodeCorrect(m.group(0), lines, i, cpplines, fileErrorCount)
        
    m = strcmp.Search(r'(\s*)(\])(\s*)', lines[i])
    if m:
      if m.group(1):
        Error(filename, lines, i, ruleCheckKey, 3, closeSquareBracketsErrMessage + ' "%s".' %m.group(2))
        makeCodeCorrect(m.group(0), lines, i, cpplines, fileErrorCount)
        
    m = strcmp.Search(r'(\+|\-|=|,|%)\s*&\s+\w+', lines[i].replace('/','=').replace('*', '=').replace('(','=').replace('++','').replace('--',''))
    if m:
      Error(filename, lines, i, ruleCheckKey, 3, errMessage + ' "&".')
      makeCodeCorrect(m.group(0), lines, i, cpplines, fileErrorCount)
    # 当前行保存
    if lines[i].endswith('\\'):
      prevLine = lines[i][:len(lines[i]) - 1]
    else:
      prevLine = lines[i]