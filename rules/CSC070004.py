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


def getTypedefBaseTypeEndLno(lines, startLno):
  openParenthesisQty = 0
  closeParenthesisQty = 0
  lengthOfLines = len(lines)
  line = lines[startLno][lines[startLno].find('typedef'):]
  endLno = startLno
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
  return endLno


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
  line = line.replace(';','')
  if line.find('(') > 0:
    return nicknameList, endLno
  tempList = line.split(',')
  for i in xrange(len(tempList)):
    if i == 0:
      tempArray = tempList[i].replace(particularType, ' ').replace('*',' ').replace('&',' ').split()
      if tempList[i].find('*') > -1 or tempList[i].find('&') > -1 or tempList[i].find('[') > -1:
        if len(tempArray) > 1:
          nicknameList.append(tempArray[0])
      else:
        for tempArrayItem in tempArray:
            nicknameList.append(tempArrayItem)
    else:
      if tempList[i].find('*') == -1 and tempList[i].find('&') == -1 and tempList[i].find('[') == -1:
        nicknameList.append(tempList[i].strip())
  return nicknameList, endLno


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
    m = strcmp.Search(r'^\s*(\benum\b)', lines[i])
    if m:
      nicknameList,typedefSkipEndLno = getNickNameFromTypedefParticularType(m.group(1), lines, i)
      break
    else:
      return False,-1,nicknameList
  return True,typedefSkipEndLno,nicknameList


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
  skipEndLineNo = -1
  for i in xrange(startLno, lengthOfLines):
    if i < skipEndLineNo:
      continue
    if common.IsBlankLine(lines[i]):
      continue
    if strcmp.Search(r'^\s*#', lines[i]):
      skipEndLineNo = getTemplateEndLno(lines, i)
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
  # int a (0),b; 这种形式不是函数定义或函数声明
  openParenthesisQty = 0
  closeParenthesisQty = 0
  for i in xrange(openParenthesisIndex, len(line)):
    if line[i] == '(':
      openParenthesisQty += 1
    elif line[i] == ')':
      closeParenthesisQty += 1
    if openParenthesisQty == closeParenthesisQty and openParenthesisQty > 0:
      if line[i + 1:].strip().startswith(','):
        return False
      break
  return True

def isInitialization(lines, currentIndex,currentLine):
# true -- be initialised or skip
# false -- be not initialised
  lengthOfLines = len(lines)
  #pointer,array,reference-- skip
  if strcmp.Search(r'^\*+', currentLine.strip()) or \
  strcmp.Search(r'^&+', currentLine.strip()) or \
  strcmp.Search(r'^\s*(\b\w+\b)\s*\[', currentLine) or \
  strcmp.Search(r'^\s*(\b\w+\b)\s*::\s*(\b\w+\b)\s*\[', currentLine):
    return True,currentIndex
  # current line has =   -- be initialised
  elif strcmp.Search(r'^\s*(\b\w+\b)\s*=', currentLine):
    return True,currentIndex
  elif strcmp.Search(r'^\s*(\b\w+\b)\s*\(', currentLine):
    return True,currentIndex
  elif strcmp.Search(r'^\s*(\b\w+\b)\s*::\s*(\b\w+\b)\s*=', currentLine):
    return True,currentIndex
  elif strcmp.Search(r'^\s*(\b\w+\b)\s*::\s*(\b\w+\b)\s*\(', currentLine):
    return True,currentIndex
  if currentIndex == lengthOfLines -1:
    return False, currentIndex
  # ,后直接接单词时，currentIndex为变量的行号;否则，下一个非空白行的行号是变量所在行的行号
  if (not currentLine.strip()) or currentLine.strip() == '\\':
    variableIndex = -1
  else:
    variableIndex = currentIndex
  templine = currentLine
  for i in xrange(currentIndex + 1, lengthOfLines):
    line = lines[i].strip()
    if common.IsBlankLine(line):
      continue
    if variableIndex == -1:
      variableIndex = i
    templine += line
  if strcmp.Search(r'^\*+', templine.strip()) or \
  strcmp.Search(r'^&+', templine.strip()) or \
  strcmp.Search(r'^\s*(\b\w+\b)\s*\[', templine) or \
  strcmp.Search(r'^\s*(\b\w+\b)\s*::\s*(\b\w+\b)\s*\[', templine):
    return True,variableIndex
  elif strcmp.Search(r'^\s*(\b\w+\b)\s*=', templine):
    return True,variableIndex
  elif strcmp.Search(r'^\s*(\b\w+\b)\s*\(', templine):
    return True,variableIndex
  elif strcmp.Search(r'^\s*(\b\w+\b)\s*::(\b\w+\b)\s*=', templine):
    return True,variableIndex
  elif strcmp.Search(r'^\s*(\b\w+\b)\s*::(\b\w+\b)\s*\(', templine):
    return True,variableIndex
  elif strcmp.Search(r'^\s*(\b\w+\b)\s*\[', templine) or strcmp.Search(r'^\s*(\b\w+\b)\s*::(\b\w+\b)\s*\[', templine):
    return True,variableIndex
  else:
    return False,variableIndex

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
  commaCheckstartLno = 0
  for i in xrange(lengthOfLines):
    commaCheckstartLno = i
    line = blockLines[i].replace(' ','').replace('\t','')
    if not line:
      continue
    isInitialised,variableIndex = isInitialization(blockLines, i, line)
    if not isInitialised:
      errorLnoList.append(i)
    break
  for i in xrange(commaCheckstartLno,lengthOfLines):
    line = blockLines[i].replace(' ','').replace('\t','')
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
    while commaIndex > -1:
      if isParameter(line[0:commaIndex],tempOpenParenthesisQty,tempCloseParenthesisQty) or \
         isInCurlyBraceBlock(line[0:commaIndex],tempOpenCurlyBraceQty,tempCloseCurlyBraceQty):
        if commaIndex == (lineLength - 1):
          commaIndex = -1
        else:
          if line[commaIndex + 1:].find(',') == -1:
            commaIndex = -1
          else:
            commaIndex = line[commaIndex + 1:].find(',') + commaIndex + 1
        continue
      isInitialised,variableIndex = isInitialization(blockLines, i, line[commaIndex + 1:])
      if isInitialised:
        if line[commaIndex + 1:].find(',') == -1:
          commaIndex = -1
        else:
          commaIndex = line[commaIndex + 1:].find(',') + commaIndex + 1
        continue
      else:
        if not (variableIndex in errorLnoList):
          errorLnoList.append(variableIndex)
        if line.endswith(',') and commaIndex != lineLength - 1:
          commaIndex = lineLength - 1
        else:
          commaIndex = -1
  return errorLnoList


def checkStructEnumUnionDeclare(typeWord, lines, startLno, targetType):
  lengthOfLines = len(lines)
  index = lines[startLno].find(typeWord)
  line = lines[startLno][index:]
  endlno = -1
  errorLnoList = []
  openCurlyBraceQty = 0
  closeCurlyBraceQty = 0
  type = ''
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
    if typeWord != targetType:
      return True,type,endlno,errorLnoList
    templineForType = templine[0:templine.find('{')]
    if templineForType.find('::') == -1:
      type = m.group(1)
    else:
      type = templineForType.replace(typeWord,'').strip()
    if openCurlyBraceQty != closeCurlyBraceQty:
      return True,type,endlno,errorLnoList
    findDeclareEndCloseBraceIndex = False
    declareEndCloseBraceIndex = line.find('}')
    while not findDeclareEndCloseBraceIndex:
      if line[0:declareEndCloseBraceIndex + 1].count('{') == line[0:declareEndCloseBraceIndex + 1].count('}'):
        findDeclareEndCloseBraceIndex = True
      elif line[declareEndCloseBraceIndex + 1:].find('}') != -1:
        declareEndCloseBraceIndex = line[declareEndCloseBraceIndex + 1:].find('}') + declareEndCloseBraceIndex + 1
    declareEndCloseBraceLno = startLno + line[0:declareEndCloseBraceIndex + 1].count(' \n')
    if line[declareEndCloseBraceIndex + 1:].find('*') == -1:
      return True,type,endlno,errorLnoList
    line = line[0:len(line) - 1]
    tempList = getErrorLnoListFromDefineBlock(line[declareEndCloseBraceIndex + 1:].split(' \n'))
    for tempLno in tempList:
      errorLnoList.append(tempLno + declareEndCloseBraceLno)
    return True,type,endlno,errorLnoList
  else:
    if typeWord != targetType:
      return False,type,-1,errorLnoList
    m = strcmp.Search(r'^' + typeWord + r'\s+(\b\w+\b)\s+(\b\w+\b)', templine.replace('*', ' ').replace('&', ' '))
    if m:
      type = m.group(1)
    return False,type,-1,errorLnoList



def checkVariableDefinition(typeWord, lines, startLno):
  lengthOfLines = len(lines)
  index = lines[startLno].find(typeWord)
  line = lines[startLno][index:]
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
    tempLine = lines[i]
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
  if not strcmp.Search(r'^' + typeWord + r'\s+(\w+)', line.replace('\n',' ').replace('*',' ').replace('&',' ')):
    return errorLnoList
  line = line[0:len(line) - 1]
  tempList = getErrorLnoListFromDefineBlock(line[len(typeWord):].split(' \n'))
  for tempLno in tempList:
    errorLnoList.append(tempLno + startLno)
  return errorLnoList

def isClassMember(currentLine, classCount, preOpenCurlyBraceQty, preCloseCurlyBraceQty):
  currentOpenCurlyBraceQty = currentLine.count('{')
  currentCloseCurlyBraceQty = currentLine.count('}')
  depth = preOpenCurlyBraceQty + currentOpenCurlyBraceQty - preCloseCurlyBraceQty - currentCloseCurlyBraceQty
  if depth == 0:
    return False,0
  elif depth == classCount:
    return True,classCount
  elif depth > classCount:
    return False,classCount
  else:
    return True,depth

def getClassMemberSkipLno(lines,startLno):
  openCurlyBraceQty = 0
  closeCurlyBraceQty = 0
  lengthOfLines = len(lines)
  skipToLno = 0
  for i in xrange(startLno, lengthOfLines):
    skipToLno = i
    if common.IsBlankLine(lines[i]):
      continue
    if strcmp.Search(r'^\s*#', lines[i]):
      continue
    openCurlyBraceQty = openCurlyBraceQty + lines[i].count('{')
    closeCurlyBraceQty = closeCurlyBraceQty + lines[i].count('}')
    if openCurlyBraceQty == closeCurlyBraceQty and lines[i].strip().endswith(';'):
      break
    if openCurlyBraceQty > 0:
      break
  # return value skipLno,boolean(True: class declare ,have brace;False class member )
  # class A a;----return skipToLno,False
  # class A
  #
  # {         ----return startLno+1,True
  if openCurlyBraceQty > 0:
    return skipToLno - 1,True
  else:
    return skipToLno, False
      

def CheckCSC070004(filename, file_extension, clean_lines, rawlines, nesting_state, ruleCheckKey, Error, cpplines, fileErrorCount):
  errorMessage = 'Code Style Rule: An enum variable must be initialized at the declaration.'
  if file_extension != "cpp":
    return
  particularTypeList = []
  openParenthesisQty = 0
  closeParenthesisQty = 0
  tempOpenParenthesisQty = 0
  tempCloseParenthesisQty = 0
  openClassCount = 0
  openCurlyBraceQty = 0
  closeCurlyBraceQty = 0
  tempOpenCurlyBraceQty = 0
  tempCloseCurlyBraceQty = 0
  lines = clean_lines.elided
  isEnumDeclare = False
  strutsEnumUnionOpenLno = 0
  regExp = ''
  skipEndLno = -1
  skipDefineEndLno = -1
  skipTemplateEndLno = -1
  for i in xrange(clean_lines.NumLines()):
    if i == 70:
      pass
    #null line skip
    if common.IsBlankLine(lines[i]):
      continue
    #define line skip
    if i <= skipDefineEndLno:
      continue 
    if strcmp.Search(r'^\s*#\s*define\s+', lines[i]):
      skipDefineEndLno = getDefineMacroEndNo(lines, i)
      continue
    # line start with # skip;
    # 下面的情形也 skip
    # #pragma message ("BSPDATA_SIZE="STRINGIFY(BSPDATA_SIZE)\
    # " BSPA_ADDR="STRINGIFY(BSPDATA_A_ADDRESS)\
    # " BSPB_ADDR="STRINGIFY(BSPDATA_B_ADDRESS))
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
    if strcmp.Search(r'^\s*class\s+', strcmp.Sub(r'(public:|private:|protected:)', '', lines[i])):
      if openClassCount == 0:
        openCurlyBraceQty = 0
        closeCurlyBraceQty = 0
        tempOpenCurlyBraceQty = 0
        tempCloseCurlyBraceQty = 0
      skipEndLno,isClassMemberDefinition = getClassMemberSkipLno(lines, i)
      if isClassMemberDefinition:
        openClassCount = openClassCount + 1
    if openClassCount > 0:
      tempOpenCurlyBraceQty = openCurlyBraceQty
      tempCloseCurlyBraceQty = closeCurlyBraceQty
      openCurlyBraceQty = openCurlyBraceQty + lines[i].count('{')
      closeCurlyBraceQty = closeCurlyBraceQty + lines[i].count('}')
    if i <= skipEndLno:
      continue
    m = strcmp.Search(r'(\btypedef\b\s+(\benum\b))\s*(\w*)\s*{*', lines[i].replace('*',' ').replace('&',' '))
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
      isTypedefParticularType,skipEndLno,typeList = getNicknameIfTypedefAndPaticulartypeInTwoLine(lines, i)
      if isTypedefParticularType:
        for typeListItem in typeList:
          if not (typeListItem in particularTypeList):
            if not regExp:
              regExp += r'\b' + typeListItem + r'\b'
            else:
              regExp += r'|\b' + typeListItem + r'\b'
            particularTypeList.append(typeListItem)
      else:
        skipEndLno = getTypedefBaseTypeEndLno(lines, i)
      continue
    isClassMemberVarible = False
    classDepth = 0
    m = strcmp.Search(r'(\bstruct\b|\bunion\b|\benum\b)', lines[i])
    if m:
      if openClassCount > 0:
        isClassMemberVarible,classDepth=isClassMember(lines[i][0:lines[i].find(m.group(1))], \
                                                      openClassCount, \
                                                      tempOpenCurlyBraceQty, \
                                                      tempCloseCurlyBraceQty)
        openClassCount = classDepth
      if isParameter(lines[i][0:lines[i].find(m.group(1))], tempOpenParenthesisQty, tempCloseParenthesisQty):
        continue
      if isFunctionDeclare(m.group(1), lines, i):
        continue
      isEnumDeclare,declareType,skipEndLno,errorLnoList = checkStructEnumUnionDeclare(m.group(1), lines, i, 'enum')
      if isEnumDeclare:
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
        if openClassCount > 0 and isClassMemberVarible:
          continue
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

    if len(particularTypeList) > 0:
      m = strcmp.Search(r'(' + regExp + r')\s*\w*\s*', lines[i].replace('*',' '))
      if m:
        if openClassCount > 0:
          isClassMemberVarible,classDepth=isClassMember(lines[i][0:lines[i].find(m.group(1))], \
                                                        openClassCount, \
                                                        tempOpenCurlyBraceQty, \
                                                        tempCloseCurlyBraceQty)
          openClassCount = classDepth
          if isClassMemberVarible:
            continue
        if isParameter(lines[i][0:lines[i].find(m.group(1))], tempOpenParenthesisQty, tempCloseParenthesisQty):
          continue
        if isFunctionDeclare(m.group(1), lines, i):
          continue
        errorLnoList = checkVariableDefinition( m.group(1), lines, i)
        for errorLno in errorLnoList:
          Error(filename, lines, errorLno, ruleCheckKey, 3,errorMessage)
        continue
    if openClassCount > 0:
      depth = openCurlyBraceQty - closeCurlyBraceQty
      if depth < openClassCount:
        openClassCount = depth
    