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
  #查找template<....>右尖括号所在的行号
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

def getNicknameFromTypedefBaseType(lines, startLno):
  openParenthesisQty = 0
  closeParenthesisQty = 0
  lengthOfLines = len(lines)
  line = lines[startLno][lines[startLno].find('typedef'):]
  nicknameList = []
  #找到typedef结尾的行的行号
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
  #如果typedef中有括号，说明是复杂的表达式定义，不是typedef int INT;这种格式，skip
  if openParenthesisQty > 0:
    return nicknameList,endLno
  line = line.replace(';','').replace('*',' ').replace('&',' ')
  #去掉方括号及其中的内容，比如去掉[limit::max]
  line = strcmp.Sub(r'\[((\w)|(:)|(\+)|(\-)|(\s)|(/)|(\*))*\]','',line)
  tempList = line.split(',')
  # 解析别名，并保存起来,比如从 typedef int PINT,QINT中得到 PINT和 QINT并保存起来
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
  if openCurlyBraceQty != closeCurlyBraceQty or (not lines[endLno].rstrip().endswith(';')):
    return nicknameList, lengthOfLines
  # typedef struct A{int a} *a1,&a2; --> typedef struct A *a1,&a2;
  if openCurlyBraceQty > 0:
    line = line[0:line.find('{')] + ',' + line[line.rfind('}') + 1:]
  # typedef struct A *a1,&a2; --> typedef struct A a1,a2
  line = line.replace(';','').replace('*',' ').replace('&',' ')
  #如果typedef中有括号，说明是复杂的表达式定义，不是typedef int INT;这种格式，skip
  if line.find('(') > 0:
    return nicknameList, endLno
  #去掉方括号及其中的内容，比如去掉[limit::max]
  line = strcmp.Sub(r'\[((\w)|(:)|(\+)|(\-)|(\s)|(/)|(\*))*\]','',line)
  # 解析别名，并保存起来,比如从typedef struct A a1,a2中得到 a1和a2并保存起来
  tempList = line.split(',')
  for i in xrange(len(tempList)):
    if i == 0:
      tempArray = tempList[i].replace(particularType, ' ').split()
      for tempArrayItem in tempArray:
        nicknameList.append(tempArrayItem)
    else:
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
    m = strcmp.Search(r'^\s*(\bstruct\b|\bunion\b|\benum\b)', lines[i])
    if m:
      nicknameList,typedefSkipEndLno = getNickNameFromTypedefParticularType(m.group(1), lines, i)
      return True,typedefSkipEndLno,nicknameList
    else:
      return False,-1,nicknameList
  return True,endLno,nicknameList

def isFunctionDeclare(typeWord, lines, startLno):
  #返回值说明：是否是函数定义或声明，function()中左圆括号所在的行号，function()中右圆括号所在的行号，是否发生错误
  openCurlyBraceQty = 0
  closeCurlyBraceQty = 0
  openParenthesisQty = 0
  closeParenthesisQty = 0
  level1OpenParenthesisLineNo = -1
  levelCloseParenthesisLineNo = -1
  lengthOfLines = len(lines)
  index = lines[startLno].find(typeWord)
  line = lines[startLno][index:]
  endLineNo = lengthOfLines
  for i in xrange(startLno, lengthOfLines):
    endLineNo = i
    if common.IsBlankLine(lines[i]):
      continue
    if strcmp.Search(r'^\s*#', lines[i]):
      continue
    if i != startLno:
      line += ' ' + lines[i]
      openCurlyBraceQty = openCurlyBraceQty + lines[i].count('{')
      closeCurlyBraceQty = closeCurlyBraceQty + lines[i].count('}')
      openParenthesisQty = openParenthesisQty + lines[i].count('(')
      closeParenthesisQty = closeParenthesisQty + lines[i].count(')')
    else:
      openCurlyBraceQty = openCurlyBraceQty + line.count('{')
      closeCurlyBraceQty = closeCurlyBraceQty + line.count('}')
      openParenthesisQty = openParenthesisQty + line.count('(')
      closeParenthesisQty = closeParenthesisQty + line.count(')')
    if level1OpenParenthesisLineNo == -1 and openParenthesisQty > 0:
      level1OpenParenthesisLineNo = i
    if levelCloseParenthesisLineNo == -1 and closeParenthesisQty > 0 and openParenthesisQty > 0:
      levelCloseParenthesisLineNo = i
    if openCurlyBraceQty == closeCurlyBraceQty and lines[i].rstrip().endswith(';') and openCurlyBraceQty == 0:
      break
    if openCurlyBraceQty == closeCurlyBraceQty and openCurlyBraceQty > 0:
      break
  #没有括号，说明不是函数
  if level1OpenParenthesisLineNo == -1:
    return False,level1OpenParenthesisLineNo,levelCloseParenthesisLineNo,False
  #统计的左右圆括号数量不一致，说明代码有问题，不check，返回错误
  if openParenthesisQty != closeParenthesisQty:
    return False,level1OpenParenthesisLineNo,levelCloseParenthesisLineNo,True
  #统计的左右圆括号数量一致，但是最后的右园括号那行，左圆括号在右圆括号后面，说明代码有问题，不check，返回错误
  elif lines[levelCloseParenthesisLineNo].rfind(')') < lines[levelCloseParenthesisLineNo].rfind('('):
    return False,level1OpenParenthesisLineNo,levelCloseParenthesisLineNo,True
  #check 第一个左圆括号前面的内容
  openParenthesisIndex = line.find('(')
  checkTargetLine = line[0:openParenthesisIndex].replace('&',' ').replace('*',' ').strip()
  #第一个左圆括号前面有大括号，逗号(int Map<T,T>::AAA中的逗号除外），右圆括号，说明不是函数
  if checkTargetLine.find('{') > -1 or checkTargetLine.find('}') > -1 or strcmp.Sub(r'<((\w)|(:)|(,)|(\s))*>','',checkTargetLine).find(',') > -1 or checkTargetLine.find(')') > -1:
    return False,level1OpenParenthesisLineNo,levelCloseParenthesisLineNo,False
  #第一个左圆括号前面有等号，且没有operator,说明不是函数
  if checkTargetLine.find('=') > -1 and checkTargetLine.find('operator') == -1:
    return False,level1OpenParenthesisLineNo,levelCloseParenthesisLineNo,False
  #左圆括号前面是int Map<T1,T2>::size
  m = strcmp.Search(r'^((\bvoid\b|\b' + typeWord + r'\b)\s+(\b\w+\b)\<(,|\w|\s)+\>::\w+\s*)', checkTargetLine)
  if m:
    #第一个左圆括号前面的内容类似int Map<T1,T2>::size这种格式，说明是函数
    if len(m.group(1)) == len(checkTargetLine):
      return True,level1OpenParenthesisLineNo,levelCloseParenthesisLineNo,False
    #第一个左圆括号前面的内容类似int Map<T1,T2>::operator +=这种格式，说明是函数
    m = strcmp.Search(r'^::(\boperator\b)\s*', checkTargetLine[checkTargetLine.find('::'):])
    if m:
      return True,level1OpenParenthesisLineNo,levelCloseParenthesisLineNo,False
  #左圆括号前面是int Map::size  or int Map::size
  templine = ''
  m = strcmp.Search(r'^((\bvoid\b|\b' + typeWord + r'\b)\s+\w+::(\b\w+\b)\s*)', checkTargetLine)
  if m:
    templine = m.group(1)
  else:
    m = strcmp.Search(r'^((\bvoid\b|\b' + typeWord + r'\b)\s+(\b\w+\b)\s*)', checkTargetLine)
    if m:
      templine = m.group(1)
  if templine:
    #第一个左圆括号前面的内容类似int String::AA or int AA这种格式，说明是函数
    if len(templine) == len(checkTargetLine):
      return True,level1OpenParenthesisLineNo,levelCloseParenthesisLineNo,False
    #第一个左圆括号前面的内容类似int String::operator +=这种格式，说明是函数
    m = strcmp.Search(r'^((\bvoid\b|\b' + typeWord + r'\b)\s+\w+::(\boperator\b)\s*)', checkTargetLine)
    if m:
      return True,level1OpenParenthesisLineNo,levelCloseParenthesisLineNo,False
    #第一个左圆括号前面的内容类似int operator +=这种格式，说明是函数
    m = strcmp.Search(r'^((\bvoid\b|\b' + typeWord + r'\b)\s+(\boperator\b)\s*)', checkTargetLine)
    if m:
      return True,level1OpenParenthesisLineNo,levelCloseParenthesisLineNo,False
  #其他情况被认为不是函数
  return False,level1OpenParenthesisLineNo,levelCloseParenthesisLineNo,False

def checkStructEnumUnionDeclare(typeWord, lines, startLno):
  #返回值说明：是否是特殊类型说明，类型，类型定义的最后一行的行号，是否发生错误
  lengthOfLines = len(lines)
  index = lines[startLno].find(typeWord)
  line = lines[startLno][index:].replace('*',' ').replace('&',' ')
  endLineNo = -1
  openCurlyBraceQty = 0
  closeCurlyBraceQty = 0
  type = ''
  #找到定义的最后一行，即；所在的行的行号
  for i in xrange(startLno, lengthOfLines):
    endLineNo = i
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
    if openCurlyBraceQty == closeCurlyBraceQty and tempLine.rstrip().endswith(';'):
      break
  templine = line.replace('\n',' ')
  m = strcmp.Search(r'^' + typeWord + r'\s*(\w+)\s*{+', templine.replace('::',''))
  if m:
    # 如果左右大括号数量不同或者找到的最后一行不是以分号结尾，说明代码写法有问题，返回错误
    if openCurlyBraceQty != closeCurlyBraceQty or (not lines[endLineNo].rstrip().endswith(';')):
      return True,type,endLineNo,True
    templineForType = templine[0:templine.find('{')]
    if templineForType.find('::') == -1:
      type = m.group(1)
    else:
      type = templineForType.replace(typeWord,'').strip()
    return True,type,endLineNo,False
  else:
    return False,type,endLineNo,False

def checkNewLine(filename, lines, startLineNo, endLineNo, ruleCheckKey, Error, cpplines, fileErrorCount):
  errMessage = 'Code Style Rule: When a function declaration/definition is too long, it should be wrapped before the type of a parameter. For example, funcA(int a, int b) should wrap before "int b".'
  checkStartLineNo = startLineNo + 1
  maxLimit = endLineNo + 1
  skipEndLno = -1
  previousLine = lines[startLineNo].strip()
  for i in xrange(checkStartLineNo, maxLimit):
    errorMessage = ''
    #空白行--skip
    if common.IsBlankLine(lines[i]):
      continue
    if i <= skipEndLno:
      continue
    #宏定义--skip
    if strcmp.Search(r'^\s*#\s*define\s+', lines[i]):
      skipEndLno = common.getDefineMacroEndLineNo(lines, i)
      continue
    #预定义--skip
    if strcmp.Search(r'^\s*#', lines[i]):
      skipEndLno = common.getDefineMacroEndLineNo(lines, i)
      continue
    line = lines[i].strip()
    # int func(int a \n\t )不报错;
    if line.startswith(')'):
      previousLine = lines[i].strip()
      continue
    # int func(\n \tint a)不报错;
    if previousLine.endswith('('):
      previousLine = lines[i].strip()
      continue
    # int func(int \n\t&a)报错;int func(int \n\t*a)报错;
    if line.startswith('&') or line.startswith('*'):
      Error(filename, lines, i, ruleCheckKey, 3, errMessage)
    #int func(int  \n\ta,int b )报错
    elif not previousLine.endswith(','):
      Error(filename, lines, i, ruleCheckKey, 3, errMessage)
    #保存当前行，目的是下一行是以&开头时，判断&是一元操作符，还是二元操作符
    previousLine = lines[i].strip()

def CheckCSC020003(filename, file_extension, clean_lines, rawlines, nesting_state, ruleCheckKey, Error, cpplines, fileErrorCount):
  errorMessage = 'Code Style Rule: When a function declaration/definition is too long, it should be wrapped before the type of a parameter. For example, funcA(int a, int b) should wrap before "int b".'
  particularTypeList = []
  lines = clean_lines.elided
  isStrutsEnumUnionDeclare = False
  strutsEnumUnionOpenLno = 0
  regExp = ''
  skipEndLno = -1
  i = 0
  while i < clean_lines.NumLines():
    #null line skip
    if common.IsBlankLine(lines[i]):
      i += 1
      continue
    #define line skip
    if strcmp.Search(r'^\s*#\s*define\s+', lines[i]):
      i = common.getDefineMacroEndLineNo(lines, i) + 1
      continue
    # line start with # skip
    if strcmp.Search(r'^\s*#', lines[i]):
      i = common.getDefineMacroEndLineNo(lines, i) + 1
      continue
    # template declare line skip
    m = strcmp.Search(r'^\s*template\s*<', lines[i])
    if m:
      if i == -1:
        break
      i = getTemplateEndLno(lines, i) + 1
      continue
    # check typedef,将定于的类型别名存放到particularTypeList中
    # typedef特殊类型（结构体，联合，枚举）check
    m = strcmp.Search(r'(\btypedef\b\s+(\bstruct\b|\bunion\b|\benum\b))\s*(\w+)\s*{*', lines[i].replace('*',' ').replace('&',' '))
    if m:
      typeList,skipEndLno = getNickNameFromTypedefParticularType(m.group(1), lines, i)
      for typeListItem in typeList:
        if not (typeListItem in particularTypeList):
          if not regExp:
            regExp += r'\b' + typeListItem + r'\b'
          else:
            regExp += r'|\b' + typeListItem + r'\b'
          particularTypeList.append(typeListItem)
      i = skipEndLno + 1
      continue
    # typedef单独在某一行  或者 typedef基本类型 时
    elif strcmp.Search(r'\btypedef\b', lines[i]):
      # check typedef的目标是特殊类型还是基本类型
      isTypedefParticularType,skipEndLno,typeList =getNicknameIfTypedefAndPaticulartypeInTwoLine(lines, i)
      if isTypedefParticularType:
        # 特殊类型
        for typeListItem in typeList:
          if not (typeListItem in particularTypeList):
            if not regExp:
              regExp += r'\b' + typeListItem + r'\b'
            else:
              regExp += r'|\b' + typeListItem + r'\b'
            particularTypeList.append(typeListItem)
        i = skipEndLno + 1
        continue
      else:
        # 基本类型
        typeList,skipEndLno=getNicknameFromTypedefBaseType(lines, i)
        for typeListItem in typeList:
          if not (typeListItem in particularTypeList):
            if not regExp:
              regExp += r'\b' + typeListItem + r'\b'
            else:
              regExp += r'|\b' + typeListItem + r'\b'
            particularTypeList.append(typeListItem)
        i = skipEndLno + 1
        continue
    # 特殊类型 struct AA::aa; 或者 struct A;这种声明，直接把声明的类型存放到particularTypeList中
    m = strcmp.Search(r'(\bstruct\b|\bunion\b|\benum\b)\s+(\w+|\w+::\w+);', lines[i])
    if m:
      if not (m.group(2) in particularTypeList):
        if not regExp:
          regExp += r'\b' + m.group(2) + r'\b'
        else:
          regExp += r'|\b' + m.group(2) + r'\b'
        particularTypeList.append(m.group(2))
      i += 1
      continue
    # 特殊类型（结构体，联合，枚举）定义时，将其类型保存到particularTypeList中
    m = strcmp.Search(r'(\bstruct\b|\bunion\b|\benum\b)', lines[i])
    if m:
      isStrutsEnumUnionDeclare,declareType,skipEndLno,hasError = checkStructEnumUnionDeclare(m.group(1), lines, i)
      #特殊类型（结构体，联合，枚举）定义时
      if isStrutsEnumUnionDeclare:
        if hasError:
          break
        else:
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
        #跳到特殊类型定义的下一行去
        i = skipEndLno + 1
        continue
    # check 是否含有基本类型的关键字
    baseIndex = -1
    particularIndex = -1
    checkTypeword = ''
    m = strcmp.Search(r'(\bvoid\b|\bbool\b|\bchar\b|\bwchar_t\b|\bshort\b|\bint\b|\blong\b|\bfloat\b|\bdouble\b)\s*\w*\s*', lines[i].replace('*',' '))
    if m:
      checkTypeword = m.group(1)
      baseIndex = lines[i].replace('*',' ').find(checkTypeword)
      if len(particularTypeList) > 0:
        # check 是否含有特殊类型的关键字
        m = strcmp.Search(r'(' + regExp + r')\s*\w*\s*', lines[i].replace('*',' '))
        #同时找到基本类型和特殊类型关键字时，哪个在前面，以哪个为基准check函数
        if m:
          particularIndex = lines[i].replace('*',' ').find(m.group(1))
          if particularIndex < baseIndex and particularIndex > -1:
            checkTypeword = m.group(1)
    #没有找到基本类型
    else:
      if len(particularTypeList) == 0:
        i += 1
        continue
      # check 是否含有特殊类型
      m = strcmp.Search(r'(' + regExp + r')\s*\w*\s*', lines[i].replace('*',' '))
      if m:
        checkTypeword = m.group(1)
        particularIndex = lines[i].replace('*',' ').find(checkTypeword)
    if baseIndex > -1 or particularIndex > -1:
      #判断是否是函数声明定义，左右圆括号所在的行号，是否发生错误
      isFunction,checkStartLineNo,checkEndLineNo,hasError = isFunctionDeclare(checkTypeword, lines, i)
      if hasError:
        break
      if isFunction:
        #func()左右圆括号所在的行号相同，说明该函数（）中间没有换行
        if checkStartLineNo == checkEndLineNo:
          i = checkEndLineNo + 1
          continue
        #check换行
        checkNewLine(filename, lines, checkStartLineNo, checkEndLineNo, ruleCheckKey, Error, cpplines, fileErrorCount)
        i = checkEndLineNo + 1
        continue
    i += 1
    