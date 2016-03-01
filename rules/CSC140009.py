#!/usr/bin/python  
#-*- coding: utf-8 -*-
'''
Created on 2014-12-16

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
  '''查找template<....>右尖括号所在的行号
  Args:
    lines:a copy of all lines without strings and comments
    startLno:开始check的行号
  Returns:
           返回template<....>右尖括号所在的行号
  '''
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
  '''查找typedef 形式定义的基本类型的同义词
  Args:
    lines:a copy of all lines without strings and comments
    startLno:开始check的行号
  Returns:
           返回typedef 形式定义的基本类型的同义词
  '''
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
  '''查找typedef 形式定义的特殊类型（结构体，联合，枚举）的同义词
  Args:
    particularType:特殊类型关键字
    lines:a copy of all lines without strings and comments
    startLno:开始check的行号
  Returns:
           返回typedef 形式定义的特殊类型（结构体，联合，枚举）的同义词,typedef的结尾的行号
  '''
  openCurlyBraceQty = 0
  closeCurlyBraceQty = 0
  lengthOfLines = len(lines)
  nicknameList = []
  line = lines[startLno][lines[startLno].find(particularType):]
  endLno = -1
  # 查找typedef语句的结束行(通过左右大括号的个数及是否以分号结尾判断)
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
  '''查找typedef 形式定义的特殊类型（结构体，联合，枚举）的同义词
         typedef 与结构体，联合，枚举关键字不在同一行上
  Args:
    lines:a copy of all lines without strings and comments
    startLno:开始check的行号
  Returns:
           返回是否是特殊类型,typedef 形式定义的特殊类型（结构体，联合，枚举）的同义词,typedef的结尾的行号
  '''
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

def isFunctionDeclaration(lines, startLno):
  '''在已知是函数的情况下，判断是否是函数声明还是函数定义
  Args:
    lines:a copy of all lines without strings and comments
    startLno: function() )所在的行的行号
  Returns:
           boolean: True--函数声明; False--函数定义
           int: 函数声明时，function() )所在的行的行号；函数定义时，返回}所在行的行号
           当文件格式不正常，无法正常判断时，返回 False，-1
  '''
  closeParenthesisIndex = lines[startLno].find(')')
  # 找不到)的位置，文件不正常
  if closeParenthesisIndex == -1:
    return False, -1
  # )所在行,)之后不为空白，且)后不是;，说明这是函数声明
  if lines[startLno].endswith('\\'):
    tempLine = lines[startLno][lines[startLno].find(')') + 1:len(lines[startLno]) - 1].strip()
  else:
    tempLine = lines[startLno][lines[startLno].find(')') + 1:].strip()
  if tempLine and tempLine.startswith(';'):
    return True, startLno
  # )之后不为空白,但是不是;也不是{,文件不正常
  if tempLine and (not tempLine.startswith('{')):
    return False, -1

  i = startLno
  lengthOfLines = len(lines)
  openCurlyBraceLineNo = -1
  while i < lengthOfLines:
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
      i += 1
      continue
    if i == startLno:
      pass
    # 如果有换行符，去掉换行符
    elif lines[i].endswith("\\"):
      tempLine = lines[i][:len(lines[i]) -1].strip()
    else:
      tempLine = lines[i].strip()
    # 如果改行只有换行符和空格而没有代码时
    if common.IsBlankLine(tempLine):
      i += 1
      continue
    # )之后不为空白,是{,说明是函数定义
    if tempLine.startswith('{'):
      openCurlyBraceLineNo = i
      break
    # )之后不为空白,是;,说明是函数声明
    elif tempLine.startswith(';'):
      return True, startLno
    # )之后不为空白,但是不是;也不是{,文件不正常
    else:
      return False, -1

  if openCurlyBraceLineNo == -1:
    return False, -1
  # 查找{对应的}所在行的行号
  i = openCurlyBraceLineNo
  openCurlyBraceQty = 0
  closeCurlyBraceQty = 0
  closeCurlyBracelineNo = -1
  while i < lengthOfLines:
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
      i += 1
      continue
    openCurlyBraceQty = openCurlyBraceQty + lines[i].count('{')
    closeCurlyBraceQty = closeCurlyBraceQty + lines[i].count('}')
    if openCurlyBraceQty == closeCurlyBraceQty and openCurlyBraceQty > 0:
      closeCurlyBracelineNo = i
      break
    i += 1

  # 找不到)的位置，文件不正常
  if openCurlyBraceQty != closeCurlyBraceQty or openCurlyBraceQty == 0 or closeCurlyBraceQty == 0:
    return False, -1
  # 返回：函数定义,}所在行的行号
  return False, closeCurlyBracelineNo

def isFunction(typeWord, lines, startLno, startIndex):
  '''判断是否是函数声明或者是函数定义
  Args:
    typeWord: 关键词
    lines:a copy of all lines without strings and comments
    startLno:开始check的行号
    startIndex:开始行中开始查找的位置
  Returns:
           返回是否是函数声明或者函数定义,function()中左圆括号所在的行号,function()中右圆括号所在的行号,文件格式是否正常
  '''
  openCurlyBraceQty = 0
  closeCurlyBraceQty = 0
  openParenthesisQty = 0
  closeParenthesisQty = 0
  level1OpenParenthesisLineNo = -1
  levelCloseParenthesisLineNo = -1
  lengthOfLines = len(lines)
  line = lines[startLno][startIndex:]
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
  '''判断是否是特殊类型声明
  Args:
    typeWord: 关键词
    lines:a copy of all lines without strings and comments
    startLno:开始check的行号
  Returns:
           返回是否是特殊类型说明，类型，类型定义的最后一行的行号，是否发生错误
  '''
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

def checkComment(filename, lines, rawLines, startLineNo, ruleCheckKey, Error, cpplines, fileErrorCount):
  '''check注释(概要说明与详细说明之间必须空一行)
     --只check/**/这种格式的注释
  Args:
    filename:文件名
    lines:a copy of all lines without strings and comments
    rawlines：all the lines without processing
    startLineNo： the line number of the end of comment 
    ruleCheckKey:ruleid
    Error: error output method
  '''
  # 写法示例
  #/**
  #   * 函数概要说明。
  #   *
  #   * 函数详细说明。写法和Class详细说明相同。
  #   *
  #   * @param [IN] path  : 年。公历。（范围：1~9999、单位：年）
  #   * @param [IN] month : 月。（范围：1~12、单位：月）
  #   * @param [IN] day   : 日。（范围：1~31、单位：日）
  #   *
  #   * @return 返回输入日期参数对应的星期几。
  #   * @retval 0...6： 星期天...星期六
  #   * @retval 负值  : 输入参数错误
  #   *
  #   * @attention Synchronous I/F.
  #   */
  # int8_t getDayOfWeek(int8_t year, int8_t month, int8_t day);
  errorMessage = 'Code Style Rule: There should be a blank line between the "summary description" and "detailed description" in the function comment.'
  # 函数声明的前一行有代码，return
  if not common.IsBlankLine(lines[startLineNo]):
    return
  # 注释格式不是/*....*/, no check
  if not rawLines[startLineNo].rstrip().endswith('*/'):
    return
  # 从*/向前查找/*所在的行
  multiCommentStartLineNo = -1
  i = startLineNo
  while i > 0:
    if not common.IsBlankLine(lines[startLineNo]):
      break
    if rawLines[i].lstrip().startswith('/*'):
      # 避免 /*/当成一个完整的注释
      if i == startLineNo and rawLines[i].strip() =='/*/':
        pass
      # 函数声明注释都写在一行了，无法区分注释概要说明和详细说明
      elif i == startLineNo:
        return
      else:
        multiCommentStartLineNo = i
        break
    i -= 1
  # 找不到/*所在的行
  if multiCommentStartLineNo == -1:
    return
  # 查找概要说明和详细说明说在的行号
  outlineLno = -1
  detailLno = -1
  i = multiCommentStartLineNo
  while i < startLineNo:
    tempLine = strcmp.Sub(r'[\*\</]','',rawLines[i])
    # 空白行，skip
    if common.IsBlankLine(tempLine):
      i += 1
      continue
    # 当注释中有以下单词时，退出循环
    # @param,@return,@retval,@attention,@warning,@see,@bug
    if strcmp.Search(r'@(param|return|retval|attention|warning|see|bug)', rawLines[i]):
      break
    # 第一个非空行的行号赋给outlineLno
    if outlineLno == -1:
      outlineLno = i
      i += 1
      continue
    # 第2个非空行的行号赋给detailLno
    if outlineLno != -1 and detailLno == -1:
      detailLno = i
      break
  # 一个非空行也没有 或者只有一个非空行时，不需要check了
  if outlineLno == -1 or detailLno == -1:
    return
  # 概要说明与详细说明之间没有空行时，报错
  if outlineLno + 1 == detailLno:
    Error(filename, lines, outlineLno, ruleCheckKey, 3, errorMessage)

def CheckCSC140009(filename, file_extension, clean_lines, rawlines, nesting_state, ruleCheckKey, Error, cpplines, fileErrorCount):
  '''函数声明的注释要求：函数的概要说明与详细说明之间必须空一行。[必须]
  (其他规则要求概要说明只能写在一行)
  Args:
    filename:文件名
    file_extension:文件扩展名
    clean_lines:Holds 3 copies of all lines with different preprocessing applied to them
                 1) elided member contains lines without strings and comments,
                 2) lines member contains lines without comments, and
                 3) raw_lines member contains all the lines without processing.（行首以/*开头的多行注释被替换成空白）
    rawlines：all the lines without processing
    nesting_state: Holds states related to parsing braces.(cpplint中的对象，暂时未使用)
    ruleCheckKey:ruleid
    Error: error output method
  '''
  particularTypeList = []
  lines = clean_lines.elided
  isStrutsEnumUnionDeclare = False
  strutsEnumUnionOpenLno = 0
  regExp = ''
  skipEndLno = -1
  i = 0
  templateStartLno = -1
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
      i += 1
      continue
    # template declare ,goto next line
    m = strcmp.Search(r'^\s*template\s*<', lines[i])
    if m:
      if i == -1:
        break
      templateStartLno = i
      i = getTemplateEndLno(lines, i) + 1
    else:
      templateStartLno = -1
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
    checkFunctionStartIndex = -1
    checkTypeword = ''
    m = strcmp.Search(r'(\bvoid\b|\bbool\b|\bchar\b|\bwchar_t\b|\bshort\b|\bint\b|\blong\b|\bfloat\b|\bdouble\b)\s*\w*\s*', lines[i].replace('*',' '))
    if m:
      checkTypeword = m.group(1)
      checkFunctionStartIndex = m.start()
      if len(particularTypeList) > 0:
        # check 是否含有特殊类型的关键字
        m = strcmp.Search(r'(' + regExp + r')\s*\w*\s*', lines[i].replace('*',' '))
        #同时找到基本类型和特殊类型关键字时，哪个在前面，以哪个为基准check函数
        if m:
          particularIndex = m.start()
          if m.start() < checkFunctionStartIndex:
            checkFunctionStartIndex = m.start()
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
        checkFunctionStartIndex = m.start()
    # 如果找到下面的格式的代码，判断其是否是函数声明
    # int function(...)
    # struct AAA function (...)
    if checkFunctionStartIndex > -1:
      #判断是否是函数声明或定义，左右圆括号所在的行号，是否发生错误
      isFunctionDeclareOrDefinition,checkStartLineNo,checkEndLineNo,hasError = isFunction( checkTypeword, lines, i, checkFunctionStartIndex)
      if hasError:
        break
      # 是函数声明或定义
      if isFunctionDeclareOrDefinition:
        isFunctionDeclare, blockEndLineNo = isFunctionDeclaration( lines, checkEndLineNo)
        # 文件不正常, return
        if blockEndLineNo == -1:
          return
        # 函数定义
        if not isFunctionDeclare:
          i = blockEndLineNo + 1
          continue
        # 函数声明
        #check fuction declare前的注释
        if templateStartLno == -1:
          checkStartLineNo = i - 1
        else:
          checkStartLineNo = templateStartLno - 1
        checkComment(filename, lines, rawlines, checkStartLineNo, ruleCheckKey, Error, cpplines, fileErrorCount)
        i = checkEndLineNo + 1
        continue
    i += 1
    