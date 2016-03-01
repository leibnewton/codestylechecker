#!/usr/bin/python  
#-*- coding: utf-8 -*-
'''
Created on 2014-1-27

@author: wangxc
'''
import os
import sys
syspath = os.path.dirname(os.path.dirname(__file__))
if not os.path.join(syspath, "tools") in sys.path:
  sys.path.append(os.path.join(syspath, "tools"))
import common
strcmp = common.StringCompareInfo()

def hasSEUVariableDefinition(lines, fromLno, endLno, hasExtern):
  i = fromLno
  line = ''
  while i <= endLno:
    if common.IsBlankLine(lines[i]):
      i = i + 1
      continue
    if strcmp.Search(r'^\s*#', lines[i]):
      i = i + 1
      continue
    line += lines[i]
    i = i + 1
  lastestLeftBraceIndex = line.rfind('{')
  leftBraceQty = line[0:lastestLeftBraceIndex].count('{')
  rightBraceQty = line[0:lastestLeftBraceIndex].count('}')
  #(extern) struct A {}a,b={};
  if leftBraceQty == rightBraceQty and leftBraceQty > 0:
    return True
  #(extern)enum/union {} a =...;
  lastestRightBraceIndex = line.rfind('}')
  if line[lastestRightBraceIndex:].find('=') > -1:
    return True
  if hasExtern:
    return False
  variables = line[lastestRightBraceIndex + 1:].replace(' ', '').replace('\t', '').replace(';','')
  if variables:
    return True
  return False


def getTypedefList(lines, fromLno):
  m = strcmp.Search(r'typedef(\s+)(\bstruct\b|\bunion\b|\benum\b)\s+',lines[fromLno])
  if not m:
    return []
  index = lines[fromLno].find(m.group(1)+m.group(2))
  line = lines[fromLno][index:]
  line = line.replace(m.group(1)+m.group(2), '')
  leftBraceQty = 0
  rightBraceQty = 0
  lengthOfLines = len(lines)
  endLno = fromLno
  for i in xrange(fromLno, lengthOfLines):
    endLno = i
    if common.IsBlankLine(lines[i]):
      continue
    if strcmp.Search(r'^\s*#', lines[i]):
      continue
    leftBraceQtyTemp = lines[i].count('{')
    rightBraceQtyTemp = lines[i].count('}')
    leftBraceQty = leftBraceQty + leftBraceQtyTemp
    rightBraceQty = rightBraceQty + rightBraceQtyTemp
    if i != fromLno:
      line += lines[i]
    if leftBraceQty == rightBraceQty and lines[i].rstrip().endswith(';'):
      break
  typeList = []
  if leftBraceQty == 0 :
    typeList = line.replace('*',' ').replace(',',' ').split()
  else:
    firstLeftBraceIndex = line.find("{")
    firstRightBraceIndex = line.rfind("}")
    lineWithoutBraceBlock = line[0:firstLeftBraceIndex] + ' ' + line[(firstRightBraceIndex + 1):(len(line) - 1)]
    typeList = lineWithoutBraceBlock.replace('*',' ').replace(',',' ').split()
  return typeList


def getTemplateEndLno(lines, startLno):
  lengthOfLines = len(lines)
  leftArrowQty = 0
  rightArrowQty = 0
  for i in xrange(startLno, lengthOfLines):
    if common.IsBlankLine(lines[i]):
      continue
    if strcmp.Search(r'^\s*#', lines[i]):
      continue
    leftArrowQty = leftArrowQty + lines[i].count('<')
    rightArrowQty = rightArrowQty + lines[i].count('>') - lines[i].count('->')
    if leftArrowQty == rightArrowQty:
      return i
  return -1


def isExternCLineOpen(line):
  leftBraceIndex = line.find('{')
  rightBraceIndex = line.find('}')
  if rightBraceIndex == -1:
    return True
  if line.count('{') != line.count('}'):
    return True
  return False


def isWordInBraceBlock(word, line, externCOpen, leftBraceQty, rightBraceQty):
  wordIndex = line.find(word)
  leftBraceQtyTemp = 0
  rightBraceQtyTemp = 0
  if wordIndex > -1:
    leftBraceQtyTemp = line[0:wordIndex].count("{")
    rightBraceQtyTemp = line[0:wordIndex].count("}")
  # externC Block close
  if externCOpen == 0:
    if (leftBraceQty + leftBraceQtyTemp) == (rightBraceQty + rightBraceQtyTemp):
      return False
    else:
      return True
  else:
  # externC Block open
    if (leftBraceQty + leftBraceQtyTemp) == (rightBraceQty + rightBraceQtyTemp):
      return False
    elif (leftBraceQty + leftBraceQtyTemp) == (rightBraceQty + rightBraceQtyTemp + 1):
      return False
    else:
      return True
  return True


def isWordInBraketBlock(word, line, leftBraketQty, rightBraketQty):
  wordIndex = line.find(word)
  leftBraketQtyTemp = 0
  rightBraketQtyTemp = 0
  if wordIndex > -1:
    leftBraketQtyTemp = line[0:wordIndex].count("(")
    rightBraketQtyTemp = line[0:wordIndex].count(")")
  if (leftBraketQty + leftBraketQtyTemp) == (rightBraketQty + rightBraketQtyTemp):
    return False
  else:
    return True


def isFunctionDeclareOrIsParam(typeWord, lines, fromLno):
  leftBraceQty = 0
  rightBraceQty = 0
  lengthOfLines = len(lines)
  index = lines[fromLno].find(typeWord)
  line = lines[fromLno][index:]
  for i in xrange(fromLno, lengthOfLines):
    endLno = i
    if common.IsBlankLine(lines[i]):
      continue
    if strcmp.Search(r'^\s*#', lines[i]):
      continue
    leftBraceQtyTemp = lines[i].count('{')
    rightBraceQtyTemp = lines[i].count('}')
    leftBraceQty = leftBraceQty + leftBraceQtyTemp
    rightBraceQty = rightBraceQty + rightBraceQtyTemp
    if i != fromLno:
      line += lines[i]
    if leftBraceQty == rightBraceQty and lines[i].rstrip().endswith(';'):
      break
  if line.count('(') != line.count(')'):
    return True
  index = line.find('(')
  if index == -1:
    return False
  if line[0:index].find('{') == -1 and line[0:index].find(',') == -1 and line[0:index].find('=') == -1:
    return True
  return False


def getDefineMacroEndNo(lines, fromLno):
  lengthOfLines = len(lines)
  for i in xrange(fromLno, lengthOfLines):
    if not lines[i].endswith("\\"):
      return i
  return -1


def CheckCSC010004(filename, file_extension, clean_lines, rawlines, nesting_state, ruleCheckKey, Error, cpplines, fileErrorCount):
  if file_extension != "h":
    return
  errMessage = "Code Style Rule: Please don\'t define variables in the header file."
  stuctsEnumTypeList = []
  leftBracketsQty = 0
  rightBracketsQty = 0
  tempLeftBracketsQty = 0
  tempRightBracketsQty = 0
  leftBraceQty = 0
  rightBraceQty = 0
  templeftBraceQty = 0
  tempRightBraceQty = 0
  lines = clean_lines.elided
  isStrutsEnumUnionOpen = False
  strutsEnumUnionOpenLno = 0
  regExp = ''
  isTypeDef = False
  inTemplate = False
  templateEndLno = -1
  templateEndLno = -1
  hasExternBeforeStruct = False
  isExternCOpen = 0
  defineEndLineNo = -1
  #追加特殊情况处理Flag
  bFlag = False
  for i in xrange(clean_lines.NumLines()):
    if common.IsBlankLine(lines[i]):
      continue
    if strcmp.Search(r'^\s*#\s*define\s+', lines[i]):
      defineEndLineNo = getDefineMacroEndNo(lines, i)
    if i < defineEndLineNo:
      continue
    if i == defineEndLineNo:
      defineEndLineNo = -1
      continue
    if strcmp.Search(r'^\s*#', lines[i]):
      continue
    if strcmp.Search(r'(\bextern\b\s*"")', lines[i]):
      if isExternCLineOpen(lines[i]):
        isExternCOpen = 1
    leftBracketsQtyTemp = lines[i].count('(')
    rightBracketsQtyTemp = lines[i].count(')')
    leftBraceQtyTemp = lines[i].count('{')
    rightBraceQtyTemp = lines[i].count('}')
    tempLeftBracketsQty = leftBracketsQty
    tempRightBracketsQty = rightBracketsQty
    templeftBraceQty = leftBraceQty
    tempRightBraceQty = rightBraceQty
    leftBracketsQty = leftBracketsQty + leftBracketsQtyTemp
    rightBracketsQty = rightBracketsQty + rightBracketsQtyTemp
    leftBraceQty = leftBraceQty + leftBraceQtyTemp
    rightBraceQty = rightBraceQty + rightBraceQtyTemp
    m = strcmp.Search(r'^\s*template\s*<', lines[i])
    if m:
      inTemplate = True
      templateEndLno = getTemplateEndLno(lines, i)
      if i == templateEndLno:
        inTemplate = False
        continue
    if inTemplate:
      if i == templateEndLno:
        inTemplate = False
        continue
      else:
        continue
    m = strcmp.Search(r'(\bstruct\b|\bunion\b|\benum\b)\s*(\w*)\s*{*', lines[i])
    if m:
      isInbrace = isWordInBraceBlock(m.group(1), lines[i], isExternCOpen, templeftBraceQty, tempRightBraceQty)
      m3 = strcmp.Search(r'(\bstruct\b|\bunion\b|\benum\b)\s+(\w+)\s*;', lines[i].replace('*',' ').replace('&',' '))
      if m3 and (not isInbrace):
        if not (m3.group(2) in stuctsEnumTypeList):
          if not regExp:
            regExp += r'\b' + m3.group(2) + r'\b'
          else:
            regExp += r'|\b' + m3.group(2) + r'\b'
          stuctsEnumTypeList.append(m3.group(2))
        continue
      isFuction = isFunctionDeclareOrIsParam(m.group(1), lines, i)
      m2 = strcmp.Search(r'(\bstruct\b|\bunion\b|\benum\b)\s+(\w+)\s+(\w+)', lines[i].replace('*',' ').replace('&',' '))
      if (not isInbrace) and (not m2) and (not m3) and (not isFuction) and (not isStrutsEnumUnionOpen):
        isStrutsEnumUnionOpen = True
        strutsEnumUnionOpenLno = i
        if lines[i].find('extern') == -1:
          hasExternBeforeStruct = False
        else:
          hasExternBeforeStruct = True
        if lines[i].find('typedef') == -1:
          if m.group(2):
            if not (m.group(2) in stuctsEnumTypeList):
              if not regExp:
                regExp += r'\b' + m.group(2) + r'\b'
              else:
                regExp += r'|\b' + m.group(2) + r'\b'
              stuctsEnumTypeList.append(m.group(2))
        else:
          isTypeDef = True
          typeList = getTypedefList(lines, i)
          if len(typeList) > 0:
            for itemType in typeList:
              if not (itemType in stuctsEnumTypeList):
                if not regExp:
                  regExp += r'\b' + itemType + r'\b'
                else:
                  regExp += r'|\b' + itemType + r'\b'
                stuctsEnumTypeList.append(itemType)
    elif strcmp.Search(r'^\s*typedef\s+', lines[i]):
      if lines[i].count('(') > 0:
        continue
      isInbrace = isWordInBraceBlock('typedef', lines[i], isExternCOpen, templeftBraceQty, tempRightBraceQty)
      if isInbrace:
        continue
      items = lines[i].replace(';','').replace('*',' ').split()
      if not (items[len(items) - 1] in stuctsEnumTypeList):
        if not regExp:
          regExp += r'\b' + items[len(items) - 1] + r'\b'
        else:
          regExp += r'|\b' + items[len(items) - 1] + r'\b'
        stuctsEnumTypeList.append(items[len(items) - 1])
      continue
    if isExternCOpen == 1 and leftBraceQty == rightBraceQty:
      isExternCOpen = 0
    if leftBraceQty == (rightBraceQty + isExternCOpen) and isStrutsEnumUnionOpen:
      if lines[i].rstrip().endswith(';'):
        isStrutsEnumUnionOpen = False
        if not isTypeDef:
          if hasSEUVariableDefinition(lines, strutsEnumUnionOpenLno, i, hasExternBeforeStruct):
            Error(filename, lines, i, ruleCheckKey, 3,errMessage)
        else:
          isTypeDef = False
        strutsEnumUnionOpenLno = 0
    if isStrutsEnumUnionOpen:
      continue
    if lines[i].find('typedef') > -1:
      continue
    #追加特殊情况处理 START
    if not bFlag:
      mSpecial = strcmp.Search(r'\S+\(.+\)\s+[^ ;{]', lines[i])
      if mSpecial and not strcmp.Search(r'{', lines[i][mSpecial.end():]):
        bFlag = True
      elif strcmp.Search(r'\S+\(.+\)\s*$', lines[i]):
        bFlag = True
    if bFlag and strcmp.Search(r'{', lines[i]):
      bFlag = False
    #追加特殊情况处理 END
    if strcmp.Search(r'\bconst\b', lines[i]):
      continue
    m = strcmp.Search(r'((\bbool\b|\bchar\b|\bwchar_t\b|\bshort\b|\bint\b|\blong\b|\bfloat\b|\bdouble\b)\s*\w+\s*)', lines[i].replace('*',' '))
    if m:
      isLineInBrace = isWordInBraceBlock(m.group(1), lines[i].replace('*',' '), isExternCOpen, templeftBraceQty, tempRightBraceQty)
      isLineInBraket = isWordInBraketBlock(m.group(1), lines[i].replace('*',' '), tempLeftBracketsQty, tempRightBracketsQty)
      if isLineInBrace or isLineInBraket:
        continue
      if isFunctionDeclareOrIsParam(m.group(2), lines, i):
        continue
      if lines[i].find('=') > -1:
        Error(filename, lines, i, ruleCheckKey, 3,errMessage)
        continue
      if not strcmp.Search(r'\bextern\b(\s*\w*)\s+' + m.group(2) + '\s+', lines[i].replace('*',' ')):
        #追加特殊情况处理判断
        if not bFlag:
          Error(filename, lines, i, ruleCheckKey, 3,errMessage)
      continue
    if len(stuctsEnumTypeList) > 0:
      m = strcmp.Search(r'((' + regExp + r')\s*\w+\s*)', lines[i].replace('*',' '))
      if m:
        isLineInBrace = isWordInBraceBlock(m.group(1), lines[i].replace('*',' '), isExternCOpen, templeftBraceQty, tempRightBraceQty)
        isLineInBraket = isWordInBraketBlock(m.group(1), lines[i].replace('*',' '), tempLeftBracketsQty, tempRightBracketsQty)
        if isLineInBrace or isLineInBraket:
          continue
        if isFunctionDeclareOrIsParam(m.group(2), lines, i):
          continue
        if lines[i].find('=') > -1:
          Error(filename, lines, i, ruleCheckKey, 3,errMessage)
          continue
        if not strcmp.Search(r'\bextern\b\s+', lines[i]):
          Error(filename, lines, i, ruleCheckKey, 3,errMessage)
    