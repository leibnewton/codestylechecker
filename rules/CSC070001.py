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

def getTemplateEndLno(lines, startLno):
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


def getDefineMacroEndNo(lines, fromLno):
  lengthOfLines = len(lines)
  for i in xrange(fromLno, lengthOfLines):
    if not lines[i].endswith("\\"):
      return i
  return -1


def getNicknameFromTypedefBaseType(lines, startLno):
  openParenthesisQty = 0
  closeParenthesisQty = 0
  lengthOfLines = len(lines)
  line = lines[startLno][lines[startLno].find('typedef'):]
  nicknameList = []
  for i in xrange(startLno, lengthOfLines):
    endLno = i
    if common.IsBlankLine(lines[i]):
      continue
    if strcmp.Search(r'^\s*#', lines[i]):
      continue
    if i == startLno:
      openParenthesisQty = line.count('(')
      closeParenthesisQty = line.count(')')
    else:
      openParenthesisQty = openParenthesisQty + lines[i].count('(')
      closeParenthesisQty = closeParenthesisQty + lines[i].count(')')
      line += ' ' + lines[i]
    if openParenthesisQty == closeParenthesisQty and lines[i].rstrip().endswith(';'):
      break
  if openParenthesisQty > 0:
    return nicknameList,endLno
  line = line.replace(';','').replace('*',' ').replace('&',' ')
  line = strcmp.Sub(r'\[((\w)|(:)|(\+)|(\-)|(\s)|(/)|(\*))*\]','',line)
  tempList = line.split(',')
  for i in xrange(len(tempList)):
    if i == 0:
      templine = strcmp.Sub(r'<.*>','',tempList[i].replace('typedef', ' '))
      tempArray = templine.split()
      nicknameList.append(tempArray[-1])
      if strcmp.Search(r'<.*>', tempList[i]):
        continue
      if len(tempArray) > 1:
        if not (tempArray[-2] in ['bool','char','wchar_t','short','int','long','float','double']):
          nicknameList.append(tempArray[-2])
    else:
      nicknameList.append(tempList[i].strip())
  return nicknameList,endLno


def getNickNameFromTypedefParticularType(particularType, lines, startLno):
  openCurlyBraceQty = 0
  closeCurlyBraceQty = 0
  lengthOfLines = len(lines)
  nicknameList = []
  line = lines[startLno][lines[startLno].find(particularType):]
  endLno = -1
  for i in xrange(startLno, lengthOfLines):
    endLno = i
    if common.IsBlankLine(lines[i]):
      continue
    if strcmp.Search(r'^\s*#', lines[i]):
      continue
    if i == startLno:
      openCurlyBraceQty = line.count('{')
      closeCurlyBraceQty = line.count('}')
    else:
      openCurlyBraceQty = openCurlyBraceQty + lines[i].count('{')
      closeCurlyBraceQty = closeCurlyBraceQty + lines[i].count('}')
      line += ' ' + lines[i]
    if openCurlyBraceQty == closeCurlyBraceQty and lines[i].rstrip().endswith(';'):
      break
  if openCurlyBraceQty > 0:
    line = line[0:line.find('{')] + ',' + line[line.rfind('}') + 1:]
  line = line.replace(';','').replace('*',' ').replace('&',' ')
  if line.find('(') > 0:
    return nicknameList, endLno
  line = strcmp.Sub(r'\[((\w)|(:)|(\+)|(\-)|(\s)|(/)|(\*))*\]','',line)
  tempList = line.split(',')
  for i in xrange(len(tempList)):
    if i == 0:
      tempArray = tempList[i].replace(particularType, ' ').split()
      for tempArrayItem in tempArray:
        nicknameList.append(tempArrayItem)
    else:
      nicknameList.append(tempList[i].strip())
  return nicknameList, -1


def getNicknameIfTypedefAndPaticulartypeInTwoLine(lines, startLno):
  nicknameList = []
  if lines[startLno].replace('typedef','').strip():
    return False,-1,nicknameList
  lengthOfLines = len(lines)
  endLno = -1
  typedefSkipEndLno = -1
  for i in xrange(startLno + 1, lengthOfLines):
    endLno = i
    if common.IsBlankLine(lines[i]):
      continue
    if strcmp.Search(r'^\s*#', lines[i]):
      continue
    m = strcmp.Search(r'^\s*(\bstruct\b|\bunion\b|\benum\b)', lines[i])
    if m:
      nicknameList,typedefSkipEndLno = getNickNameFromTypedefParticularType(m.group(1), lines, i)
      break
    else:
      return False,-1,nicknameList
  if len(nicknameList) == 0:
    return True,typedefSkipEndLno,nicknameList
  return True,endLno,nicknameList


def isParameter(line, openParenthesisQty, closeParenthesisQty):
  if openParenthesisQty + line.count('(') != closeParenthesisQty + line.count(')'):
    return True
  return False


def isInCurlyBraceBlock(line, openCurlyBraceQty, closeCurlyBraceQty):
  if openCurlyBraceQty + line.count('{') != closeCurlyBraceQty + line.count('}'):
    return True
  return False


def isFunctionDeclare(typeWord, lines, startLno):
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
    if openCurlyBraceQty == closeCurlyBraceQty and lines[i].rstrip().endswith(';') and openCurlyBraceQty == 0:
      break
    if openCurlyBraceQty == closeCurlyBraceQty and openCurlyBraceQty > 0:
      break
  openParenthesisIndex = line.find('(')
  if openParenthesisIndex == -1:
    return False
  if line[0:openParenthesisIndex].find('{') > -1:
    return False
  if line[0:openParenthesisIndex].find(',') > -1:
    return False
  if line[0:openParenthesisIndex].find('=') > -1:
    if line[0:openParenthesisIndex].find('operator') > -1:
      return True
    return False
  return True

def getErrorLnoListFromDefineBlock(blockLines):
  lengthOfLines = len(blockLines)
  openCurlyBraceQty = 0
  closeCurlyBraceQty = 0
  openParenthesisQty = 0
  closeParenthesisQty = 0
  tempOpenCurlyBraceQty = 0
  tempCloseCurlyBraceQty = 0
  tempOpenParenthesisQty = 0
  tempCloseParenthesisQty = 0
  errorLnoList = []
  for i in xrange(lengthOfLines):
    line = blockLines[i].strip()
    if common.IsBlankLine(line):
      continue
    tempOpenCurlyBraceQty = openCurlyBraceQty
    tempCloseCurlyBraceQty = closeCurlyBraceQty
    tempOpenParenthesisQty = openParenthesisQty
    tempCloseParenthesisQty = closeParenthesisQty
    openCurlyBraceQty = openCurlyBraceQty + line.count('{')
    closeCurlyBraceQty = closeCurlyBraceQty + line.count('}')
    openParenthesisQty = openParenthesisQty + line.count('(')
    closeParenthesisQty = closeParenthesisQty + line.count(')')
    commaIndex = line.find(',')
    lineLength = len(line)
    if commaIndex == -1:
      continue
    if lineLength == 1 or lineLength - 1 == commaIndex:
      continue
    while commaIndex > -1:
      if isParameter(line[0:commaIndex],tempOpenParenthesisQty,tempCloseParenthesisQty) or isInCurlyBraceBlock(line[0:commaIndex],tempOpenCurlyBraceQty,tempCloseCurlyBraceQty):
        if commaIndex == (lineLength - 1):
          commaIndex = -1
        else:
          if line[commaIndex + 1:].find(',') == -1:
            commaIndex = -1
          else:
            commaIndex = line[commaIndex + 1:].find(',') + commaIndex + 1
        continue
      if commaIndex == 0:
        if line[commaIndex + 1:].find(',') == -1:
          commaIndex = -1
        else:
          commaIndex = line[commaIndex + 1:].find(',') + commaIndex + 1
        continue
      if commaIndex == (lineLength - 1):
        commaIndex = -1
        continue
      if strcmp.Search(r'(\w|\)|\}),\w', line[commaIndex - 1 : commaIndex + 2]):
        errorLnoList.append(i)
        commaIndex = -1
      elif line[commaIndex + 1:].find(',') == -1:
        commaIndex = -1
      else:
        commaIndex = line[commaIndex + 1:].find(',') + commaIndex + 1
  return errorLnoList


def checkStructEnumUnionDeclare(typeWord, lines, startLno):
  lengthOfLines = len(lines)
  index = lines[startLno].find(typeWord)
  line = lines[startLno][index:].replace('*',' ').replace('&',' ')
  lnoOf1stOpenCurlyBrace = -1
  errorLnoList = []
  openCurlyBraceQty = 0
  closeCurlyBraceQty = 0
  type = ''
  declareLastCloseBraceLno = -1
  for i in xrange(startLno, lengthOfLines):
    if common.IsBlankLine(lines[i]):
      line += ' \n'
      continue
    if strcmp.Search(r'^\s*#', lines[i]):
      line += ' \n'
      continue
    tempLine = lines[i].replace('*',' ').replace('&',' ')
    if i == startLno:
      line += ' \n'
    else:
      line += tempLine + ' \n'
    if openCurlyBraceQty == 0 and tempLine.find('{') > -1:
      lnoOf1stOpenCurlyBrace = i
    openCurlyBraceQty = openCurlyBraceQty + tempLine.count('{')
    closeCurlyBraceQty = closeCurlyBraceQty + tempLine.count('}')
    if openCurlyBraceQty == closeCurlyBraceQty and tempLine.rstrip().endswith(';'):
      break
  templine = line.replace('\n',' ')
  m = strcmp.Search(r'^' + typeWord + r'\s*(\w*)\s*{+', templine.replace('::',''))
  if m:
    templineForType = templine[0:templine.find('{')]
    if templineForType.find('::') == -1:
      type = m.group(1)
    else:
      type = templineForType.replace(typeWord,'').strip()
    if openCurlyBraceQty != closeCurlyBraceQty:
      return True,type,len(lines)-1,errorLnoList
    if line.find(',') == -1:
      return True,type,lnoOf1stOpenCurlyBrace,errorLnoList
    findDeclareEndCloseBraceIndex = False
    declareEndCloseBraceIndex = line.find('}')
    while not findDeclareEndCloseBraceIndex:
      if line[0:declareEndCloseBraceIndex + 1].count('{') == line[0:declareEndCloseBraceIndex + 1].count('}'):
        findDeclareEndCloseBraceIndex = True
      elif line[declareEndCloseBraceIndex + 1:].find('}') != -1:
        declareEndCloseBraceIndex = line[declareEndCloseBraceIndex + 1:].find('}') + declareEndCloseBraceIndex + 1
    declareEndCloseBraceLno = startLno + line[0:declareEndCloseBraceIndex + 1].count(' \n')
    if line[declareEndCloseBraceIndex + 1:].count('{') == 0 and line[declareEndCloseBraceIndex + 1:].find(',') == -1:
      return True,type,lnoOf1stOpenCurlyBrace,errorLnoList
    if line[declareEndCloseBraceIndex + 1:].count('{') == 1:
      if (line[declareEndCloseBraceIndex + 1:].find('{') < line[declareEndCloseBraceIndex + 1:].find(',')) and (line[declareEndCloseBraceIndex + 1:].rfind('}') > line[declareEndCloseBraceIndex + 1:].rfind(',')):
        return True,type,lnoOf1stOpenCurlyBrace,errorLnoList
    tempList = getErrorLnoListFromDefineBlock(line[declareEndCloseBraceIndex + 1:].split(' \n'))
    for tempLno in tempList:
      errorLnoList.append(tempLno + declareEndCloseBraceLno)
    return True,type,lnoOf1stOpenCurlyBrace,errorLnoList
  else:
    m = strcmp.Search(r'^' + typeWord + r'\s+(\b\w+\b)\s+(\b\w+\b)', templine.replace('*', ' '))
    if m:
      type = m.group(1)
    return False,type,-1,errorLnoList


def checkVariableDefinition(typeWord, lines, startLno):
  lengthOfLines = len(lines)
  index = lines[startLno].find(typeWord)
  line = lines[startLno][index:].replace('*',' ').replace('&',' ')
  errorLnoList = []
  openCurlyBraceQty = 0
  closeCurlyBraceQty = 0
  for i in xrange(startLno, lengthOfLines):
    if common.IsBlankLine(lines[i]):
      line += ' \n'
      continue
    if strcmp.Search(r'^\s*#', lines[i]):
      line += ' \n'
      continue
    tempLine = lines[i].replace('*',' ').replace('&',' ')
    if i == startLno:
      line += ' \n'
    else:
      line += tempLine + ' \n'
    openCurlyBraceQty = openCurlyBraceQty + tempLine.count('{')
    closeCurlyBraceQty = closeCurlyBraceQty + tempLine.count('}')
    if openCurlyBraceQty > 0:
      firstopenCurlyBrace = line.find('{')
      if line[0:firstopenCurlyBrace].count('(') == line[0:firstopenCurlyBrace].count(')') and line[0:firstopenCurlyBrace].find('=') == -1:
        return errorLnoList
    if openCurlyBraceQty == closeCurlyBraceQty and tempLine.rstrip().endswith(';'):
      break
  if line.find(',') == -1:
    return errorLnoList
  if openCurlyBraceQty == 1 and (line.find(',') > line.find('{')) and (line.rfind(',') < line.rfind('}')):
    return errorLnoList
  if not strcmp.Search(r'^' + typeWord + r'\s+(\w+)', line.replace('\n',' ')):
    return errorLnoList
  tempList = getErrorLnoListFromDefineBlock(line.split(' \n'))
  for tempLno in tempList:
    errorLnoList.append(tempLno + startLno)
  return errorLnoList



def CheckCSC070001(filename, file_extension, clean_lines, rawlines, nesting_state, ruleCheckKey, Error, cpplines, fileErrorCount):
  errorMessage = 'Code Style Rule: Please don\'t define more than one variable in a single line.'
  particularTypeList = []
  openParenthesisQty = 0
  closeParenthesisQty = 0
  tempOpenParenthesisQty = 0
  tempCloseParenthesisQty = 0
  lines = clean_lines.elided
  isStrutsEnumUnionDeclare = False
  strutsEnumUnionOpenLno = 0
  regExp = ''
  skipEndLno = -1
  skipDefineEndLno = -1
  skipTemplateEndLno = -1
  for i in xrange(clean_lines.NumLines()):
    #null line skip
    if common.IsBlankLine(lines[i]):
      continue
    #define line skip
    if i <= skipDefineEndLno:
      continue 
    if strcmp.Search(r'^\s*#\s*define\s+', lines[i]):
      skipDefineEndLno = getDefineMacroEndNo(lines, i)
      continue
    # line start with # skip
    if strcmp.Search(r'^\s*#', lines[i]):
      skipDefineEndLno = getDefineMacroEndNo(lines, i)
      continue
    # template declare line skip
    if i <= skipTemplateEndLno:
      continue
    m = strcmp.Search(r'^\s*template\s*<', lines[i])
    if m:
      skipTemplateEndLno = getTemplateEndLno(lines, i)
      continue
    # Parenthesis statistics
    openParenthesisQtyTemp = lines[i].count('(')
    closeParenthesisQtyTemp = lines[i].count(')')
    tempOpenParenthesisQty = openParenthesisQty
    tempCloseParenthesisQty = closeParenthesisQty
    openParenthesisQty = openParenthesisQty + openParenthesisQtyTemp
    closeParenthesisQty = closeParenthesisQty + closeParenthesisQtyTemp
    if i <= skipEndLno:
      continue
    m = strcmp.Search(r'(\btypedef\b\s+(\bstruct\b|\bunion\b|\benum\b))\s*(\w*)\s*{*', lines[i].replace('*',' ').replace('&',' '))
    if m:
      typeList,skipEndLno = getNickNameFromTypedefParticularType(m.group(1), lines, i)
      for typeListItem in typeList:
        if not (typeListItem in particularTypeList):
          if not regExp:
            regExp += r'\b' + typeListItem + r'\b'
          else:
            regExp += r'|\b' + typeListItem + r'\b'
          particularTypeList.append(typeListItem)
      continue
    elif strcmp.Search(r'\btypedef\b', lines[i]):
      isTypedefParticularType,skipEndLno,typeList =getNicknameIfTypedefAndPaticulartypeInTwoLine(lines, i)
      if isTypedefParticularType:
        for typeListItem in typeList:
          if not (typeListItem in particularTypeList):
            if not regExp:
              regExp += r'\b' + typeListItem + r'\b'
            else:
              regExp += r'|\b' + typeListItem + r'\b'
            particularTypeList.append(typeListItem)
        continue
      else:
        typeList,skipEndLno=getNicknameFromTypedefBaseType(lines, i)
        for typeListItem in typeList:
          if not (typeListItem in particularTypeList):
            if not regExp:
              regExp += r'\b' + typeListItem + r'\b'
            else:
              regExp += r'|\b' + typeListItem + r'\b'
            particularTypeList.append(typeListItem)
        continue
    m = strcmp.Search(r'(\bstruct\b|\bunion\b|\benum\b)', lines[i])
    if m:
      if isParameter(lines[i][0:lines[i].find(m.group(1))], tempOpenParenthesisQty, tempCloseParenthesisQty):
        continue
      if isFunctionDeclare(m.group(1), lines, i):
        continue
      isStrutsEnumUnionDeclare,declareType,skipEndLno,errorLnoList = checkStructEnumUnionDeclare(m.group(1), lines, i)
      if isStrutsEnumUnionDeclare:
        if declareType:
          if not (declareType in particularTypeList):
            if not regExp:
              regExp += r'\b' + declareType + r'\b'
            else:
              regExp += r'|\b' + declareType + r'\b'
            particularTypeList.append(declareType)
          if declareType.find('::') > -1:
            declareTypeTemp = declareType[declareType.find('::'):].replace('::','').strip()
            if not (declareTypeTemp in particularTypeList):
              if not regExp:
                regExp += r'\b' + declareTypeTemp + r'\b'
              else:
                regExp += r'|\b' + declareTypeTemp + r'\b'
              particularTypeList.append(declareTypeTemp)
        for errorLno in errorLnoList:
          Error(filename, lines, errorLno, ruleCheckKey, 3,errorMessage)
        continue
      else:
        if declareType:
          if not (declareType in particularTypeList):
            if not regExp:
              regExp += r'\b' + declareType + r'\b'
            else:
              regExp += r'|\b' + declareType + r'\b'
            particularTypeList.append(declareType)

    m = strcmp.Search(r'(\bbool\b|\bchar\b|\bwchar_t\b|\bshort\b|\bint\b|\blong\b|\bfloat\b|\bdouble\b)\s*\w*\s*', lines[i].replace('*',' '))
    if not m:
      if len(particularTypeList) == 0:
        continue
      m = strcmp.Search(r'(' + regExp + r')\s*\w*\s*', lines[i].replace('*',' '))
    if m:
      if isParameter(lines[i][0:lines[i].find(m.group(1))], tempOpenParenthesisQty, tempCloseParenthesisQty):
        continue
      if isFunctionDeclare(m.group(1), lines, i):
        continue
      errorLnoList = checkVariableDefinition( m.group(1), lines, i)
      for errorLno in errorLnoList:
        Error(filename, lines, errorLno, ruleCheckKey, 3,errorMessage)
      continue
    