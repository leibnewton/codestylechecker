#!/usr/bin/python  
#-*- coding: utf-8 -*-
'''
Created on 2014-2-11

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

def getStatementStartEnd(lines, startLineNo, typeword):
  #函数功能：查找if，while的左右括号所在的行号，以及if，while行的缩进情况
  #if，while所在行，凡是含有if，while字符串的单词，都相应的字符串都被替换
  substring = ''
  if typeword == 'if':
    substring = '12'
  elif typeword == 'while':
    substring = '12345'
  startLine = strcmp.Sub(r'\w' + typeword, '0' + substring, lines[startLineNo])
  startLine = strcmp.Sub(r'' + typeword + r'\w', substring + '0', startLine)
  #int a; /* if (*/ or int a; /* if( or  int a; /* adfa \n if */这三种情况skip，当成if的左右括号在一行，不check的情况
  typewordIndex = startLine.find(typeword)
  multiCommentStartIndex = startLine.find('/*')
  multiCommentEndIndex = startLine.find('*/')
  if multiCommentStartIndex > -1 and multiCommentEndIndex > -1 and \
  typewordIndex > multiCommentStartIndex and typewordIndex < multiCommentEndIndex:
    return 0,startLineNo,startLineNo
  elif multiCommentStartIndex == -1 and multiCommentEndIndex > -1 and typewordIndex < multiCommentEndIndex:
    return 0,startLineNo,startLineNo
  elif multiCommentEndIndex == -1 and multiCommentStartIndex > -1 and typewordIndex > multiCommentStartIndex:
    return 0,startLineNo,startLineNo
  #查找if，while所在行的缩进的空格数量，tab键作为4个空格
  indentation = 0
  m = strcmp.Search(r'^(\s*)\S', startLine)
  if m:
    indentation = len(m.group(1).replace('\t', '    '))
  #查找if(),while()中左右括号所在的行
  lengthOfLines = len(lines)
  openParenthesisQty = 0
  closeParenthesisQty = 0
  checkStartLineNo = -1
  checkEndLineNo = -1
  skipEndLno = -1
  line = ''
  for i in xrange(startLineNo, lengthOfLines):
    checkEndLineNo = i
    line = lines[i]
    if i == startLineNo:
      line = lines[i][startLine.find(typeword):]
    #空白行--skip
    if common.IsBlankLine(line):
      continue
    if i <= skipEndLno:
      continue
    #宏定义--skip
    if strcmp.Search(r'^\s*#\s*define\s+', line):
      skipEndLno = common.getDefineMacroEndLineNo(lines, i)
      continue
    #预定义--skip
    if strcmp.Search(r'^\s*#', lines[i]):
      skipEndLno = common.getDefineMacroEndLineNo(lines, i)
      continue
    openParenthesisQty = openParenthesisQty + line.count('(')
    closeParenthesisQty = closeParenthesisQty + line.count(')')
    if openParenthesisQty > 0 and checkStartLineNo == -1:
      checkStartLineNo = i
    if openParenthesisQty == closeParenthesisQty and openParenthesisQty > 0:
      break
  if openParenthesisQty != openParenthesisQty:
    return indentation, checkStartLineNo, -1
  return indentation, checkStartLineNo, checkEndLineNo

def checkIfStartWithDyadicOperator(currentLine, previousLine):
  #换行以二元操作符为起点check
  #二元操作符列表(逻辑运算符，比较运算符)
  #dyadicOperatorWithTwoCharactersArray = ['<=', '>=', '==', '!=', '&&', '||']
  dyadicOperatorWithTwoCharactersArray = ['&&', '||']
#  dyadicOperatorWithOneCharacterArray = ['<', '>', '|', '^']
#  #当起点是函数的参数时，不作为check对象
#  if currentLine.strip().startswith(',') or previousLine.endswith(',') or strcmp.Search(r'\b\w+\b\s*\($', previousLine):
#    return True
  char2 = currentLine.strip()[0:2]
  #如果起点是两个字符的二元操作符,return True
  if char2 in dyadicOperatorWithTwoCharactersArray:
    return True
  # if (c == token
  #     ->get()) 如果起点是->,不是二元操作符，return False
  if char2 == '->':
    return False
  #如果起点是1个字符的二元操作符,return True
#  char1 = currentLine.strip()[0:1]
#  if char1 in dyadicOperatorWithOneCharacterArray:
#    return True
  #其他的情况，说明起点不是二元操作符,return False
  return False
    

def checkNewLine(filename, indentation, lines, startLineNo, endLineNo, ruleCheckKey, Error, cpplines, fileErrorCount):
  errMessageHeader = 'Code Style Rule: If an expression is too long,'
  errorMessageIndentation = ' it should be wrapped, and the new line should indent 4 spaces.'
  errorMessageStartWord = ' it should be wrapped before a Logical AND (&&) or a Logical OR (||).'
  errorMessageBoth = ' it should be wrapped before a Logical AND (&&) or a Logical OR (||), and the new line should indent 4 spaces.'
  
  checkStartLineNo = startLineNo + 1
  maxLimit = endLineNo+ 1
  skipEndLno = -1
  previousLine = lines[startLineNo].strip()
  for i in xrange(checkStartLineNo, maxLimit):
    errorMessage = ''
    hasIndentationError = False
    hasStartWordError = False
    #if ( a > 1
    #   ) --如果最后一个右括号所在的行,右括号前没有代码，则不check
    if i == endLineNo and lines[i].strip().startswith(')') and lines[i].count(')') == 1:
      continue
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
    #新行相对缩进4个空格check
    tempIndentation = 0
    m = strcmp.Search(r'^(\s*)\S', lines[i])
    if m:
      tempIndentation = len(m.group(1).replace('\t', '    '))
    #  缩进错误，编辑errormessage
    if indentation + 4 != tempIndentation:
      hasIndentationError = True
    #换行以二元操作符为起点check
    #  不是以二元操作符为起点，编辑errormessage
    if not checkIfStartWithDyadicOperator(lines[i], previousLine):
      hasStartWordError = True
    #如果有错误信息，报错
    if hasIndentationError and hasStartWordError:
      errorMessage = errMessageHeader + errorMessageBoth
    elif hasIndentationError:
      errorMessage = errMessageHeader + errorMessageIndentation
    elif hasStartWordError:
      errorMessage = errMessageHeader + errorMessageStartWord
    if errorMessage:
      Error(filename, lines, i, ruleCheckKey, 3, errorMessage)
    #保存当前行，目的是下一行是以&开头时，判断&是一元操作符，还是二元操作符
    previousLine = lines[i].strip()

def CheckCSC020006(filename, file_extension, clean_lines, rawlines, nesting_state, ruleCheckKey, Error, cpplines, fileErrorCount):
  '''如果出现较长的表达式，也要进行换行。换行以二元逻辑操作符为起点，新行相对缩进4个空格。
  Args:
    filename:文件名
    file_extension:文件扩展名
    clean_lines:Holds 3 copies of all lines with different preprocessing applied to them
                 1) elided member contains lines without strings and comments,
                 2) lines member contains lines without comments, and
                 3) raw_lines member contains all the lines without processing.（行首以/*开头的多行注释被替换成空白）
    rawlines：all the lines without processing
    nesting_state: Holds states related to parsing braces.(cpplint中的对象，暂时未使用)
    startLineNo:for,while,if,switch所在的行
    ruleCheckKey:ruleid
    Error: error output method
  '''
  lines = clean_lines.elided
  i = 0
  while i < clean_lines.NumLines():
    #空白行--skip
    if common.IsBlankLine(lines[i]):
      i += 1
      continue
    #宏定义--skip
    if strcmp.Search(r'^\s*#\s*define\s+', lines[i]):
      i = common.getDefineMacroEndLineNo(lines, i) + 1
      continue
    #预定义--skip
    if strcmp.Search(r'^\s*#', lines[i]):
      i = common.getDefineMacroEndLineNo(lines, i) + 1
      continue
    #template<...> -- skip
    if strcmp.Search(r'^\s*template\s*<', lines[i]):
      i = getTemplateEndLno(lines, i)
      if i == -1:
        break
      else:
        i += 1
      continue
    m = strcmp.Search(r'(\bif\b|\bwhile\b)', lines[i])
    if m:
      indentation, startLineNo,endLineNo = getStatementStartEnd(lines, i, m.group(1))
      if endLineNo == -1 or endLineNo ==  clean_lines.NumLines() - 1:
        break
      if startLineNo == endLineNo:
        i = endLineNo + 1
        continue
      checkNewLine(filename,indentation, lines, startLineNo, endLineNo, ruleCheckKey, Error, cpplines, fileErrorCount)
      i = endLineNo
    i += 1