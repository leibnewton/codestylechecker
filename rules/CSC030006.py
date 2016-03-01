#!/usr/bin/python  
#-*- coding: utf-8 -*-
'''
Created on 2014-4-25

@author: zhangran
'''
import os
import sys
syspath = os.path.dirname(os.path.dirname(__file__))
if not os.path.join(syspath, "tools") in sys.path:
  sys.path.append(os.path.join(syspath, "tools"))
import common
strcmp = common.StringCompareInfo()

import sre_compile
import re
import unicodedata

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

def isFunctionDefinition(lines, openCurlyBraceLineNo, openCurlyBraceIndex):
  '''判断{是否是函数定义的第一个{
  Args:
    lines:所有行
    openCurlyBraceLineNo: {所在行的行号
    openCurlyBraceIndex : {在所在行的位置
  Returns:
            是否是函数定义(True: yes; False: no)；是函数定义的话，返回)所在的行的行号以及)的位置
  '''
  # {所在行,{之前不为空白，且{前不是)，说明这不是函数定义
  tempLine = lines[openCurlyBraceLineNo][:openCurlyBraceIndex].strip()
  if tempLine and (not tempLine.endswith(')')):
    return False, -1, -1
  # {所在行,{之前为空白
  closeParenthesisLineNo = -1
  closeParenthesisIndex = -1
  # 查找)--------------->
  # {所在行,{之前不为空白
  if tempLine:
    closeParenthesisLineNo = openCurlyBraceLineNo
    closeParenthesisIndex = lines[openCurlyBraceLineNo][:openCurlyBraceIndex].rfind(')')
  else:
    i = openCurlyBraceLineNo - 1
    # 查看离{最近的字符是否为)
    while i > 0:
      # line start with # skip
      if strcmp.Search(r'^\s*#', lines[i]):
        i -= 1
        continue
      #null line skip
      if common.IsBlankLine(lines[i]):
        i -= 1
        continue
      # 如果有换行符，去掉换行符
      if lines[i].endswith("\\"):
        tempLine = lines[i][:len(lines[i]) -1].rstrip()
      else:
        tempLine = lines[i].rstrip()
      # 如果改行只有换行符和空格而没有代码时
      if common.IsBlankLine(tempLine):
        i -= 1
        continue
      # 离{最近的字符是),保存）的行号和位置，为判断是否为函数定义做准备
      if tempLine.endswith(')'):
        closeParenthesisLineNo = i
        closeParenthesisIndex = len(tempLine) - 1
        break
      # 离{最近的字符不是)，说明这不是函数定义
      else:
        return False, -1, -1
  # 查找)<---------------
  # 查找)对应的（--------------->
  i =  closeParenthesisLineNo
  openParenthesisLineNo = -1
  openParenthesisIndex = -1
  while i > 0:
    # line start with # skip
    if strcmp.Search(r'^\s*#', lines[i]):
      i -= 1
      continue
    #null line skip
    if common.IsBlankLine(lines[i]):
      i -= 1
      continue
    if i == closeParenthesisLineNo:
      tempLine = lines[i][:closeParenthesisIndex]
    elif lines[i].endswith("\\"):
      tempLine = lines[i][:len(lines[i]) -1]
    else:
      tempLine = lines[i]
    openParenthesisIndex = tempLine.rfind('(')
    # )前还有)，说明不是函数定义，function(...)中不可能还有（）
    if openParenthesisIndex == -1:
      if tempLine.rfind(')') != -1:
        return False, -1, -1
      else:
        i -= 1
        continue
    # ()之间还有)，说明不是函数定义，function(...)中不可能还有（）
    else:
      if tempLine[openParenthesisIndex + 1:].rfind(')') != -1:
        return False, -1, -1
      else:
        openParenthesisLineNo = i
        break
  # 如果找不到)对应的(,说明不是函数定义
  if openParenthesisLineNo == -1:
    return False, -1, -1
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
      return True, closeParenthesisLineNo, closeParenthesisIndex
    # (前面是单词，且这些单词不是关键字时，说明该代码块是函数定义
    m = strcmp.Search(r'\b(\w+)\b\s*$', tempLine)
    if m:
      if m.group(1) not in ['if', 'while', 'for', 'switch']:
        return True, closeParenthesisLineNo, closeParenthesisIndex
    return False, -1, -1
  return False, -1, -1
  # 查找(前得单词，判断其是否是关键字，如果不是，说明是函数<---------------

def CheckCSC030006(filename, file_extension, clean_lines, rawlines, nesting_state, ruleCheckKey, Error, cpplines, fileErrorCount):
    
  errMessage = "Code Style Rule: There should be a blank line after every function definition."
    
  lines = clean_lines.elided

#函数定义的例子
#void A (){
#Test1& operator = (const Test1& t1){ // 赋值运算符
#void VRS_210010::CheckGlobalInitInConstructor(){
#void VRS_210010::foo(string s, int i):name(s), id(i){} ;
#int bb<t,t1>::aa(){
#AA::A VRS_210010::CheckGlobalInitInConstructor(){

#1 operator关键字
#2 ::找
#3 普通

  i = 0
  while i < clean_lines.NumLines():
    line = lines[i]
      
    #null line skip
    if common.IsBlankLine(line):
      i += 1
      continue
    #define line skip
    if strcmp.Search(r'^\s*#\s*define\s+', line):
      i = common.getDefineMacroEndLineNo(lines, i) + 1
      continue
    # line start with # skip
    if strcmp.Search(r'^\s*#', line):
      i = common.getDefineMacroEndLineNo(lines, i) + 1
      continue
  
    # 查找{
    openCurlyBraceIndex = line.find('{')
    if openCurlyBraceIndex == -1:
      i += 1
      continue
  
    # 如果{左侧满足operator += (...) 或者aaa(...)这种格式，说明这个是函数定义
    # operator +=(int a, int b) {}
    # AA::BB() {}
    # BB() {}
    
    # 判断{是否是函数定义的第一个{
    isFunction, tempCloseParenthesislineNo, tempcloseParenthesisIndex = isFunctionDefinition(lines, i, openCurlyBraceIndex)
    # 是函数定义
    if isFunction:
      # 查找{对应的}的行号和其所在行的位置
      closeCurlyBraceLineNo, closeCurlyBraceIndex = getFunctionCloseCurlyBraceInfo(lines, i, openCurlyBraceIndex)
      # 查不到{对应的}的行号和其所在行的位置，说明文件不正常，不再check了
      if closeCurlyBraceLineNo == -1:
        return
    
      # {}在同一行
      if closeCurlyBraceLineNo == i:
        i += 1
        continue
      else :
        
        # 文件结束
        if -1 == lines[closeCurlyBraceLineNo + 1].find('EOF') and \
          closeCurlyBraceLineNo + 1 < clean_lines.NumLines() - 1 and \
          lines[closeCurlyBraceLineNo + 1].strip() != '};' and \
          lines[closeCurlyBraceLineNo + 1].strip() != '}'  :
            
          # 函数定义后必须有空行
          if not common.IsBlankLine(lines[closeCurlyBraceLineNo + 1]) :
            Error(filename, lines, closeCurlyBraceLineNo, ruleCheckKey, 3, errMessage)
            
          i = closeCurlyBraceLineNo + 2
          continue
    
    i += 1
# end of CheckCSC030006
