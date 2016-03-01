#!/usr/bin/python  
#-*- coding: utf-8 -*-
'''
Created on 2014-12-12

@author: wangxc
'''
import os
import sys      
syspath = os.path.dirname(os.path.dirname(__file__))
if not os.path.join(syspath, "tools") in sys.path:
  sys.path.append(os.path.join(syspath, "tools"))
import common
strcmp = common.StringCompareInfo()
sameCharactersQty = 3
asciiListExceptionAlphanumeric = ['!'*sameCharactersQty, '"'*sameCharactersQty, '#'*sameCharactersQty,
                                  '$'*sameCharactersQty, '%'*sameCharactersQty, '&'*sameCharactersQty,
                                  "'"*sameCharactersQty, '('*sameCharactersQty, ')'*sameCharactersQty,
                                  '*'*sameCharactersQty, '+'*sameCharactersQty, ','*sameCharactersQty,
                                  '-'*sameCharactersQty, '.'*sameCharactersQty, '/'*sameCharactersQty,
                                  ':'*sameCharactersQty, ';'*sameCharactersQty, '<'*sameCharactersQty,
                                  '='*sameCharactersQty, '>'*sameCharactersQty, '?'*sameCharactersQty,
                                  '@'*sameCharactersQty, '['*sameCharactersQty, '\\'*sameCharactersQty,
                                  ']'*sameCharactersQty, '^'*sameCharactersQty, '_'*sameCharactersQty,
                                  '`'*sameCharactersQty, '{'*sameCharactersQty, '|'*sameCharactersQty,
                                  '}'*sameCharactersQty, '~'*sameCharactersQty]
def getMultiCommentEndLno(lines, startLine, linestartLno):
  '''查找多行注释
  Args:
    lines:所有行
    startLine:/*所在行的/*后的字符串
    linestartLno:/*所在行的line number
  Returns:
            返回离/*最近的*/所在的line number；如果查不到*/，则返回-1
  '''
  # 查找离/*最近的*/所在的line number
  if startLine.find('*/') > -1:
    return linestartLno
  i = linestartLno + 1
  while i < len(lines):
    if lines[i].find('*/') > -1:
      return i
    i = i + 1
  # 如果查不到*/，则返回-1，说明文件有问题，不要再check该文件了
  return -1


def makeCodeCorrect(searchStr, replaceStr, lineNo, cpplines, fileErrorCount):
    cpplines[lineNo] = cpplines[lineNo].replace(searchStr, replaceStr)
    fileErrorCount[0] =  fileErrorCount[0] + 1

def CheckCSC030021(filename, file_extension, clean_lines, rawlines, nesting_state, ruleCheckKey, Error, cpplines, fileErrorCount):
  '''注释标示符与注释内容之间，至少保留一个空格。
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
  errMessage = "Code Style Rule: There should be at least one space between the comment mark and the comment contents."
  commentEndLno = -1
  currentHasError = False
  for i in xrange(clean_lines.NumLines()):
    # /**/多行注释换行时，中间行不用check
    if i < commentEndLno:
      continue

    # 该行是空行（或者该行全是注释）时------------------------>
    # 文档注释-- /** 注释 */  -- 区块说明-------不能出现在语句尾部
    # 文档注释-- /// 注释           -- 区块的简易说明-------不能出现在语句尾部
    # 文档注释-- /**< 注释 */ -- 代码行说明
    # 文档注释-- ///< 注释         -- 代码行说明
    # 代码注释-- /* 注释 */   -- 长文/多行注释
    # 代码注释-- // 注释              -- 简短注释
    startIndex = -1
    endIndex = -1
    currentHasError = False
    if common.IsBlankLine(lines[i]):
      # 该行是空行时,skip
      if common.IsBlankLine(rawlines[i]):
        continue

      # 查找当行是否有注释标识符
      # 当前行是多行注释的*/所在的行时,即当前行是下面例子中的第2行时,从第2行的*/后面开始check
      # /* 2222
      #   /* 2222 */ // 333333
      if commentEndLno == i:
        commentEndLno = -1
        startIndex = rawlines[i].find('*/')
        # 找不到对应的*/,文件有错误，不再check本文件
        if startIndex == -1:
          break
        # 如果*/前是连续的符号，不报错
        if startIndex >= sameCharactersQty and rawlines[i][startIndex - sameCharactersQty:startIndex] in asciiListExceptionAlphanumeric:
          pass
        # */前没有空格（*/除外）,报错
        # /* 2222
        #   /* 2222*/
        elif rawlines[i][startIndex - 1] not in [' ','\t'] and (not currentHasError) and startIndex > 0:
          currentHasError =True
          Error(filename, lines, i, ruleCheckKey, 3, errMessage)
          
          makeCodeCorrect('*/', ' */',i, cpplines, fileErrorCount)
      # 当前行是多行注释的第一行时(因为上面的[if i < commentEndLno:continue]已经过滤了多行注释的中间行)
      else:
        m = strcmp.Search(r'(/\*|//)', rawlines[i])
        # 匹配不了多行注释的首字符串，文件有错误，不再check本文件
        if not m:
          break
        # 以下三种注释的注释标识符与内容间没有空格的话，报错
        # 文档注释-- /// 注释           -- 区块的简易说明
        # 文档注释-- ///< 注释         -- 代码行说明
        # 代码注释-- // 注释              -- 简短注释
        m1 = strcmp.Search(r'^\s*///<\S', rawlines[i])
        if m1:
          # 如果注释符号之后是连续的符号，不报错
          if not rawlines[i][m1.end() - 1: m1.end() - 1 + sameCharactersQty] in asciiListExceptionAlphanumeric:
            commentEndLno = -1
            Error(filename, lines, i, ruleCheckKey, 3, errMessage)
            makeCodeCorrect('///<', '///< ', i, cpplines, fileErrorCount)
            continue
        m2 = strcmp.Search(r'^\s*(///[^\s<]|//[^\s/@])', rawlines[i])
        if m2:
          # 如果注释符号之后是连续的符号，不报错
          if not rawlines[i][m2.end() - 1: m2.end() - 1 + sameCharactersQty] in asciiListExceptionAlphanumeric:
            commentEndLno = -1
            Error(filename, lines, i, ruleCheckKey, 3, errMessage)
            makeCodeCorrect(m2.group(1)[0:len(m2.group(1)) - 1], m2.group(1)[0:len(m2.group(1)) - 1] + ' ', i, cpplines, fileErrorCount)
            continue
        m3 = strcmp.Search(r'^\s*//@[\{\}]\S', rawlines[i])
        if m3:
          # 如果注释符号之后是连续的符号，不报错
          if not rawlines[i][m3.end() - 1: m3.end() - 1 + sameCharactersQty] in asciiListExceptionAlphanumeric:
            commentEndLno = -1
            Error(filename, lines, i, ruleCheckKey, 3, errMessage)
            makeCodeCorrect(m3.group(0)[0:m3.end() - 1], m3.group(0)[0:m3.end() - 1] + ' ', i, cpplines, fileErrorCount)
            continue
        if rawlines[i].lstrip().startswith('//'):
          continue
        m = strcmp.Search(r'^\s*(/\*\*<{0,1}|/\*[^\*]{0,1})', rawlines[i])
        # 匹配不了多行注释的首字符串，文件有错误，不再check本文件
        if not m:
          return
        # 注释标识符后不是空白时，报错
        # /**A  error
        # /**<A error
        # /*A   error
        if m.group(1) in ['/**<','/**']:
          # 如果注释符号之后是连续的符号，不报错
          if rawlines[i][m.end(): m.end() + sameCharactersQty] in asciiListExceptionAlphanumeric:
            pass
          # /** or /**<后不是空格，报错
          elif  m.end() != len(rawlines[i]) and rawlines[i][m.end()] not in [' ','\t'] and (not currentHasError):
            currentHasError = True
            Error(filename, lines, i, ruleCheckKey, 3, errMessage)
            makeCodeCorrect(m.group(1), m.group(1) + ' ', i, cpplines, fileErrorCount)
        else:
          if len(m.group(1)) == 3:
            # 如果是/*!
            if m.group(1) == '/*!':
              # 如果注释符号之后是连续的符号，不报错
              if rawlines[i][m.end(): m.end() + sameCharactersQty] in asciiListExceptionAlphanumeric:
                pass
              # /*!后不是空格，报错
              elif rawlines[i][m.end(): m.end() + 1] not in [' ','\t'] and rawlines[i][m.end(): m.end() + 1] != '' and (not currentHasError):
                currentHasError = True
                Error(filename, lines, i, ruleCheckKey, 3, errMessage)
                makeCodeCorrect(m.group(1), m.group(1) + ' ', i, cpplines, fileErrorCount)
            # 不是/*!
            else:
              # 如果注释符号之后是连续的符号，不报错
              if rawlines[i][m.end() - 1: m.end() - 1 + sameCharactersQty] in asciiListExceptionAlphanumeric:
                pass
              # /*后不是空格，报错
              elif m.group(1)[2] not in [' ','\t'] and (not currentHasError):
                currentHasError = True
                Error(filename, lines, i, ruleCheckKey, 3, errMessage)
                makeCodeCorrect('/*', '/* ', i, cpplines, fileErrorCount)
        if m.group(1) == '/**':
          commentEndLno = getMultiCommentEndLno(rawlines, rawlines[i][m.end() - 1:], i)
        else:
          commentEndLno = getMultiCommentEndLno(rawlines, rawlines[i][m.end():], i)
        # 如果返回-1，说明查不到*/,文件有问题，不要再check该文件了
        if commentEndLno == -1:
          return
        # /*对应的*/在下一行时
        if commentEndLno > i:
          continue
        # /*对应的*/在本行时
        # check */前是否有空白，如果紧跟着注释内容，则报错
        startIndex = rawlines[i].find('*/')
        # 找不到对应的*/,文件有错误，不再check本文件
        if startIndex == -1:
          break
        # 如果*/前是连续的符号，不报错
        if startIndex >= sameCharactersQty and rawlines[i][startIndex - sameCharactersQty:startIndex] in asciiListExceptionAlphanumeric:
          pass
        # */前不是空格，报错
        elif rawlines[i][startIndex - 1] not in[' ', '\t'] and (not currentHasError) and startIndex > 0:
          currentHasError =True
          Error(filename, lines, i, ruleCheckKey, 3, errMessage)
          makeCodeCorrect('*/', ' */', i, cpplines, fileErrorCount)
      m = strcmp.Search(r'(/\*|//)', rawlines[i][startIndex + 2:])
      if not m:
        continue
      # 当前行还有其他注释时
      # 1./*  111111111*/ //
      # 2./*  222222222*/ /*3333
      # 3./*  111111111
      #       222222222*/ /*3333
      startIndex = startIndex + 2 + m.start()
      lenghOfLine = len(rawlines[i])
      while startIndex != -1 and startIndex < lenghOfLine:
        # 下列情况报错
        # 1./*  111111111*/ //A
        # 2./*  111111111*/ ///A
        # 3./*  111111111*/ ///<A
        m1 = strcmp.Search(r'^\s*///<\S', rawlines[i][startIndex:])
        if m1 and (not currentHasError):
          # 如果注释符号之后不是连续的符号 and ///<后不是空格，报错
          if not rawlines[i][startIndex:][m1.end() - 1: m1.end() - 1 + sameCharactersQty] in asciiListExceptionAlphanumeric:
            Error(filename, lines, i, ruleCheckKey, 3, errMessage)
            makeCodeCorrect('///<', '///< ', i, cpplines, fileErrorCount)
            currentHasError = True
        if not currentHasError:
          m2 = strcmp.Search(r'^\s*(///[^\s<]|//[^\s/@])', rawlines[i][startIndex:])
          if m2:
            # 如果注释符号之后不是连续的符号 and (///后不是空格 or //后不是空格 ,/, @)，报错
            if not rawlines[i][startIndex:][m2.end() - 1: m2.end() - 1 + sameCharactersQty] in asciiListExceptionAlphanumeric:
              Error(filename, lines, i, ruleCheckKey, 3, errMessage)
              makeCodeCorrect(m2.group(1)[0:len(m2.group(1)) - 1], m2.group(1)[0:len(m2.group(1)) - 1] + ' ', i, cpplines, fileErrorCount)
              currentHasError = True
        if not currentHasError:
          m3 = strcmp.Search(r'^\s*//@[\{\}]\S', rawlines[i][startIndex:])
          if m3:
            # 如果注释符号之后不是连续的符号 and (//@{ or //@}后不是空格 )，报错
            if not rawlines[i][startIndex:][m3.end() - 1: m3.end() - 1 + sameCharactersQty] in asciiListExceptionAlphanumeric:
              Error(filename, lines, i, ruleCheckKey, 3, errMessage)
              makeCodeCorrect(m3.group(0)[0:m3.end() - 1], m3.group(0)[0:m3.end() - 1] + ' ', i, cpplines, fileErrorCount)
              currentHasError = True
        # 查找注释结束的行号
        # 注释标识符是//, ///, ///<时，说明*/后是单行注释，查找下一行
        if m.group(1) == '//':
          commentEndLno = i
          break
        # 注释标识符是/*, /**, /**<时，
        # 下列情况报错
        # 1./*  111111111*/ /*A
        # 2./*  111111111*/ /**A
        # 3./*  111111111*/ /**<A
        m = strcmp.Search(r'^\s*(/\*\*<{0,1}|/\*[^\*]{0,1})', rawlines[i][startIndex:])
        # /*  111111111*/ /**<  ok
        # /*  111111111*/ /**   ok
        # /*  111111111*/ /*    ok
        # /*  111111111*/ /**A  error
        # /*  111111111*/ /**<A error
        # /*  111111111*/ /*A   error
        if m.group(1) in ['/**<','/**']:
          # 如果注释符号之后是连续的符号，不报错
          if rawlines[i][startIndex:][m.end(): m.end() + sameCharactersQty] in asciiListExceptionAlphanumeric:
            pass
          # /** or /**<后不是空格，报错
          elif  m.end() != len(rawlines[i][startIndex:]) and rawlines[i][startIndex + m.end()] not in [' ','\t'] and (not currentHasError):
            currentHasError = True
            Error(filename, lines, i, ruleCheckKey, 3, errMessage)
            makeCodeCorrect(m.group(1), m.group(1) + ' ', i, cpplines, fileErrorCount)
        elif len(m.group(1)) == 3:
          # 如果是/*!
          if m.group(1) == '/*!':
            # 如果注释符号之后是连续的符号，不报错
            if rawlines[i][startIndex:][m.end(): m.end() + sameCharactersQty] in asciiListExceptionAlphanumeric:
              pass
            # /*!后不是空格，报错
            if rawlines[i][startIndex:][m.end(): m.end() + 1] not in [' ','\t'] and rawlines[i][startIndex:][m.end(): m.end() + 1] != '' and (not currentHasError):
              currentHasError = True
              Error(filename, lines, i, ruleCheckKey, 3, errMessage)
              makeCodeCorrect(m.group(1), m.group(1) + ' ', i, cpplines, fileErrorCount)
          # 如果不是/*!
          else:
            # 如果注释符号之后是连续的符号，不报错
            if rawlines[i][startIndex:][m.end() - 1: m.end() - 1 + sameCharactersQty] in asciiListExceptionAlphanumeric:
              pass
            # /*后不是空格，报错
            elif m.group(1)[2] not in [' ','\t'] and (not currentHasError):
              currentHasError = True
              Error(filename, lines, i, ruleCheckKey, 3, errMessage)
              makeCodeCorrect('/*', '/* ', i, cpplines, fileErrorCount)
        #查找/*对应的*/所在的行号
        if m.group(1) == '/**':
          startIndex = startIndex + m.end() - 1
        else:
          startIndex = startIndex + m.end()
        commentEndLno = getMultiCommentEndLno(rawlines, rawlines[i][startIndex:], i)
        # 如果返回-1，说明查不到*/,文件有问题，不要再check该文件了
        if commentEndLno == -1:
          return
        # /*对应的*/在下一行时
        if commentEndLno > i:
          break
        # /*对应的*/在本行时
        # check */前是否有空白，如果紧跟着注释内容，则报错
        closeCommentIndex = rawlines[i][startIndex:].find('*/')
        startIndex = startIndex + closeCommentIndex
        # 如果*/前是连续的符号，不报错
        if startIndex >= sameCharactersQty and rawlines[i][startIndex - sameCharactersQty:startIndex] in asciiListExceptionAlphanumeric:
          pass
        # */前不是空格，报错
        elif rawlines[i][startIndex - 1] not in[' ', '\t'] and (not currentHasError) and closeCommentIndex > 0:
          currentHasError = True
          Error(filename, lines, i, ruleCheckKey, 3, errMessage)
          makeCodeCorrect('*/', ' */', i, cpplines, fileErrorCount)
        # */后还有注释时
        # /*  111111111*/ /* 
        m = strcmp.Search(r'(/\*|//)', rawlines[i][startIndex + 2:])
        if m:
          startIndex = startIndex + 2 + m.start()
          continue
        else:
          break
      # 该行全是注释,结束该行代码的处理，进入下次循环
      continue
    # 该行是空行（或者该行全是注释）时<------------------------

    # 当前行有代码时------------------------>
    # 当前行有代码，则认为当前行上的注释是代码注释，而不可能是文档注释，只能是//或者/*属于注释标识符，/**, ///等都认为是错误
    # 查找当行是否有注释标识符
    # 当前行是多行注释的*/所在的行时,即当前行是下面例子中的第2行时,从第2行的*/后面开始查找
    # String a; /* 1111 */ String b; /* 2222
    #                                /* 2222 */ String C; // 333333
    if commentEndLno == i:
      commentEndLno = -1
      startIndex = rawlines[i].find('*/')
      if startIndex == -1:
        break
      # 如果*/前是连续的符号，不报错
      if startIndex >= sameCharactersQty and rawlines[i][startIndex - sameCharactersQty:startIndex] in asciiListExceptionAlphanumeric:
          pass
      # */前没有空格（*/除外）,报错
      # /* 2222
      #   /* 2222*/ String a;
      elif rawlines[i][startIndex - 1] not in [' ','\t'] and (not currentHasError) and startIndex > 0:
        currentHasError =True
        Error(filename, lines, i, ruleCheckKey, 3, errMessage)
        makeCodeCorrect('*/', ' */', i, cpplines, fileErrorCount)
      m = strcmp.Search(r'(/\*|//)', rawlines[i][startIndex + 2:])
      if m:
        startIndex = startIndex + 2 + m.start()
    # 当前行的开头不是注释时
    else:
      m = strcmp.Search(r'(/\*|//)', rawlines[i])
      if m:
        startIndex = m.start()
    if not m:
      continue
    inSingleQuotesblock = False
    inDoubleQuotesblock = False
    lenghOfLine = len(rawlines[i])
    while startIndex != -1 and startIndex < lenghOfLine:
      # 判断注释标识符是否在两个单引号中间
      singleQuotesQty = rawlines[i][0:startIndex].count("'")
      if singleQuotesQty % 2 == 1 and rawlines[i][startIndex:].count("'") > 0:
        inSingleQuotesblock = True
      if not inSingleQuotesblock:
        # 判断注释标识符是否在两个双引号中间
        doubleQuotesQty = rawlines[i][0:startIndex].count('"')
        if doubleQuotesQty % 2 == 1 and rawlines[i][startIndex:].count('"') > 0:
          inDoubleQuotesblock = True
      # 注释标识符在两个单引号中间或者在两个双引号中间,查找下一个注释标识符
      if inSingleQuotesblock or inDoubleQuotesblock:
        pass
      # 注释标识符的确是注释的标志，而不是字符串中的字符
      else:
        # 下列情况报错
        # 1./*  111111111 */ String a; //A
        # 2./*  111111111 */ String a; /// aaaa
        # 3./*  111111111 */ String a; ///<A
        m1 = strcmp.Search(r'^//[^\s/]', rawlines[i][startIndex:])
        if m1 and (not currentHasError):
          # 如果注释符号之后不是连续的符号 and //后不是(/,空格)，报错
          if not rawlines[i][startIndex:][m1.end() - 1: m1.end() - 1 + sameCharactersQty] in asciiListExceptionAlphanumeric:
            Error(filename, lines, i, ruleCheckKey, 3, errMessage)
            makeCodeCorrect(m1.group(0)[0:m1.end() - 1], m1.group(0)[0:m1.end() - 1] + ' ', i, cpplines, fileErrorCount)
            currentHasError = True
        if not currentHasError:
          m2 = strcmp.Search(r'^///[^<]', rawlines[i][startIndex:])
          if m2:
            # 如果注释符号之后不是连续的符号 and ///后不是<，报错
            if not rawlines[i][startIndex:][m2.end() - 1: m2.end() - 1 + sameCharactersQty] in asciiListExceptionAlphanumeric:
              Error(filename, lines, i, ruleCheckKey, 3, errMessage)
              makeCodeCorrect(m2.group(0)[0:m2.end() - 1], m2.group(0)[0:m2.end() - 1] + ' ', i, cpplines, fileErrorCount)
              currentHasError = True
        if not currentHasError:
          m3 = strcmp.Search(r'^///<\S', rawlines[i][startIndex:])
          if m3:
            # 如果注释符号之后不是连续的符号 and ///<后不是空格，报错
            if not rawlines[i][startIndex:][m3.end() - 1: m3.end() - 1 + sameCharactersQty] in asciiListExceptionAlphanumeric:
              Error(filename, lines, i, ruleCheckKey, 3, errMessage)
              makeCodeCorrect(m3.group(0)[0:m3.end() - 1], m3.group(0)[0:m3.end() - 1] + ' ', i, cpplines, fileErrorCount)
              currentHasError = True
        # 查找注释结束的行号
        # 注释标识符是//, ///, ///<时，说明*/后是单行注释，查找下一行
        if m.group(1) == '//':
          commentEndLno = i
          break
        # 注释标识符是/*时，
        # /*  111111111 */ /* a  ok
        # /*  111111111 */ /**   error
        # /*  111111111 */ /**<  ok
        # /*  111111111 */ /**A  error
        # /*  111111111 */ /**<A error
        # /*  111111111 */ /*A   error
        m1 = strcmp.Search(r'^/\*[^\s\*\!]', rawlines[i][startIndex:])
        if m1 and (not currentHasError):
          # 如果注释符号之后不是连续的符号 and /*后不是(*,空格)，报错
          if not rawlines[i][startIndex:][m1.end() - 1: m1.end() - 1 + sameCharactersQty] in asciiListExceptionAlphanumeric:
            Error(filename, lines, i, ruleCheckKey, 3, errMessage)
            makeCodeCorrect('/*', '/* ', i, cpplines, fileErrorCount)
            currentHasError = True
        if not currentHasError:
          m2 = strcmp.Search(r'^/\*\*[^<]', rawlines[i][startIndex:])
          if m2:
            # 如果注释符号之后不是连续的符号 and /**后不是<，报错
            if not rawlines[i][startIndex:][m2.end() - 1: m2.end() - 1 + sameCharactersQty] in asciiListExceptionAlphanumeric:
              Error(filename, lines, i, ruleCheckKey, 3, errMessage)
              makeCodeCorrect(m2.group(0)[0:m2.end() - 1], m2.group(0)[0:m2.end() - 1] + ' ', i, cpplines, fileErrorCount)
              currentHasError = True
        if not currentHasError:
          m3 = strcmp.Search(r'^/\*\*<\S', rawlines[i][startIndex:])
          if m3:
            # 如果注释符号之后不是连续的符号 and /**<后不是空格，报错
            if not rawlines[i][startIndex:][m3.end() - 1: m3.end() - 1 + sameCharactersQty] in asciiListExceptionAlphanumeric:
              Error(filename, lines, i, ruleCheckKey, 3, errMessage)
              makeCodeCorrect(m3.group(0)[0:m3.end() - 1], m3.group(0)[0:m3.end() - 1] + ' ', i, cpplines, fileErrorCount)
              currentHasError = True
        if not currentHasError:
          m4 = strcmp.Search(r'^/\*\!\S', rawlines[i][startIndex:])
          if m4:
            # 如果注释符号之后不是连续的符号 and /*!后不是空格，报错
            if not rawlines[i][startIndex:][m4.end() - 1: m4.end() - 1 + sameCharactersQty] in asciiListExceptionAlphanumeric:
              Error(filename, lines, i, ruleCheckKey, 3, errMessage)
              makeCodeCorrect(m4.group(0)[0:m4.end() - 1], m4.group(0)[0:m4.end() - 1] + ' ', i, cpplines, fileErrorCount)
              currentHasError = True
        #查找/*对应的*/所在的行号
        startIndex = startIndex + 2
        commentEndLno = getMultiCommentEndLno(rawlines, rawlines[i][startIndex:], i)
        # 如果返回-1，说明查不到*/,文件有问题，不要再check该文件了
        if commentEndLno == -1:
          return
        # /*对应的*/在下一行时
        if commentEndLno > i:
          break
        # /*对应的*/在本行时
        # check */前是否有空白，如果紧跟着注释内容，则报错
        closeCommentIndex = rawlines[i][startIndex:].find('*/')
        startIndex = startIndex + closeCommentIndex
        # 如果*/前是连续的符号，不报错
        if startIndex >= sameCharactersQty and rawlines[i][startIndex - sameCharactersQty:startIndex] in asciiListExceptionAlphanumeric:
          pass
        # */前不是空格，报错
        elif rawlines[i][startIndex - 1] not in[' ', '\t'] and (not currentHasError) and closeCommentIndex > 0:
          currentHasError = True
          Error(filename, lines, i, ruleCheckKey, 3, errMessage)
          makeCodeCorrect('*/', ' */', i, cpplines, fileErrorCount)
      # 字符串中的/*(or //)还有注释  or */后还有注释时
      # 1. String a= "/*";/*aaaaaaaa
      # 2./*  111111111*/String a; /* 2222222
      m = strcmp.Search(r'(/\*|//)', rawlines[i][startIndex + 2:])
      if m:
        inSingleQuotesblock = False
        inDoubleQuotesblock = False
        startIndex = startIndex + 2 + m.start()
        continue
      else:
        break
    # 当前行有代码时<------------------------