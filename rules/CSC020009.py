#!/usr/bin/python  
#-*- coding: utf-8 -*-
'''
Created on 2014-12-15

@author: wangxc
'''
import os
import sys
syspath = os.path.dirname(os.path.dirname(__file__))
if not os.path.join(syspath, "tools") in sys.path:
  sys.path.append(os.path.join(syspath, "tools"))
import common
strcmp = common.StringCompareInfo()

def whetherHasSourceBetweenTwoLine(lines, startLineNo, startIndex, endLineNo, endIndex):
  '''检查指定的两个位置之间是否有代码{对应的}的行号和其所在行的位置
  Args:
    lines:所有行
    startLineNo:开始的行号
    startIndex:开始行中开始查找的位置
    endLineNo:结束的行号
    endIndex:结束行中开始查找的位置
  Returns:
    True：指定的两个位置之间有代码；False:指定的两个位置之间没有代码
  '''
  # 开始行，startIndex之后有代码
  if not common.IsBlankLine(lines[startLineNo][startIndex + 1:]):
    return True
  # 结束行，endIndex之前有代码
  if not common.IsBlankLine(lines[endLineNo][:endIndex]):
    return True
  i = startLineNo + 1
  while i < endLineNo:
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
    # 有代码行
    return True
  return False

def getFunctionCloseCurlyBraceInfo(lines, openCurlyBraceLno, openCurlyBraceIdx):
  '''返回{对应的}的行号和其所在行的位置
  Args:
    lines:所有行
    openParenthesisLno:{所在行的行号
    openParenthesisIdx:{在其所在行的位置
  Returns:
            返回{对应的}所在的line number和其所在行的位置；如果查不到}，则返回-1, -1
  '''
  lengthOfLines =len(lines)
  i = openCurlyBraceLno
  openCurlyBraceQty = 0
  closeCurlyBraceQty = 0
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
      i = common.getDefineMacroEndLineNo(lines, i) + 1
      continue
    if i == openCurlyBraceLno:
      checkStartIndex = openCurlyBraceIdx
    else:
      checkStartIndex = 0
    # #逐个字符累计左右大括号
    for j in xrange(checkStartIndex, len(lines[i])):
      if lines[i][j] == '{':
        openCurlyBraceQty += 1
      elif lines[i][j] == '}':
        closeCurlyBraceQty += 1
      else:
        continue
      # 左右大括号的个数相同时，返回右大括号的行号和位置
      if openCurlyBraceQty == closeCurlyBraceQty and openCurlyBraceQty > 0:
        return i, j
    i += 1
  # 如果查不到*/，则返回-1，说明文件有问题，不要再check该文件了
  return -1, -1

def getPreviousNotNullLineNo(lines, startLno):
  '''从startLno向上查找第一个非空的行
  Args:
    lines:a copy of all lines without strings and comments
    startLno:目标行
  Returns:
           第一个非空的行的行号
  '''
  lengthOfLines = len(lines)
  i = startLno - 1
  while i < lengthOfLines:
    if common.IsBlankLine(lines[i]):
      i -= 1
      continue
    elif strcmp.Search(r'^\s*#', lines[i]):
      i -= 1
      continue
    # 如果有换行符，去掉换行符
    if lines[i].endswith("\\"):
      tempLine = lines[i][:len(lines[i]) -1]
    else:
      tempLine = lines[i]
    if common.IsBlankLine(tempLine):
      i -= 1
      continue
    return i
  return -1

def getOpenParenthesisInfoByCloseParenthesis(lines, closeParenthesisLineNo, closeParenthesisIndex):
  '''查找)对应的（
  Args:
    lines:所有行
    openParenthesisLineNo: )所在行的行号
    openParenthesisIndex : )在所在行的位置
  Returns:
            (所在行的行号,(在所在行的位置--如果找不到，则返回-1，-1
  '''
  openParenthesisQty = 0
  closeParenthesisQty = 0
  i = closeParenthesisLineNo
  while i > 0:
    # line start with # skip
    if strcmp.Search(r'^\s*#', lines[i]):
      i -= 1
      continue
    #null line skip
    if common.IsBlankLine(lines[i]):
      i -= 1
      continue
    currentLine = lines[i]
    # 逐个字符对比，累计左右圆括号的数量
    startIndex = len(currentLine) - 1
    if i == closeParenthesisLineNo:
      startIndex = closeParenthesisIndex
    for j in xrange(startIndex, -1, -1):
      if currentLine[j] == '(':
        openParenthesisQty += 1
      elif currentLine[j] == ')':
        closeParenthesisQty += 1
      #左右圆括号个数相同，则返回左圆括号的lineNo,其位于所在行的位置
      if openParenthesisQty == closeParenthesisQty and openParenthesisQty > 0:
        return i, j
    i -= 1
  return -1, -1

def isFunctionDefinition(lines, openCurlyBraceLineNo, openCurlyBraceIndex):
  '''判断{是否是函数定义的第一个{
  Args:
    lines:所有行
    openCurlyBraceLineNo: {所在行的行号
    openCurlyBraceIndex : {在所在行的位置
  Returns:
            是否是函数定义(True: yes; False: no)；是函数定义的话，返回)所在的行的行号以及)的位置,是否有参数列表（True: yes; False: no）
  '''
  # {所在行,{之前不为空白，且{前不是)，说明这不是函数定义
  tempLine = lines[openCurlyBraceLineNo][:openCurlyBraceIndex].strip()
  if tempLine and (not tempLine.endswith(')')):
    return False, -1, -1, False
  # {所在行,{之前为空白
  closeParenthesisLineNo = -1
  closeParenthesisIndex = -1
  # 查找)--------------->
  # {所在行,{之前不为空白
  if tempLine:
    closeParenthesisLineNo = openCurlyBraceLineNo
    closeParenthesisIndex = lines[openCurlyBraceLineNo][:openCurlyBraceIndex].rfind(')')
  else:
    # 向上查找第一个非空的行
    i = getPreviousNotNullLineNo(lines , openCurlyBraceLineNo)
    if i == -1:
      return False, -1, -1, False
    # 如果有换行符，去掉换行符
    if lines[i].endswith("\\"):
      tempLine = lines[i][:len(lines[i]) -1].rstrip()
    else:
      tempLine = lines[i].rstrip()
    # 查看离{最近的字符是否为)
    # 离{最近的字符是),保存）的行号和位置，为判断是否为函数定义做准备
    if tempLine.endswith(')'):
      closeParenthesisLineNo = i
      closeParenthesisIndex = len(tempLine) - 1
    # 离{最近的字符不是)，说明这不是函数定义
    else:
      return False, -1, -1, False
  # 查找)<---------------
  # 查找)对应的（--------------->
  i =  closeParenthesisLineNo
  openParenthesisLineNo = -1
  openParenthesisIndex = -1
  openParenthesisLineNo,openParenthesisIndex = getOpenParenthesisInfoByCloseParenthesis(lines, closeParenthesisLineNo, closeParenthesisIndex)
  # 如果找不到)对应的(,说明不是函数定义
  if openParenthesisLineNo == -1:
    return False, -1, -1, False
  # 查找)对应的（<---------------
  # 查找(前得单词，判断其是否是关键字，如果不是，说明是函数--------------->
  i = openParenthesisLineNo
  while i > 0:
    # line start with # skip
    if strcmp.Search(r'^\s*#', lines[i]):
      i -= 1
      continue
    #null line skip
    if common.IsBlankLine(lines[i]):
      i -= 1
      continue
    if i == openParenthesisLineNo:
      tempLine = lines[i][:openParenthesisIndex]
    elif lines[i].endswith("\\"):
      tempLine = lines[i][:len(lines[i]) -1]
    else:
      tempLine = lines[i]
    # 如果改行只有换行符和空格而没有代码时
    if common.IsBlankLine(tempLine):
      i -= 1
      continue
    # 是操作符重载函数时
    # operator +=(int a, int b) {}
    if tempLine.rstrip().endswith('=') and tempLine.rfind('operator') != -1:
      return True, closeParenthesisLineNo, closeParenthesisIndex, False
    # check是不是函数定义----------->
    m = strcmp.Search(r'\b(\w+)\b\s*$', tempLine)
    # (前面是单词
    if m:
      # (前面是单词，且这些单词不是关键字时，说明该代码块是函数定义
      if m.group(1) not in ['if', 'while', 'for', 'switch']:
        # 判断是否有参数列表-------------------->
        temp = tempLine[:m.start()].strip()
        # 1)当前行，单词前不是空白
        if temp:
          # 单词前是::,没有参数列表
          if temp.endswith('::'):
            return True, closeParenthesisLineNo, closeParenthesisIndex, False
          if strcmp.Search(r'\b(public|private|protected)\b\s*\:\s*$', temp):
            return True, closeParenthesisLineNo, closeParenthesisIndex, False
          # 单词前是, or :,有参数列表
          if temp.endswith(':') or temp.endswith(','):
            return True, closeParenthesisLineNo, closeParenthesisIndex, True
          # 没有参数列表
          return True, closeParenthesisLineNo, closeParenthesisIndex, False
        # 2)当前行，单词前是空白,向上查找第一个非空的行
        j = getPreviousNotNullLineNo(lines , i)
        temp = ''
        if j > -1:
          if lines[j].endswith("\\"):
            temp = lines[j][:len(lines[j]) -1].strip()
          else:
            temp = lines[j].strip()
        # 上一个非空行是以::结尾，没有参数列表
        if temp.endswith('::'):
          return True, closeParenthesisLineNo, closeParenthesisIndex, False
        if strcmp.Search(r'\b(public|private|protected)\b\s*\:\s*$', temp):
          return True, closeParenthesisLineNo, closeParenthesisIndex, False
        # 上一个非空行是以, or :结尾,有参数列表
        if temp.endswith(':') or temp.endswith(','):
          return True, closeParenthesisLineNo, closeParenthesisIndex, True
        # 没有参数列表
        return True, closeParenthesisLineNo, closeParenthesisIndex, False
        # 判断是否有参数列表<--------------------
      # (前面是单词，且这些单词是关键字时，说明该代码块不是函数定义
      else:
        return False, -1, -1, False
    # (前面不是单词
    else:
      return False, -1, -1, False
    # check是不是函数定义<-----------
  return False, -1, -1, False
  # 查找(前得单词，判断其是否是关键字，如果不是，说明是函数<---------------

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
      i = common.getDefineMacroEndLineNo(lines, i) + 1
      continue
    else:
      break
  if i < lengthOfLines:
    return i
  else:
    return lengthOfLines - 1

def whetherCommarIsCloseAfterCloseCurlyBrace(lines, closeCurlyBraceLineNo, closeCurlyBraceIndex):
  '''判断}后面是否是逗号
  Args:
    lines:所有行
    openCurlyBraceLineNo: }所在行的行号
    openCurlyBraceIndex : }在所在行的位置
  Returns:
            True: yes; False: no
  '''
  tempLine = lines[closeCurlyBraceLineNo][closeCurlyBraceIndex + 1:].strip()
 
  if not tempLine:
    pass
  # }后面是否是逗号
  elif tempLine.startswith(','):
    return True
  # }后面是否是注释
  elif tempLine.startswith('/*'):
    pass
  else:
    return False
  i = getNextNotNullLineNo(lines, closeCurlyBraceLineNo)
  tempLine = lines[i].strip()
  # }后面是否是逗号
  if tempLine.startswith(','):
    return True
  else:
    return False
  return False

def getTemplateEndLno(lines, startLno, startIndex):
  '''从startLno向下查找template的>所在的行号
  Args:
    lines:a copy of all lines without strings and comments
    startLno:目标行
    startIndex:check start index
  Returns:
           template的>所在的行号,index
  '''
  lengthOfLines = len(lines)
  leftAngleBracketQty = 0
  rightAngleBracketQty = 0
  for i in xrange(startLno, lengthOfLines):
    if common.IsBlankLine(lines[i]):
      continue
    if strcmp.Search(r'^\s*#', lines[i]):
      continue
    if i == startLno:
      leftAngleBracketQty = leftAngleBracketQty + lines[i][startIndex:].count('<')
      rightAngleBracketQty = rightAngleBracketQty + lines[i][startIndex:].count('>') - lines[i].count('->')
    else:
      leftAngleBracketQty = leftAngleBracketQty + lines[i].count('<')
      rightAngleBracketQty = rightAngleBracketQty + lines[i].count('>') - lines[i].count('->')
    if leftAngleBracketQty == rightAngleBracketQty and leftAngleBracketQty > 0:
      closeAngleBranceIndex = lines[i].replace('->','  ').find('>')
      return i, closeAngleBranceIndex
  return -1, -1

def findClassStructDefinitionEndInfo(lines, startLineNo, startIndex, keyWord):
  '''从startLno向下查找class的}所在的行号
  Args:
    lines:a copy of all lines without strings and comments
    startLno:leyword[class]所在的行号
    startIndex: leyword[class] index
    keyWord: 关键字
  Returns:
           是否是class/struct定义,class的};(or struct 的})所在的行号,index
    (systemError: return True, -1, -1)
  '''
  openCurlyBraceQty = 0
  closeCurlyBraceQty = 0
  lengthOfLines = len(lines)
  i = startLineNo
  semicolonIndex = -1
  otherCharIndex = -1
  closeCurlyBraceIndex = -1
  colonIndex = -1
  commaIndex = -1
  while i < lengthOfLines:
    endLine = i
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
    if i == startLineNo:
      line = lines[i][startIndex:]
    else:
      line = lines[i]
    if openCurlyBraceQty == closeCurlyBraceQty and openCurlyBraceQty > 0:
      # struct
      if keyWord == 'struct':
        return True, i, closeCurlyBraceIndex
      # class
      # class A {};--是函数定义
      if line.strip().startswith(';'):
        endIndex = line.find(';')
        if i == startLineNo:
          endIndex = endIndex + startIndex
        return True, i, endIndex
      # class {} AA-- }后没有;，说明文件有问题
      else:
        return True, -1, -1
    # 逐个字符对比，累计{,}的数量
    for j in xrange(0, len(line)):
      if line[j] == '{':
        openCurlyBraceQty += 1
      elif line[j] == '}':
        closeCurlyBraceIndex = j
        closeCurlyBraceQty += 1
      elif line[j] == ':':
        colonIndex = j
      elif line[j] == ',':
        commaIndex = j
      elif line[j] == ';':
        semicolonIndex = j
      elif line[j] in ['(',')', '=']:
        otherCharIndex = j
      #{,}个数相同
      if openCurlyBraceQty == closeCurlyBraceQty:
        # class A; --不是class定义
        # struct A a; --不是struct定义
        if openCurlyBraceQty == 0 and semicolonIndex != -1:
          return False, -1, -1
        #class a: public b, public c {-- 避免这种情况当成非类定义
        # function(class A a,struct A c);--不是class定义
        elif openCurlyBraceQty == 0 and colonIndex == -1 and commaIndex != -1:
          return False, -1, -1
        # stuct a a ={};--不是struct定义
        # function(struct A b,struct A c);--不是struct定义
        elif openCurlyBraceQty == 0 and otherCharIndex != -1:
          return False, -1, -1
        elif openCurlyBraceQty > 0:
          # struct
          if keyWord == 'struct':
            return True, i, closeCurlyBraceIndex
          # class
          # class A {};--是函数定义
          if line[j + 1 :].strip().startswith(';'):
            semicolonIndex = line[j:].find(';')
            if i == startLineNo:
              endIndex = startIndex + j + semicolonIndex
            else:
              endIndex = j + semicolonIndex
            return True, i, endIndex
          # class A {} \\ or class A {} -- check next line
          elif line[j + 1 :].strip() == '\\' or (not line[j + 1 :].strip()):
            break
          # class {} AA-- }后没有;，说明文件有问题
          else:
            return True, -1, -1
          break
    i += 1
  return False, -1, -1

def isInBlock(targetLineNo, targetIndex, blockStartLineNo, blockStartIndex, blockEndLineNo, blockEndIndex):
  '''查看target是否在block内
  Args:
    targetLineNo:目标所在的行
    targetIndex:目标的index
    blockStartLineNo: block开始的行
    blockStartIndex: block开始的index
    blockEndLineNo: block结束的行
    blockEndIndex: block结束的index
  Returns:
           是否在block内
  '''
  # 开始行或结束行的行号非法，return false
  if blockStartLineNo == -1 or blockEndLineNo == -1:
    return False
  # block开始行和结束行是同一行
  if blockStartLineNo == blockEndLineNo:
    # 目标行不是block所在的行
    if targetLineNo != blockStartLineNo:
      return False
    # 目标行是block所在的行，但是目标的index不在block的范围内
    if targetIndex < blockStartIndex or targetIndex > blockEndIndex:
      return False
    return True
  # block开始行和结束行不是同一行
  # 目标行在block的前面或者后面
  if targetLineNo < blockStartLineNo or targetLineNo > blockEndLineNo:
    return False
  # 目标行在block的开始的行上 且目标在block前
  if targetLineNo == blockStartLineNo and targetIndex < blockStartIndex:
    return False
  # 目标行在block的结束的行上 且目标在block后
  if targetLineNo == blockEndLineNo and targetIndex > blockEndIndex:
    return False
  return True

def CheckCSC020009(filename, file_extension, clean_lines, rawlines, nesting_state, ruleCheckKey, Error, cpplines, fileErrorCount):
  '''函数体定义需要遵循下面的规范：
     {和}分别单独占一行。
     [例外]如果是定义在class定义中的空实现，{和}分别单独在一行，或者需将{和}写在一起，并放置在函数后面。
     {和}分别单独占一行也是可以的。[必须]
     cpp文件中的空实现，{和}分别单独占一行。
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
  errorMessageHeader = 'Code Style Rule:'
  #{和}分别单独占一行。
  errorMessage = ' The left curly brace "{" and right curly brace "}" in a function definition should be both in a separate line.'
  # 右大括号右边不能带分号
  semicolonErrorMessage = ' There should be no semicolon after the right curly brace "}".'
  # function() {   } ---error
  hasSpaceInBraceErrorMessage = ' Please leave no space between the left and right curly braces. For example: void func() {}.'
  # class定义(struct定义)中，空实现,{和}写在一起,{和)放置在函数后面 or {和}分别单独占一行。
  exceptionClassDefinition = ' For an empty function in the class(or struct) definition block, it can be written in the following two formats: 1.Put the "{" and "}" in the same line with the function name 2.Put the "{" and "}" both in a separate line.'
  lines = clean_lines.elided
  i = 0
  currentLineHasError = False
  nextLineHasError = False
  openCurlyBraceIndex = -1
  closeCurlyBraceLineNo = -1
  closeCurlyBraceIndex = -1
  classStartLineNo = -1
  classStartIndex = -1
  classEndLineNo = -1
  classEndIndex = -1
  templateCloseAngleBraceLineNo = -1
  templateCloseAngleBraceIndex = -1
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
    # template<class t, class t1>---- skkip
    m = strcmp.Search(r'\btemplate\b', lines[i])
    if m:
      templateCloseAngleBraceLineNo,templateCloseAngleBraceIndex = getTemplateEndLno(lines, i, m.start())
      #找不到template >所在的位置，则说明代码有问题，不再check
      if templateCloseAngleBraceLineNo == -1 or templateCloseAngleBraceIndex == -1:
        return
      i = templateCloseAngleBraceLineNo
    # 当前行是class的}所在的行，或者}后面的行时，重新找class定义
    if classEndLineNo <= i:
      # 当前行是template 的>所在的行,从class定义和templae的>后开始查找 class定义
      if templateCloseAngleBraceLineNo == i:
        classFindBeginIndex = templateCloseAngleBraceIndex
        # 当前行是class的};所在的行
        if classEndLineNo == i:
          if templateCloseAngleBraceIndex < classEndIndex:
            classFindBeginIndex = classEndIndex
      # 当前行不是template 的>所在的行 and 当前行是class的};所在的行,从class定义后开始查找 class定义
      elif classEndLineNo == i:
        classFindBeginIndex = classEndIndex
      # 当前行不是template 的>所在的行 and 当前行不是class的}所在的行
      else:
        classFindBeginIndex = 0
      # check是不是class定义
      m = strcmp.Search(r'\b(class|struct)\b', lines[i][classFindBeginIndex:])
      if m:
        isClassDefinition,classEndLineNo,classEndIndex = findClassStructDefinitionEndInfo(lines, i, m.start(), m.group(1))
        if isClassDefinition and (classEndLineNo == -1 or classEndIndex == -1):
          return
        # 是class定义
        if isClassDefinition:
          classStartLineNo = i
          classStartIndex = classFindBeginIndex + m.start()

    # 假如几个函数定义都写到一行了而且都不符合要求，这一行只报一个错误，不会重复报多个错误
    currentLineHasError = False
    if i == closeCurlyBraceLineNo and nextLineHasError:
      currentLineHasError = True
    nextLineHasError = False

    currentLine = lines[i]
    lengthCurrentLine = len(lines[i])
    # 查找{
    openCurlyBraceIndex = currentLine.find('{')
    if openCurlyBraceIndex == -1:
      i += 1
      continue
    # 如果{左侧满足operator += (...) 或者aaa(...)这种格式，说明这个是函数定义
    # operator +=(int a, int b) {}
    # AA::BB() {}
    # BB() {}
    while openCurlyBraceIndex > -1 and openCurlyBraceIndex < lengthCurrentLine:
      # 判断{是否是函数定义的第一个{
      isFunction, tempCloseParenthesislineNo, tempcloseParenthesisIndex, hasInitializationList = isFunctionDefinition(lines, i, openCurlyBraceIndex)
      # 是函数定义
      if isFunction:
        # 查找{对应的}的行号和其所在行的位置
        closeCurlyBraceLineNo, closeCurlyBraceIndex = getFunctionCloseCurlyBraceInfo(lines, i, openCurlyBraceIndex)
        # 查不到{对应的}的行号和其所在行的位置，说明文件不正常，不再check了
        if closeCurlyBraceLineNo == -1:
          return
        # check 函数是否在class 的{}内
        isInClassDefinition = isInBlock(closeCurlyBraceLineNo, closeCurlyBraceIndex, classStartLineNo, classStartIndex, classEndLineNo, classEndIndex)
        # }后面是逗号-- 不是函数定义
        if whetherCommarIsCloseAfterCloseCurlyBrace(lines, closeCurlyBraceLineNo, closeCurlyBraceIndex):
          # {}不在同一行
          if i < closeCurlyBraceLineNo:
            i = closeCurlyBraceLineNo
            break
          # {}在同一行
          # check 本行下一个{
          tempOpenCurlyBraceIndex = currentLine[closeCurlyBraceIndex + 1:].find('{')
          if tempOpenCurlyBraceIndex == -1:
            i += 1
            break
          openCurlyBraceIndex = closeCurlyBraceIndex + 1 + tempOpenCurlyBraceIndex
          continue
        # {}在同一行
        if closeCurlyBraceLineNo == i:
          if (not currentLineHasError) and strcmp.Search(r'^\s*;', lines[closeCurlyBraceLineNo][closeCurlyBraceIndex + 1:]):
            Error(filename, lines, i, ruleCheckKey, 3, errorMessageHeader + semicolonErrorMessage)
          # {}之间没有内容 and 无初始化列表时
          if common.IsBlankLine(lines[i][openCurlyBraceIndex + 1:closeCurlyBraceIndex]) and (not hasInitializationList):
            # ) 与 {不在同一行
            if tempCloseParenthesislineNo != i and (not currentLineHasError):
              # class定义中
              if isInClassDefinition:
                # {和}写在一起,{和)放置在函数后面 or {和}分别单独占一行。
                Error(filename, lines, i, ruleCheckKey, 3, errorMessageHeader + exceptionClassDefinition)
              else:
                # {和}分别单独占一行
                Error(filename, lines, i, ruleCheckKey, 3, errorMessageHeader + errorMessage)
              currentLineHasError = True
            elif tempCloseParenthesislineNo == i and (not currentLineHasError):
              # class定义中时,
              if isInClassDefinition:
                # function() {} other code(for example:  get();)---error
                if strcmp.Search(r'^\s*[^\s\;]', lines[closeCurlyBraceLineNo][closeCurlyBraceIndex + 1:]):
                  Error(filename, lines, i, ruleCheckKey, 3, errorMessageHeader + errorMessage)
                  currentLineHasError = True
                # function() {       } ---error
                if openCurlyBraceIndex + 1 < closeCurlyBraceIndex:
                  Error(filename, lines, i, ruleCheckKey, 3, errorMessageHeader + hasSpaceInBraceErrorMessage)
                  currentLineHasError = True
              # class定义外
              else:
                Error(filename, lines, i, ruleCheckKey, 3, errorMessageHeader + errorMessage)
                currentLineHasError = True
          # {}之间有内容  or have初始化列表时
          # 要求:{和}分别单独占一行
          else:
            if not currentLineHasError:
              currentLineHasError = True
              Error(filename, lines, i, ruleCheckKey, 3, errorMessageHeader + errorMessage)
          tempOpenCurlyBraceIndex = currentLine[openCurlyBraceIndex + 1:].find('{')
          if tempOpenCurlyBraceIndex == -1:
            i += 1
            break
          openCurlyBraceIndex = openCurlyBraceIndex + 1 + tempOpenCurlyBraceIndex
        # {}不在同一行
        else:
          hasCode = whetherHasSourceBetweenTwoLine(lines, i, openCurlyBraceIndex, closeCurlyBraceLineNo, closeCurlyBraceIndex)
          # check {   -------------------->
          if not currentLineHasError:
            # 空实现(无代码 and 没有初始化列表)
            if (not hasCode) and (not hasInitializationList):
              # class定义中时
              if isInClassDefinition:
                # )与{在同一行
                if tempCloseParenthesislineNo == i:
                  # {和}写在一起,{和)放置在函数后面 or {和}分别单独占一行。
                  Error(filename, lines, i, ruleCheckKey, 3, errorMessageHeader + exceptionClassDefinition)
                  currentLineHasError = True
              # class定义外时
              else:
                # )与{在同一行
                if tempCloseParenthesislineNo == i:
                  #{和}分别单独占一行。
                  Error(filename, lines, i, ruleCheckKey, 3, errorMessageHeader + errorMessage)
                  currentLineHasError = True
            # 非空实现
            else:
              # {独占一行
              if common.IsBlankLine(lines[i][:openCurlyBraceIndex]) and common.IsBlankLine(lines[i][openCurlyBraceIndex + 1:]):
                pass
              # {非独占一行
              else:
                currentLineHasError = True
                Error(filename, lines, i, ruleCheckKey, 3, errorMessageHeader + errorMessage)
          # check {   <--------------------
          # check }   -------------------->
          # 非空实现(有代码  or 有初始化列表)
          if hasCode or hasInitializationList:
            # }独占一行
            # chcek }前是否有代码
            hasCodeBeforeCloseCurlyBrace = False
            if not common.IsBlankLine(lines[closeCurlyBraceLineNo][:closeCurlyBraceIndex]):
              hasCodeBeforeCloseCurlyBrace = True
            # chcek }后是否有分号
            hasSemicolonAfterCloseCurlyBrace = False
            mForSemicolon = strcmp.Search(r'^\s*;', lines[closeCurlyBraceLineNo][closeCurlyBraceIndex + 1:])
            if mForSemicolon:
              hasSemicolonAfterCloseCurlyBrace = True
            # chcek }后是否有代码
            # }后有分号时
            if hasSemicolonAfterCloseCurlyBrace:
              # chcek 分号后是否有代码
              if common.IsBlankLine(lines[closeCurlyBraceLineNo][closeCurlyBraceIndex + 1 + mForSemicolon.end():]):
                hasCodeAfterCloseCurlyBrace = False
              else:
                hasCodeAfterCloseCurlyBrace = True
            # }后没有分号时
            else:
              # chcek }后是否有代码
              if common.IsBlankLine(lines[closeCurlyBraceLineNo][closeCurlyBraceIndex + 1:]):
                hasCodeAfterCloseCurlyBrace = False
              else:
                hasCodeAfterCloseCurlyBrace = True
            # }后有分号 and }所在的行有代码
            if  (hasCodeBeforeCloseCurlyBrace or hasCodeAfterCloseCurlyBrace) and hasSemicolonAfterCloseCurlyBrace:
              nextLineHasError = True
              currentLineHasError = True
              Error(filename, lines, closeCurlyBraceLineNo, ruleCheckKey, 3, errorMessageHeader + errorMessage)
              Error(filename, lines, closeCurlyBraceLineNo, ruleCheckKey, 3, errorMessageHeader + semicolonErrorMessage)
            # }后有分号
            elif hasSemicolonAfterCloseCurlyBrace:
                nextLineHasError = True
                currentLineHasError = True
                Error(filename, lines, closeCurlyBraceLineNo, ruleCheckKey, 3, errorMessageHeader + semicolonErrorMessage)
            # }所在的行有代码
            elif hasCodeBeforeCloseCurlyBrace or hasCodeAfterCloseCurlyBrace:
              nextLineHasError = True
              currentLineHasError = True
              Error(filename, lines, closeCurlyBraceLineNo, ruleCheckKey, 3, errorMessageHeader + errorMessage)
          # 空实现
          else:
            # check }后是否有分号
            if strcmp.Search(r'^\s*;', lines[closeCurlyBraceLineNo][closeCurlyBraceIndex + 1:]):
              nextLineHasError = True
              currentLineHasError = True
              Error(filename, lines, closeCurlyBraceLineNo, ruleCheckKey, 3, errorMessageHeader + semicolonErrorMessage)
            # )与{不在同一行 and }后有代码
            elif strcmp.Search(r'^\s*\S', lines[closeCurlyBraceLineNo][closeCurlyBraceIndex + 1:]):
              if not isInClassDefinition:
                nextLineHasError = True
                currentLineHasError = True
                Error(filename, lines, closeCurlyBraceLineNo, ruleCheckKey, 3, errorMessageHeader + errorMessage)
              elif tempCloseParenthesislineNo != i:
                nextLineHasError = True
                currentLineHasError = True
                Error(filename, lines, closeCurlyBraceLineNo, ruleCheckKey, 3, errorMessageHeader + errorMessage)
          # check }   <--------------------
          i = closeCurlyBraceLineNo
          break
      # 不是函数定义
      else:
        tempOpenCurlyBraceIndex = currentLine[openCurlyBraceIndex + 1:].find('{')
        if tempOpenCurlyBraceIndex == -1:
          i += 1
          break
        openCurlyBraceIndex = openCurlyBraceIndex + 1 + tempOpenCurlyBraceIndex     
