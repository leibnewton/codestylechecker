#!/usr/bin/python  
#-*- coding: utf-8 -*-
'''
Created on 2014-6-10

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

def checkSwitchOpenCurlyBraceInOneLine(lines, startLineNo):
  openParenthesisQty = 0
  closeParenthesisQty = 0
  i = startLineNo
  isInSameLine = True
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
    openParenthesisQty = openParenthesisQty + lines[i].count('(')
    closeParenthesisQty = closeParenthesisQty + lines[i].count(')')
    if openParenthesisQty == closeParenthesisQty and openParenthesisQty > 0:
      if lines[i].find('{') == -1:
        isInSameLine = False
      return i, isInSameLine
    i += 1
  return startLineNo, isInSameLine

def getSwitchBlockEndLineNo(lines, startLineNo):
  openCurlyBraceQty = 0
  closeCurlyBraceQty = 0
  lengthOfLines = len(lines)
  skipEndLno = -1
  for i in xrange(startLineNo, lengthOfLines):
    if common.IsBlankLine(lines[i]):
      continue
    if i <= skipEndLno:
      continue
    if strcmp.Search(r'^\s*#\s*define\s+', lines[i]):
      skipEndLno = getDefineMacroEndLineNo(lines, i)
      continue
    if strcmp.Search(r'^\s*#', lines[i]):
      continue
    openCurlyBraceQty = openCurlyBraceQty + lines[i].count('{')
    closeCurlyBraceQty = closeCurlyBraceQty + lines[i].count('}')
    if openCurlyBraceQty == closeCurlyBraceQty and openCurlyBraceQty > 0:
      return i
  return -1


def checkCaseBlock(filename, lines, rawlines, startLineNo,EndLineNo, ruleCheckKey, Error, cpplines, fileErrorCount):

  i = startLineNo

  while i <= EndLineNo:
    if common.IsBlankLine(lines[i]):
      i += 1
      continue
    if strcmp.Search(r'^\s*#\s*define\s+', lines[i]):
      i = getDefineMacroEndLineNo(lines, i) + 1
      continue
    if strcmp.Search(r'^\s*#', lines[i]):
      i += 1
      continue
   
    if strcmp.Search(r'^(\s*)\bswitch\b', lines[i]):
      i = checkSwitchBlock(filename, lines, rawlines, i, ruleCheckKey, Error, cpplines, fileErrorCount)
      if -1 == i:
        return -1
      i += 1
      continue
  
    # 返回case的结束
    if strcmp.Search(r'^(\s*)((\bcase\b)|(\bdefault\b))', lines[i]) and i > startLineNo:
      return i - 1
    
    i += 1
    
  return EndLineNo -1

def checkDefaultBlock(filename, lines, rawlines, startLineNo,EndLineNo, ruleCheckKey, Error, cpplines, fileErrorCount):

  i = startLineNo

  while i <= EndLineNo:
    if common.IsBlankLine(lines[i]):
      i += 1
      continue
    if strcmp.Search(r'^\s*#\s*define\s+', lines[i]):
      i = getDefineMacroEndLineNo(lines, i) + 1
      continue
    if strcmp.Search(r'^\s*#', lines[i]):
      i += 1
      continue
   
    if strcmp.Search(r'^(\s*)\bswitch\b', lines[i]):
      i = checkSwitchBlock(filename, lines, rawlines, i, ruleCheckKey, Error, cpplines, fileErrorCount)
      if -1 == i:
        return -1
      i += 1
      continue
    
    i += 1

def checkSwitchBlock(filename, lines, rawlines, startLineNo, ruleCheckKey, Error, cpplines, fileErrorCount):

  hasDefault = False
  i = startLineNo

  # get qty of  Switch indent charactor
  m = strcmp.Search(r'^(\s*)\bswitch\b', lines[startLineNo])
  indentCharactorQtyOfSwitch = len(m.group(1).replace('\t','    '))
  # get switch block end line no
  i,isInSameLine = checkSwitchOpenCurlyBraceInOneLine(lines, startLineNo)
  if i == -1:
    return len(lines)
  switchEndLineNo = getSwitchBlockEndLineNo(lines, i)
  
  if switchEndLineNo == -1:
    return -1
  # error message
  errorMessage = "Code Style Rule: There should be a default in every switch statement."
  # check
  while i <= switchEndLineNo:
    if common.IsBlankLine(lines[i]):
      i += 1
      continue
    if strcmp.Search(r'^\s*#\s*define\s+', lines[i]):
      i = getDefineMacroEndLineNo(lines, i) + 1
      continue
    if strcmp.Search(r'^\s*#', lines[i]):
      i += 1
      continue
    m =  strcmp.Search(r'^(\s*)((\bcase\b)|(\bdefault\b))', lines[i])
    if m:
        
      checkEndLineNo = 0
      
      if m.group(2) == 'case':
        i = checkCaseBlock(filename, lines, rawlines, i, switchEndLineNo, ruleCheckKey, Error, cpplines, fileErrorCount)
      else :
        checkDefaultBlock(filename, lines, rawlines, i, switchEndLineNo, ruleCheckKey, Error, cpplines, fileErrorCount)
        hasDefault = True  
        i = switchEndLineNo 
      
    i += 1

  if not hasDefault:
    Error(filename, lines, startLineNo, ruleCheckKey, 3, errorMessage)

  return i - 1
      
      

def CheckCSC080014(filename, file_extension, clean_lines, rawlines, nesting_state, ruleCheckKey, Error, cpplines, fileErrorCount):
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
    if strcmp.Search(r'^(\s*)\bswitch\b', lines[i]):
      i = checkSwitchBlock(filename, lines, rawlines, i, ruleCheckKey, Error, cpplines, fileErrorCount)
      if -1 == i:
        return -1
    i += 1
  
      