#!/usr/bin/python  
#-*- coding: utf-8 -*-
'''
Created on 2014-12-10

@author: wangxc
'''
import os
import sys
syspath = os.path.dirname(os.path.dirname(__file__))
if not os.path.join(syspath, "tools") in sys.path:
  sys.path.append(os.path.join(syspath, "tools"))
import common
strcmp = common.StringCompareInfo()

def CheckCSC030029(filename, file_extension, clean_lines, rawlines, nesting_state, ruleCheckKey, Error, cpplines, fileErrorCount):
  '''如果做大括号{和右大括号}出现在一行，并且之间没有内容，请写在一起，不要留空格。[必须]
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
  errMessage = 'Code Style Rule: If a left curly brace "{" is closely followed by a right curly brace "}", there should be no space between them.'
  i = 0
  while i < clean_lines.NumLines():
    # null line skip
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
    # if no {, skip
    if lines[i].find('{') == -1:
      i += 1
      continue
    # 查看是否存在{}中全是空格的情况
    m = strcmp.Search(r'\{\s+\}', lines[i])
    # 不存在{}中全是空格的情况，进入下次循环
    if not m:
      i += 1
      continue
    # 存在{}中全是空格的情况,需要检查rawlines[i],避免if(...) { /*1111111*/  }被误判
    # 检查rawlines[i] --Start
    # 该行如果没有注释标识符/* 且 {...}中...全是空格，则报错
    if rawlines[i].find('/*') == -1:
      Error(filename, lines, i, ruleCheckKey, 3, errMessage)
      j = cpplines[i].find("{") + 1
      strTemp = "{"
      while j < len(cpplines[i]):
        if cpplines[i][j] == " ":
          strTemp += " "
          j += 1
        elif cpplines[i][j] == "}":
          fileErrorCount[0] += 1
          cpplines[i] = cpplines[i].replace(strTemp, "{")
          break
        else:
          break
      i += 1
      continue
    # 因为lines中已经去掉多行注释了，为了避免if(...) { /*1111111*/  }被误判,需要检查rawlines
    m = strcmp.Search(r'\{\s+\}', rawlines[i])
    # 不存在{}中全是空格的情况，进入下次循环
    if not m:
      i += 1
      continue
    startIndex = m.start()
    endIndex = m.end()
    inSingleQuotesblock = False
    inDoubleQuotesblock = False
    while startIndex != -1:
      # 判断{  }是否在两个单引号中间
      singleQuotesQty = rawlines[i][0:startIndex].count("'")
      if singleQuotesQty % 2 == 1 and rawlines[i][startIndex:].count("'") > 0:
        inSingleQuotesblock = True
      if not inSingleQuotesblock:
        # 判断{  }是否在两个双引号中间
        doubleQuotesQty = rawlines[i][0:startIndex].count('"')
        if doubleQuotesQty % 2 == 1 and rawlines[i][startIndex:].count('"') > 0:
          inDoubleQuotesblock = True
      # {  }在两个单引号中间或者在两个双引号中间,需要查找下一个{  }
      if inSingleQuotesblock or inDoubleQuotesblock:
        pass
      # {  }不是字符串中的字符
      else:
        # 为了避免注释中的{   }情况被误判
        # if(...) {} else { /*111 {    }1111*/  }
        # if(...) {} else { /*1111111*/  } // {    }
        # if(...) {} else { /*1111111*/  } /*1111111*/ /* {    }
        singleCommentIndex = rawlines[i][0:startIndex].rfind('//')
        multiCommentOpenIndex = rawlines[i][0:startIndex].rfind('/*')
        multiCommentCloseIndex = rawlines[i][0:startIndex].rfind('*/')
        isComment = False
        if singleCommentIndex == -1 and multiCommentOpenIndex == -1:
          pass
        # if(...) {} else { /*1111111*/  } /*1111111*/ /* {    }
        elif multiCommentOpenIndex > -1 and multiCommentOpenIndex > multiCommentCloseIndex:
          isComment =True
        # if(...) {} else { /*1111111*/  } /*1111111*/ // {    }
        # if(...) {} else { /*1111111*/  } //  /*1111111*/ {    }
        # if(...) {} else { /*1111111*/  } // 2345345*/ {    }
        elif singleCommentIndex > -1:
          if (multiCommentCloseIndex > -1 and singleCommentIndex > multiCommentCloseIndex) or \
             (multiCommentOpenIndex > -1 and singleCommentIndex < multiCommentOpenIndex) or \
              multiCommentOpenIndex == -1:
            isComment =True
        # if(...) {} else { /*1111111
        #                     if(...) {  } */
        multiCommentOpenIndex = rawlines[i][startIndex:].find('/*')
        multiCommentCloseIndex = rawlines[i][startIndex:].find('*/')
        if not isComment and multiCommentCloseIndex > -1 and multiCommentCloseIndex < multiCommentOpenIndex:
          isComment = True
        # {}中全是空格且不是注释的情况，报错,不再check本行了，check下一行
        if not isComment:
          Error(filename, lines, i, ruleCheckKey, 3, errMessage)
          j = cpplines[i].find("{") + 1
          strTemp = "{"
          while j < len(cpplines[i]):
            if cpplines[i][j] == " ":
              strTemp += " "
              j += 1
            elif cpplines[i][j] == "}":
              fileErrorCount[0] += 1
              cpplines[i] = cpplines[i].replace(strTemp, "{")
              break
            else:
              break
          i += 1
          startIndex = -1
          continue
      # 查找下一个{  }
      m = strcmp.Search(r'\{\s+\}', rawlines[i][endIndex:])
      if m:
        inSingleQuotesblock = False
        inDoubleQuotesblock = False
        startIndex = endIndex + m.start()
        endIndex = endIndex + m.end()
        continue
      # 查找不到下一个{  },不再检查本行了，去检查下一行
      else:
        i += 1
        startIndex = -1