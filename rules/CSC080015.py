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

def getCaseCloseParenthesisLine(lines, startLineNo):
  checkStartLno = -1
  lengthOfLines = len(lines)
  casewordIndex = lines[startLineNo].find('case')
  openParenthesisQty = 0
  closeParenthesisQty = 0
  closeParenthesisEndLine = ''
  templine = ''
  for i in xrange(startLineNo, lengthOfLines):
    checkStartLno = i
    if common.IsBlankLine(lines[i]):
      continue
    if strcmp.Search(r'^\s*#', lines[i]):
      continue
    if i == startLineNo:
      line = lines[i][casewordIndex:]
    else:
      line = lines[i]
    templine += line
    openParenthesisQtyTemp = 0
    closeParenthesisQtyTemp = 0
    parenthesisList = strcmp.FindAll(r'\(|\)', lines[i])
    for parenthesisListItem in parenthesisList:
      if parenthesisListItem == '(':
        openParenthesisQtyTemp = openParenthesisQtyTemp + 1
        openParenthesisQty = openParenthesisQty + 1
      else:
        closeParenthesisQtyTemp = closeParenthesisQtyTemp + 1
        closeParenthesisQty = closeParenthesisQty + 1
      if openParenthesisQty == closeParenthesisQty:
        break
    if openParenthesisQty == closeParenthesisQty and strcmp.Search(r'^case.+:', templine.replace('::', '')):
      tempArrayBysplitLine = lines[i].split(')')
      closeParenthesisEndLine = ' '.join(tempArrayBysplitLine[closeParenthesisQtyTemp:])
      break
  closeParenthesisEndLine = closeParenthesisEndLine[closeParenthesisEndLine.replace('::', '  ').find(':'):]
  return checkStartLno, closeParenthesisEndLine

#startLineNo 实际实际代码的最后一行
def checkBreakError(lines, rawlines, startLineNo, endLineNo, hasBreak, hasStatementLine):
  if hasBreak:
    return False
  if not hasStatementLine:
    return False
  hasError = True
  i = startLineNo
  while i <= endLineNo:
    if common.IsBlankLine(rawlines[i]):
      i += 1
      continue
    if strcmp.Search(r'^\s*#\s*define\s+', lines[i]):
      i = getDefineMacroEndLineNo(lines, i) + 1
      continue
    if strcmp.Search(r'^\s*#', lines[i]):
      i += 1
      continue
    # 实际实际代码的最后一行后有注释行，则非空。
    if not common.IsBlankLine(rawlines[i].replace(':','').replace('{','').replace('}','').replace(';','')):
       hasError = False
       break
    i += 1
  return hasError

def checkGotoReturnError(lines, rawlines, caseStartLineNo, laseStatementLineNo, gotoReturnLineNo, hasStatement):
  checkStartLineNo = -1
  if rawlines[gotoReturnLineNo].find('//') > -1 or rawlines[gotoReturnLineNo].find('/*') > -1:
    return False
  if caseStartLineNo == gotoReturnLineNo:
    if rawlines[gotoReturnLineNo].find('//') == -1 and rawlines[gotoReturnLineNo].find('/*') == -1:
      return True
    else:
      return False
  if hasStatement:
    checkStartLineNo = laseStatementLineNo + 1
    if laseStatementLineNo == gotoReturnLineNo:
      if rawlines[gotoReturnLineNo].find('//') == -1 and rawlines[gotoReturnLineNo].find('/*') == -1:
        return True
      else:
        return False
  else:
    if rawlines[caseStartLineNo].find('//') > -1 or rawlines[caseStartLineNo].find('/*') > -1:
      return False
    checkStartLineNo = caseStartLineNo + 1
  hasError = True
  i = checkStartLineNo
  while i < gotoReturnLineNo:
    if common.IsBlankLine(rawlines[i]):
      i += 1
      continue
    if strcmp.Search(r'^\s*#\s*define\s+', lines[i]):
      i = getDefineMacroEndLineNo(lines, i) + 1
      continue
    if strcmp.Search(r'^\s*#', lines[i]):
      i += 1
      continue
    if not common.IsBlankLine(rawlines[i].replace(':','').replace('{','').replace('}','').replace(';','')):
       hasError = False
       break
    i += 1
  return hasError

def checkCaseBlock(filename, lines, rawlines, startLineNo,EndLineNo, ruleCheckKey, Error, cpplines, fileErrorCount):
  checkStartLineNo,checkStartLine = getCaseCloseParenthesisLine(lines, startLineNo)
  hasBreak = False
  hasGotoReturn = False
  hasStatement = False
  hasStatementForReturn = False
  hasError = False
  hasGotoReturnError = False
  i = checkStartLineNo
  gotoReturnLineNo = -1
  statementEndLineNo = checkStartLineNo
  statementEndLineNoForReturn = checkStartLineNo
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
    if i == checkStartLineNo:
      line = checkStartLine.replace('{','').replace('}','').replace(';','').replace(':',' ')
    else:
      line = lines[i].replace('{','').replace('}','').replace(';','').replace(':',' ')
    if strcmp.Search(r'^(\s*)\bswitch\b', line):
      if i == checkStartLineNo or i == EndLineNo:
        return True,EndLineNo,hasError,hasGotoReturnError
      i = checkSwitchBlock(filename, lines, rawlines, i, ruleCheckKey, Error, cpplines, fileErrorCount)
      if -1 == i:
        return -1
      i += 1
      continue
    if strcmp.Search(r'^(\s*)((\bcase\b)|(\bdefault\b))', line):
      if i == checkStartLineNo or i == EndLineNo:
        return True,EndLineNo,hasError,hasGotoReturnError
      break
    elif i == EndLineNo:
      break
    else:
      if strcmp.Search(r'\bbreak\b', line):
        hasBreak = True
      elif not common.IsBlankLine(line):
        hasStatement = True
        statementEndLineNo = i
      if strcmp.Search(r'(\bgoto\b|\breturn\b|\bexit\b)', line):
        mm = strcmp.Search(r'(\bgoto\b|\breturn\b|\bexit\b)', line)
        if not common.IsBlankLine(line[0:line.find(mm.group(1))]):
          hasStatementForReturn = True
          statementEndLineNoForReturn = i
        hasGotoReturn = True
        gotoReturnLineNo = i
        if not hasGotoReturnError:
          hasGotoReturnError = checkGotoReturnError(lines, rawlines, checkStartLineNo, statementEndLineNoForReturn, gotoReturnLineNo, hasStatementForReturn)
      elif not common.IsBlankLine(line):
        hasStatementForReturn = True
        statementEndLineNoForReturn = i
    i += 1
  caseEndLineNo = i - 1
  if hasGotoReturn:
    hasError = False
  else:
    hasError = checkBreakError(lines, rawlines, statementEndLineNo + 1, caseEndLineNo, hasBreak, hasStatement)
  return False,caseEndLineNo,hasError,hasGotoReturnError

def checkDefaultBlock(filename, lines, rawlines, startLineNo,EndLineNo, ruleCheckKey, Error, cpplines, fileErrorCount):
  hasBreak = False
  hasGotoReturn = False
  hasStatement = False
  hasStatementForReturn = False
  hasError = False
  hasGotoReturnError = False
  i = startLineNo
  gotoReturnLineNo = -1
  statementEndLineNo = startLineNo
  statementEndLineNoForReturn = startLineNo
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
    if i == startLineNo:
      line = lines[i].replace('{','').replace('}','').replace(';','').replace(':',' ')
    else:
      line = lines[i].replace('{','').replace('}','').replace(';','').replace(':',' ')
    if strcmp.Search(r'^(\s*)\bswitch\b', line):
      if i == startLineNo or i == EndLineNo:
        return True,EndLineNo,hasError,hasGotoReturnError
      i = checkSwitchBlock(filename, lines, rawlines, i, ruleCheckKey, Error, cpplines, fileErrorCount)
      if -1 == i:
        return -1
      i += 1
      continue
    if strcmp.Search(r'^(\s*)((\bcase\b)|(\bdefault\b))', line):
      if i == startLineNo or i == EndLineNo:
        return True,EndLineNo,hasError,hasGotoReturnError
      break
    elif i == EndLineNo:
      break
    else:
      if strcmp.Search(r'\bbreak\b', line):
        hasBreak = True
      elif not common.IsBlankLine(line):
        hasStatement = True
        statementEndLineNo = i
      if strcmp.Search(r'(\bgoto\b|\breturn\b|\bexit\b)', line):
        mm = strcmp.Search(r'(\bgoto\b|\breturn\b|\bexit\b)', line)
        if not common.IsBlankLine(line[0:line.find(mm.group(1))]):
          hasStatementForReturn = True
          statementEndLineNoForReturn = i
        hasGotoReturn = True
        gotoReturnLineNo = i
        if not hasGotoReturnError:
          hasGotoReturnError = checkGotoReturnError(lines, rawlines, startLineNo, statementEndLineNoForReturn, gotoReturnLineNo, hasStatementForReturn)
      elif not common.IsBlankLine(line):
        hasStatementForReturn = True
        statementEndLineNoForReturn = i
    i += 1
  caseEndLineNo = i - 1
  if hasGotoReturn:
    hasError = False
  else:
    hasError = checkBreakError(lines, rawlines, statementEndLineNo + 1, caseEndLineNo, hasBreak, hasStatement)
  return False,caseEndLineNo,hasError,hasGotoReturnError

def checkSwitchBlock(filename, lines, rawlines, startLineNo, ruleCheckKey, Error, cpplines, fileErrorCount):

  hasNoBreakCommentError = False
  hasGotoReturnNoCommentError = False
  i = startLineNo
  indentErrorTypeWord = ''
  # get qty of  Switch indent charactor
  m = strcmp.Search(r'^(\s*)\bswitch\b', lines[startLineNo])

  # get switch block end line no
  i,isInSameLine = checkSwitchOpenCurlyBraceInOneLine(lines, startLineNo)
  if i == -1:
    return len(lines)
  switchEndLineNo = getSwitchBlockEndLineNo(lines, i)
  if switchEndLineNo == -1:
    return -1

  # error message
  errorMessageHeader = "Code Style Rule:"
  hasNoBreakErrorMessage = "If a non-empty case doesn't have a break, there should be comments to explain the reason."
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

      indentErrorTypeWord = ''
      hasNoBreakCommentError = False
      hasGotoReturnNoCommentError = False
      caseDefaultLineNo = i

      if m.group(2) == 'case':
        indentErrorTypeWord = 'case'
        isSkipSwitch, i, hasNoBreakCommentError, hasGotoReturnNoCommentError = checkCaseBlock(filename, lines, rawlines, i, switchEndLineNo, ruleCheckKey, Error, cpplines, fileErrorCount)
      else:
        indentErrorTypeWord = 'default'
        isSkipSwitch, i, hasNoBreakCommentError, hasGotoReturnNoCommentError = checkDefaultBlock(filename, lines, rawlines, i, switchEndLineNo, ruleCheckKey, Error, cpplines, fileErrorCount)
        
      outputErrorMessage = errorMessageHeader

      if hasNoBreakCommentError:
        outputErrorMessage += ' ' + hasNoBreakErrorMessage
      if outputErrorMessage != errorMessageHeader:
        Error(filename, lines, caseDefaultLineNo, ruleCheckKey, 3, outputErrorMessage)
      if indentErrorTypeWord == 'default':
        i = switchEndLineNo
    i += 1

  return i - 1
      
      

def CheckCSC080015(filename, file_extension, clean_lines, rawlines, nesting_state, ruleCheckKey, Error, cpplines, fileErrorCount):
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
  
      