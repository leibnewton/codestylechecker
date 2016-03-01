#!/usr/bin/python  
#-*- coding: utf-8 -*- 
'''
Created on 2014-3-19

@author: zhangran
'''
import os
import sys
syspath = os.path.dirname(os.path.dirname(__file__))
if not os.path.join(syspath, "tools") in sys.path:
  sys.path.append(os.path.join(syspath, "tools"))
import common
strcmp = common.StringCompareInfo()

#忽略temeplate的声明
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

def checkmMemberFunctionAccessInClass(lines, startLineNo, endLineNo):

  accessFlg = False
  
  startLine = lines[startLineNo][lines[startLineNo].find('{') + len('{'):]
  i = 0
  for i in range(startLineNo, endLineNo):
    line = lines[i]
    if i == startLineNo:
      line = startLine
    
    if common.IsBlankLine(line):
      continue
    if strcmp.Search(r'^\s*#', line):
      continue
  
    #找到成员的声明或者定义
    if strcmp.Search(r'{|;|}', line):
      break
  
  # 空的class类，不判断public / protected / private关键字
  if i == endLineNo - 1:
    return True
  
  startLine = lines[startLineNo][lines[startLineNo].find('class') + len('class'):]
  for i in range(startLineNo, endLineNo):
    line = lines[i]
    if i == startLineNo:
      line = startLine
      
    if common.IsBlankLine(line):
      continue
    if strcmp.Search(r'^\s*#', line):
      continue
  
    if strcmp.Search(r'^\s*template\s*<', line):
      iRet = getTemplateEndLno(lines, i)
      if iRet != -1:
        # skip template的声明
        i = iRet
        continue
    
    if strcmp.Search(r'^\s*class\s+\w+', line) and not strcmp.Search(r'^\s*class\s+\w+\s*;', line) and not strcmp.Search(r'^\s*class\s+\w+\s*>', line) and line.count('(') == 0:
      isClass, startBlockLineNo, endBlockLineNo =common.isClassDeclareCheck(lines, i)
      if isClass:
        checkmMemberFunctionAccessInClass(lines, startBlockLineNo , endBlockLineNo)
    else:
      if (strcmp.Search(r'(\bpublic\b|\bprotected\b|\bprivate\b)\s*:', line)):
        accessFlg =  True
        break
        
    #找到成员的声明或者定义
    if strcmp.Search(r';|}', lines[i]) and not accessFlg:
      break
    
  return accessFlg
    
def CheckCSC100001(filename, file_extension, clean_lines, rawlines, nesting_state, ruleCheckKey, Error, cpplines, fileErrorCount):
  lines = clean_lines.elided
  errMessage = "Code Style Rule:  Please don't rely on the default access level for class members(which is private)."
  for i in xrange(clean_lines.NumLines()):
    
    if common.IsBlankLine(lines[i]):
      continue
    if strcmp.Search(r'^\s*#', lines[i]):
      continue
    
    # template类型例子，
    # template <class T, ASN1::natural explicit_tag,  
    #     ASN1::tag_class_enum explicit_tag_class = ASN1::class_context_specific>
    if strcmp.Search(r'^\s*template\s*<', lines[i]):
      iRet = getTemplateEndLno(lines, i)
      if iRet != -1:
        i = iRet
        continue
    
    # eg. class A {
    # 查找到class类名后，检查类作用域内是否有public / protected / private关键字
    # 排除namespace中的class声明 class NCWifiEvent; template <class T>
    if strcmp.Search(r'^\s*class\s+\w+', lines[i]) and not strcmp.Search(r'^\s*class\s+\w+\s*;', lines[i]) and not strcmp.Search(r'^\s*class\s+\w+\s*>', lines[i]) and lines[i].count('(') == 0:
        isClass, startBlockLineNo, endBlockLineNo =common.isClassDeclareCheck(lines, i)
        if isClass and startBlockLineNo < endBlockLineNo:
           bRet = checkmMemberFunctionAccessInClass(lines, startBlockLineNo , endBlockLineNo)
           if not bRet:
             Error(filename, lines, i, ruleCheckKey, 3, errMessage)
             continue