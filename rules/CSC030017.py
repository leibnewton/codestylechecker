#!/usr/bin/python  
#-*- coding: utf-8 -*-
'''
Created on 2014-4-30

@author: zhangran
'''
import os
import sys
import re
syspath = os.path.dirname(os.path.dirname(__file__))
if not os.path.join(syspath, "tools") in sys.path:
  sys.path.append(os.path.join(syspath, "tools"))
import common
strcmp = common.StringCompareInfo()

# Matches standard C++ escape esequences per 2.13.2.3 of the C++ standard.
_RE_PATTERN_CLEANSE_LINE_ESCAPES = re.compile(
    r'\\([abfnrtv?"\\\']|\d+|x[0-9a-fA-F]+)')
# Matches strings.  Escape codes should already be removed by ESCAPES.
_RE_PATTERN_CLEANSE_LINE_DOUBLE_QUOTES = re.compile(r'"[^"]*"')
# Matches characters.  Escape codes should already be removed by ESCAPES.
_RE_PATTERN_CLEANSE_LINE_SINGLE_QUOTES = re.compile(r"'.'")

def checkSignLeftRightBlank(line, leftPos, rightPos):

  # 符号有换行
  if len(line) <= rightPos :
    return True
  if (line[leftPos:leftPos + 1] == ' ' or line[leftPos:leftPos + 1] == '\t') and  (line[rightPos:rightPos + 1] == ' ' or line[rightPos:rightPos + 1] == '\t'):
    return True
  return False
  
# end of  checkSignLeftRightBlank

def replaceCorrectString(lines, lineNo, leftPos, rightPos, str):

  tmp = str
  if lines[lineNo][leftPos:leftPos + 1] != ' ' and lines[lineNo][leftPos:leftPos + 1] != '\t' :
    tmp = ' ' + str
  
  if lines[lineNo][rightPos:rightPos + 1] != ' ' and lines[lineNo][rightPos:rightPos + 1] != '\t':
    tmp = str + ' '

  if lineNo > 1 and not common.hasChangeLineCharInCurrentLineOrPrevLine(lines, lineNo):
    lines[lineNo] = lines[lineNo].replace(str, tmp)

def CheckCSC030017(filename, file_extension, clean_lines, rawlines, nesting_state, ruleCheckKey, Error, cpplines, fileErrorCount):
  
  # 赋值判断
  #因为 * & 即是指针也是运算符，无法判断，所有不判断这两个
  arraySign1 = ["+","-","*","/","%","&", "|", "~", "^"]
  # 运算符 
  # eg. if (a && b), if (a || b)
  arraySign2 = ["&&", "||"]
  # 必须在等号后判断的，否则容易产生误判
  # error 数据有赋值为负数的情况，'-'删除
  arraySign3 = ["+","/","%", "|", "<<", ">>"]
  
  lines = clean_lines.elided
  errMessage = "Code Style Rule: There should a space both before and after a binary operator \"%s\". For example: A = B."
  i = 0
  FoldinglineFlag = False
  line = ''
  while i < clean_lines.NumLines():
    findFlg = True
    index = 0
    signTag = ''
    
    if lines[i].endswith("\\"):
      # 换行的第一行，清空缓存的line
      if not FoldinglineFlag:
        line = ''
        
      FoldinglineFlag = True
      line = line + lines[i][0:len(lines[i])]
      i += 1
      continue
    else :
      # 换行的最后一行
      if FoldinglineFlag:
        line = line + lines[i]
        line = _RE_PATTERN_CLEANSE_LINE_ESCAPES.sub('', line)
        line = _RE_PATTERN_CLEANSE_LINE_SINGLE_QUOTES.sub("''", line)
        line = _RE_PATTERN_CLEANSE_LINE_DOUBLE_QUOTES.sub('""', line)
      else :
        line = lines[i]
        
      FoldinglineFlag = False
        
    line = lines[i].replace("->", ".")
        
    if common.IsBlankLine(line):
      i += 1
      continue
  
    #define line skip
    if strcmp.Search(r'^\s*#\s*define\s+', lines[i]):
      i = common.getDefineMacroEndLineNo(lines, i) + 1
      continue
  
    if strcmp.Search(r'^\s*#', line):
      i += 1
      continue
    
    
    # 查找"operator",忽略操作符重载的函数名的判断
    if strcmp.Search(r'\boperator\b', line):
      i += 1
      continue
  
    # 查找"===",忽略
    if strcmp.Search(r'===', line):
      i += 1
      continue
  
    #只判断结束语句
    endPos = line.rfind(";")
    if endPos == -1:
      endPos = len(line)
    
    # 查找"="
    index2 = line.rfind("=", 0, endPos)
    if -1 != index2 and -1 == line.find('virtual ', 0, index2):
    
      # 忽略字符串中的 = 的判断
      # static std::string myTestData = "<?xml version=\"1.0\" encoding=\"UTF-8\" ?> \
      #strFlgIndex = line.find("\"", 0, endPos)
      #if strFlgIndex >= index2:
      #  i += 1
       # continue
    
      arraySign1FLg = False
      
      index3 = cpplines[i].rfind("=", 0, endPos)
      # 判断前一位是否为运算符
      if line[index2 - 1:index2] in arraySign1:
        findFlg = checkSignLeftRightBlank(line, index2 - 2, index2 + 1)
        signTag = line[index2 - 1:index2] + '='
        arraySign1FLg = True
        if not findFlg:
          replaceCorrectString(cpplines, i, index3 - 2, index3 + 1, signTag)
          fileErrorCount[0] =  fileErrorCount[0] + 1
      
      if not arraySign1FLg:
        if line[index2 - 1:index2] == "<" or line[index2 - 1:index2] == ">":
          # "<<=",">>=" 情况
          if line[index2 - 2:index2 - 1] == "<" or line[index2 - 2:index2 - 1] == ">":
            findFlg = checkSignLeftRightBlank(line, index2 - 3, index2 + 1)
            
            signTag = line[index2 - 2:index2] + '='
            if not findFlg:
              replaceCorrectString(cpplines, i, index3 - 3, index3 + 1, signTag)
              fileErrorCount[0] =  fileErrorCount[0] + 1
          else:
             # "<=",">=" 情况
            findFlg = checkSignLeftRightBlank(line, index2 - 2, index2 + 1)
            signTag = line[index2 - 2:index2] + '='
            
            if not findFlg:
              replaceCorrectString(cpplines, i, index3 - 2, index3 + 1, signTag)
              fileErrorCount[0] =  fileErrorCount[0] + 1
          
           # "!=" 情况
        elif line[index2 - 1:index2] == "!" :
          findFlg = checkSignLeftRightBlank(line, index2 - 2, index2 + 1)
          signTag = '!='
          if not findFlg:
            replaceCorrectString(cpplines, i, index3 - 2, index3 + 1, signTag)
            fileErrorCount[0] =  fileErrorCount[0] + 1
          # "==" 情况
        elif line[index2 - 1:index2] == "=" :
          findFlg = checkSignLeftRightBlank(line, index2 - 2, index2 + 1)
          signTag = '=='
          if not findFlg:
            replaceCorrectString(cpplines, i, index3 - 2, index3 + 1, signTag)
            fileErrorCount[0] =  fileErrorCount[0] + 1
        else:
          # "=" 情况
          findFlg = checkSignLeftRightBlank(line, index2 - 1, index2 + 1)
          signTag = '='
          if not findFlg:
            replaceCorrectString(cpplines, i, index3 - 1, index3 + 1, signTag)
            fileErrorCount[0] =  fileErrorCount[0] + 1
              
          for k in xrange(len(arraySign3)):
            index = line.find(arraySign3[k], index2, endPos)
            # "||" 在 '|'判断时产生误判
            if -1 != index and line[index: index +2 ] != '||':
              # next = *s++ 误判
              indexPlusPlus = line.find('++')
              if indexPlusPlus == index:
                continue
            
              findFlg = checkSignLeftRightBlank(line, index - 1, index + len(arraySign3[k]))
              signTag = arraySign3[k]
              if not findFlg:
                index = cpplines[i].find(arraySign3[k], index2, endPos)
                replaceCorrectString(cpplines, i, index - 1, index + len(arraySign3[k]), signTag)
                fileErrorCount[0] =  fileErrorCount[0] + 1
               
              break
          
    # 赋值判断
    for j in xrange(len(arraySign2)):
      index = line.find(arraySign2[j], 0, endPos)
      if -1 != index:
        findFlg = checkSignLeftRightBlank(line, index - 1, index + len(arraySign2[j]))
        signTag = arraySign2[j]
        
        if not findFlg:
          index = cpplines[i].find(arraySign2[j], 0, endPos)
          replaceCorrectString(cpplines, i, index - 1, index + len(arraySign2[j]), signTag)
          fileErrorCount[0] =  fileErrorCount[0] + 1
    
    #如果是类似 (XXX)*(XXX) 的形式，也需要报错。因为这种情况说明写法有问题，导致无法判断是乘号还是指针
    if strcmp.Search(r'\(\w+\)\*\(\w+\)', line):
      signTag = '*'
      findFlg = False
      if not findFlg:

        cpplines[i] = cpplines[i].replace(")*(", ") * (")
        fileErrorCount[0] =  fileErrorCount[0] + 1
    
    if not findFlg:
      Error(filename, lines, i, ruleCheckKey, 3, errMessage % signTag)
  
    i += 1
# end of CheckCSC030017