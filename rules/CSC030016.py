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

def CheckCSC030016(filename, file_extension, clean_lines, rawlines, nesting_state, ruleCheckKey, Error, cpplines, fileErrorCount):
  '''可执行语句之后紧跟;，之间不要留空格。
     ;之后有可执行的内容时，其后要留空格。
     例子：
     for (initialization; condition; update) {
     ...
     }
     // 没内容时写成
     for (;;) {
     ...
     }
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
  # ;之后有可执行的内容时，其后要留空格
  notOneSpaceAfterSemicolonErrMessage = 'Code Style Rule: If the ";" does not mark the end of a sentence, there should be a space following it. For example: for (initialization; condition; update){...}.'
  # 可执行语句之后紧跟;，之间不要留空格
  hasSpaceInFrontOfSemicolonErrMessage = 'Code Style Rule: The semicolon ";" should follow closely with the statement before it, without any space.For example: statement;.'
  # ;前后没有可执行语句，不要有空格
  hasSpaceWithoutExecutableStatementEM = 'Code Style Rule: If there is no contents before/after a semicolon ";", please leave no space before/after it. For example: for(;;).'
  for i in xrange(clean_lines.NumLines()):
    if common.IsBlankLine(lines[i]):
      continue
    # 可执行语句之后紧跟;，之间不要留空格
    m = strcmp.Search(r'[^\s;\\\(\{\}]\s+;', lines[i])
    if m:
      Error(filename, lines, i, ruleCheckKey, 3, hasSpaceInFrontOfSemicolonErrMessage)
      fileErrorCount[0] += 1
      cpplines[i] = cpplines[i].replace(" ;", ";")
      continue
    # ;之后有可执行的内容时，其后没有空格
    m = strcmp.Search(r';[^\s;\\\)\}]', lines[i])
    if m:
      Error(filename, lines, i, ruleCheckKey, 3, notOneSpaceAfterSemicolonErrMessage)
      fileErrorCount[0] += 1
      icount = cpplines[i].count(";");
      if cpplines[i].endswith(";"):
        icount -= 1
      cpplines[i] = cpplines[i].replace(";", "; ", icount)
      continue
    # ;前后没有可执行语句，不要有空格
    m = strcmp.Search(r'[;\(]\s+;|;\s+\)', lines[i])
    if m:
      Error(filename, lines, i, ruleCheckKey, 3, hasSpaceWithoutExecutableStatementEM)
      fileErrorCount[0] += 1
      cpplines[i] = cpplines[i].replace("( ;", "(;")
      cpplines[i] = cpplines[i].replace("; ;", ";;")
      cpplines[i] = cpplines[i].replace("; )", ";)")
      continue