#!/usr/bin/python  
#-*- coding: utf-8 -*-
'''
Created on 2014-12-29
namespace的定义，需要遵循下面的规范。
[例外]如果有多重namespace的嵌套，为了避免过多缩进，嵌套的namespace不用缩进。
@author: zhangran
'''
import os
import sys
syspath = os.path.dirname(os.path.dirname(__file__))
if not os.path.join(syspath, "tools") in sys.path:
  sys.path.append(os.path.join(syspath, "tools"))
import CopyRightContents
import common
strcmp = common.StringCompareInfo()

def getDefineMacroEndLineNo(lines, fromLno):
  lengthOfLines = len(lines)
  for i in xrange(fromLno, lengthOfLines):
    if not lines[i].endswith("\\"):
      return i
  return fromLno

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


def getNamespaceBlock(lines, startLineNo, EndLineNo):
  ''' 检查namespace区域的代码
  
  Args:
    lines:文件的内容
    startLineNo:开始的行数
    
  Returns:
    Boolean: 是否正确
    integer: 起始行 
    integer: 结束行.
  '''

  openCurlyBraceQty = 0
  closeCurlyBraceQty = 0
  checkStartLineNo = -1
  checkEndLineNo = -1
  
  line = ''
  startLine = lines[startLineNo][lines[startLineNo].find('namespace') + len('namespace'):]
  
  i = startLineNo
  while i <= EndLineNo:
    line = lines[i]
    if i == startLineNo:
      line = startLine
    if common.IsBlankLine(line):
      i += 1
      continue
    if strcmp.Search(r'^\s*#', line):
      i += 1
      continue

    if strcmp.Search(r'^\s*#\s*define\s+', line):
      i = getDefineMacroEndLineNo(lines, i)
      continue

    checkEndLineNo = i
    
    openCurlyBraceQty = openCurlyBraceQty + line.count('{')
    closeCurlyBraceQty = closeCurlyBraceQty + line.count('}')
    
    if openCurlyBraceQty > 0 and checkStartLineNo == -1:
      checkStartLineNo = i

    #namespace的定义
    if openCurlyBraceQty == closeCurlyBraceQty and closeCurlyBraceQty > 0:
      break
  
    i += 1
    
    #统计的左右大括号数量不一致，说明代码有问题，不check，返回错误
  if openCurlyBraceQty != closeCurlyBraceQty:
    return False, checkStartLineNo, checkEndLineNo
  
  return True, checkStartLineNo, checkEndLineNo

def CheckCSC020014(filename, file_extension, clean_lines, rawlines, nesting_state, ruleCheckKey, Error, cpplines, fileErrorCount):
  ''' namespace的定义，需要遵循下面的规范。
  
  [例外]如果有多重namespace的嵌套，为了避免过多缩进，嵌套的namespace不用缩进。
  
  Args:
    filename:文件名
    lines:文件的内容
    rawlines:原始的文件内容
    noteStartLineNo:注释说明开始的行数
    noteEndLineNo:注释说明结束的行数
    ruleCheckKey:rule的id
    Error:error的句柄
  '''
      
  errorMessage = 'Code Style Rule: Nested namespace does not need to indent.'
 
  lines = clean_lines.elided
  
  i = 0
  while i < len(lines):
    if common.IsBlankLine(lines[i]):
      i += 1
      continue
    if strcmp.Search(r'^\s*#\s*define\s+', lines[i]):
      i = getDefineMacroEndLineNo(lines, i) + 1
      continue
    if strcmp.Search(r'^\s*#', lines[i]):
      i += 1
      continue

    #check struct,union,enum
    m = strcmp.Search(r'\bnamespace[\s:;{]', lines[i])
    # 只判断namespace的定义
    if m and -1 == lines[i].find('using'):
      ret, checkStartLineNo, checkEndLineNo = getNamespaceBlock(lines, i, len(lines) - 1 )
      if ret:
        for j in xrange(checkStartLineNo, checkEndLineNo + 1):
          m = strcmp.Search(r'\bnamespace[\s:;{]', lines[j])
          if m and -1 == lines[j].find('using'):
            indentCharactorQtyOrgin = len(lines[j].replace('\t','    '))
            indentCharactorQtyStrip = len(lines[j].replace('\t','    ').lstrip())
            if indentCharactorQtyOrgin != indentCharactorQtyStrip:
              Error(filename, lines, j, ruleCheckKey, 3, errorMessage)
              
              cpplines[j] = cpplines[j].lstrip()
              fileErrorCount[0] =  fileErrorCount[0] + 1
            
        i = checkEndLineNo + 1
        continue
    
    
    i += 1
      