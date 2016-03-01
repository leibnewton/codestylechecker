#!/usr/bin/python  
#-*- coding: utf-8 -*-
'''
Created on 2014-12-16

@author: zhangran
'''
import os
import sys
syspath = os.path.dirname(os.path.dirname(__file__))
if not os.path.join(syspath, "tools") in sys.path:
  sys.path.append(os.path.join(syspath, "tools"))
import common
strcmp = common.StringCompareInfo()

def getDefineMacroEndLineNo(lines, fromLno):
  lengthOfLines = len(lines)
  for i in xrange(fromLno, lengthOfLines):
    if not lines[i].endswith("\\"):
      return i
  return fromLno

def getTemplateEndLno(lines, startLno):
  #查找template<...>中>所在的行
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

def checkClassDiscription(filename, file_extension, lines, rawlines, noteStartLineNo, noteEndLineNo, classkeyLineNo, ruleCheckKey, Error, cpplines, fileErrorCount):
  ''' 检查class注释说明
  
  Sample
  /**
   * 简单的Class说明。            <-- Class概要说明 ,必须写在一行之内[必须]
   *
   * 空一行后开始写Class详细说明。         <-- Class详细说明 [必须]
   * 注意这里即使有换行，生成的文档中也不会换行，如果想要换行像下面一样加入空行，
   * 或者使用html的标签<br>。
   *
   * 这样空一行后的内容会在文档中另起一行，用下面的条目也会单独一行显示。
   * - 条目1
   * - 条目2
   */
  
  Args:
    filename:文件名
    lines:文件的内容
    rawlines:原始的文件内容
    noteStartLineNo:注释说明开始的行数
    noteEndLineNo:注释说明结束的行数
    ruleCheckKey:rule的id
    Error:error的句柄
  '''
    
  #包含如下的注释格式 /** 注释 */， /// 注释， /**< 注释 */， ///< ， /* 注释 */， // 注释
  COMMENTKEY = (
      '/*', '*/','//'                      
  )
  errorMessage = "Code Style Rule: In class declaration, there should be comments of: 1.Summary description 2.Details description of the class."

  # cpp文件里，只用判断是否有注释，不用判断注释内容
  if file_extension != "h":
    for i in xrange(classkeyLineNo -1 , 0, -1) :
      if common.IsBlankLine(rawlines[i]):
        continue
      
      # 非空行
      index = -1
      for j in xrange(0, len(COMMENTKEY)):
        index = rawlines[i].find(COMMENTKEY[j])
        if -1 != index :
          break
      
      if index < 0 :
        Error(filename, lines, classkeyLineNo, ruleCheckKey, 3, errorMessage)
    
      # 不管找到不找到，都退出循环
      break
  
    return

  if noteStartLineNo == 0 and noteEndLineNo == 0:
    Error(filename, lines, classkeyLineNo, ruleCheckKey, 3, errorMessage)
    return

  #判断注释是否是属于该class的说明，即注释和class中不能有其他的非空行
  i = noteEndLineNo + 1
  while i <= classkeyLineNo:
    line = rawlines[i]
    if i == classkeyLineNo:
      line = rawlines[classkeyLineNo][0: lines[classkeyLineNo].find('class')]
      
    if common.IsBlankLine(line):
      i += 1
      continue
    else :
      #template<...> -- skip
      if strcmp.Search(r'^\s*template\s*<', lines[i]):
        i = getTemplateEndLno(lines, i)
        i += 1
        continue
    
      Error(filename, lines, classkeyLineNo, ruleCheckKey, 3, errorMessage)
      return
          
  summaryLineNo = 0
  detailsLineNo = 0
  
  i = noteStartLineNo
  while i <= noteEndLineNo:
    line = rawlines[i]
    
    if common.IsBlankLine(line):
      i += 1
      continue
  
    #Class概要说明
    if strcmp.Search(r'\*\s+\S+', line) and 0 == summaryLineNo:
      summaryLineNo = i
      i += 1
      continue
      
    #Class概要说明 ,必须写在一行之内  
    if i == (summaryLineNo + 1) and line.strip() != '*' and summaryLineNo > 0:
      Error(filename, lines, i, ruleCheckKey, 3, errorMessage)
    
    # Class详细说明
    if strcmp.Search(r'\*\s+\S+', line) and summaryLineNo > 0 and i > (summaryLineNo + 1) :
      detailsLineNo  = i
      i += 1
      break
             
    i += 1
  
  #判断class的注释说明
  if detailsLineNo == 0:
    Error(filename, lines, noteStartLineNo, ruleCheckKey, 3, errorMessage)
    
    

def CheckCSC140003(filename, file_extension, clean_lines, rawlines, nesting_state, ruleCheckKey, Error, cpplines, fileErrorCount):
  '''class声明必须有下面的注释说明。
     概要说明 无 必须写在一行之内
    详细说明 无 描述详细说明。
    如有必要，可以列一些条目形式的内容，或一些SampleCode

  Args:
    filename:文件名
    file_extension:文件的扩展名
    clean_lines:文件的内容(不包含注释)
    rawlines:原始的文件内容
    nesting_state:一个NestingState实例，维护有关嵌套块的当前堆栈信息进行解析。
    ruleCheckKey:rule的id
    Error:error的句柄
  '''

  noteStartLineNo = 0
  noteEndLineNo = 0
  
  i = 0
  while i < len(rawlines):
    if common.IsBlankLine(rawlines[i]):
      i += 1
      continue
    if strcmp.Search(r'^\s*#\s*define\s+', rawlines[i]):
      i = getDefineMacroEndLineNo(rawlines, i) + 1
      continue
    if strcmp.Search(r'^\s*#', rawlines[i]):
      i += 1
      continue

    if rawlines[i].strip() == '/**':
      noteStartLineNo = i
      noteEndLineNo = 0
    #结束
    elif rawlines[i].strip() == '*/':
      if noteEndLineNo == 0:
        noteEndLineNo = i
    elif strcmp.Search(r'^(\s*)\bclass[\s*:{;]', rawlines[i]) :
      isClass, startBlockLineNo, endBlockLineNo = common.isClassDeclareCheck(rawlines, i)
      if isClass:
        checkClassDiscription(filename, file_extension, rawlines, rawlines, noteStartLineNo, noteEndLineNo, i, ruleCheckKey, Error, cpplines, fileErrorCount)
    
    i += 1
        
