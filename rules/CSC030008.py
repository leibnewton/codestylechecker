#!/usr/bin/python  
#-*- coding: utf-8 -*-
'''
Created on 2014-4-16

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

def checkClassBlock(filename, lines, startLineNo, endLineNo, ruleCheckKey, Error, cpplines, fileErrorCount):
  
  errMessage = "Code Style Rule: There should be a blank line after every public/protected/private area."
  
  # public/protected/private区域表示
  bDeclareFlg = False
  bBlankFlg = False
  
  i = startLineNo + 1
  while i <= endLineNo:
    line = lines[i]
    
    if common.IsBlankLine(lines[i]):
      i += 1
      
      #有区间标志，记录空行
      if bDeclareFlg:
        bBlankFlg = True
        
      continue
  
    #宏定义--skip
    if strcmp.Search(r'^\s*#\s*define\s+', line):
      i = common.getDefineMacroEndLineNo(lines, i) + 1
      continue
  
    #预定义--skip
    if strcmp.Search(r'^\s*#', line):
      i += 1
      continue
  
    # template类型例子，
    # template <class T, ASN1::natural explicit_tag,  
    #     ASN1::tag_class_enum explicit_tag_class = ASN1::class_context_specific>
    if strcmp.Search(r'^\s*template\s*<', lines[i]):
      iRet = getTemplateEndLno(lines, i)
      if iRet != -1:
        i = iRet + 1
        continue
    
    m = strcmp.Search(r'^\s*(\bpublic\b|\bprivate\b|\bprotected\b)\s*:', line)
    if m:
        
      # 找到后修改标志
      if not bDeclareFlg:
        bDeclareFlg = True
      else :
        if not bBlankFlg:
          Error(filename, lines, i, ruleCheckKey, 3, errMessage)
          
          # 有空行，变量修改为false，继续查找
        else :
          bBlankFlg = False
          
    # 内嵌类    
    # eg. class A {
    # 查找到class类名后，检查类作用域内是否有public / protected / private关键字
    # 排除namespace中的class声明 class NCWifiEvent; template <class T>
    if strcmp.Search(r'^\s*class\s+\w+', lines[i]) and not strcmp.Search(r'^\s*class\s+\w+\s*;', lines[i]) and not strcmp.Search(r'^\s*class\s+\w+\s*>', lines[i]) and lines[i].count('(') == 0:
      #判断是否是类定义
      isClassDeclare,nestStartLineNo,nestEndLineNo = common.isClassDeclareCheck(lines, i)
      #当class的类定义中，所有的代码都是在同一行时,没必要check
      if nestStartLineNo == nestEndLineNo:
        i = nestEndLineNo + 1
        continue
      # check 内部类
      if isClassDeclare:
        checkClassBlock(filename, lines, nestStartLineNo, nestEndLineNo, ruleCheckKey, Error, cpplines, fileErrorCount)
      i = nestEndLineNo + 1
      continue
      
    i += 1
    
# end checkClassBlock

def CheckCSC030008(filename, file_extension, clean_lines, rawlines, nesting_state, ruleCheckKey, Error, cpplines, fileErrorCount):
  lines = clean_lines.elided
  
  isClassDeclare = False

  i = 1
  while i < len(lines) :
    
    if common.IsBlankLine(lines[i]):
      i += 1
      continue
    
    #宏定义--skip
    if strcmp.Search(r'^\s*#\s*define\s+', lines[i]):
      i = common.getDefineMacroEndLineNo(lines, i) + 1
      continue
  
    if strcmp.Search(r'^\s*#', lines[i]):
      i += 1
      continue
  
    # template类型例子，
    # template <class T, ASN1::natural explicit_tag,  
    #     ASN1::tag_class_enum explicit_tag_class = ASN1::class_context_specific>
    if strcmp.Search(r'^\s*template\s*<', lines[i]):
      iRet = getTemplateEndLno(lines, i)
      if iRet != -1:
        i = iRet + 1
        continue
    
    # eg. class A {
    # 查找到class类名后，检查类作用域内是否有public / protected / private关键字
    # 排除namespace中的class声明 class NCWifiEvent; template <class T>
    if strcmp.Search(r'^\s*class\s+\w+', lines[i]) and not strcmp.Search(r'^\s*class\s+\w+\s*;', lines[i]) and not strcmp.Search(r'^\s*class\s+\w+\s*>', lines[i]) and lines[i].count('(') == 0:
      
      #判断是否是类定义
      isClassDeclare,startLineNo,endLineNo = common.isClassDeclareCheck(lines, i)
      
      #当class的类定义中，所有的代码都是在同一行时,没必要check
      if startLineNo == endLineNo:
        i = endLineNo + 1
        continue
      #check 类定义
      if isClassDeclare:
        checkClassBlock(filename, lines, startLineNo, endLineNo, ruleCheckKey, Error, cpplines, fileErrorCount)
        i = endLineNo + 1
        continue

    i += 1
