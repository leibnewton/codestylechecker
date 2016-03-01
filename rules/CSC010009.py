#!/usr/bin/python  
#-*- coding: utf-8 -*-
'''
Created on 2014-2-10

@author: wangxc
'''
import os
import sys
syspath = os.path.dirname(os.path.dirname(__file__))
if not os.path.join(syspath, "tools") in sys.path:
  sys.path.append(os.path.join(syspath, "tools"))
import common
strcmp = common.StringCompareInfo()

def CheckCSC010009(filename, file_extension, clean_lines, rawlines, nesting_state, ruleCheckKey, Error, cpplines, fileErrorCount):
  if file_extension != "h":
    return
  dirName, fileNameWithoutPath = os.path.split(filename)
  # 文件名中含有半角英文，数字，下划线以外的字符时，比如汉字，全角字符等等，不check本规则
  if filename.count('.') > 1:
    return
  if strcmp.Search(r'\W', filename.replace('.','')):
    return
  headerGuardName = fileNameWithoutPath.replace('.','_').upper()
  lines = clean_lines.elided
  ifndef = None
  ifndef_linenum = -1
  define = None
  define_linenum = -1
  endif_linenum = -1
  for i in xrange(clean_lines.NumLines()):
    if common.IsBlankLine(lines[i]):
      continue
    linesplit = lines[i].strip(' \t').split()
    if len(linesplit) >= 2:
      # find the first occurrence of #ifndef, save arg
      if ifndef_linenum == -1 and linesplit[0] == '#ifndef':
      # set ifndef to the header guard presented on the #ifndef line.
        ifndef = linesplit[1]
        ifndef_linenum = i
      if define_linenum == -1 and ifndef_linenum != -1 and linesplit[0] == '#define':
        define = linesplit[1]
        define_linenum = i
    if lines[i].strip().startswith('#endif'):
      endif_linenum = i

  if ifndef_linenum == -1:
    Error(filename, lines, 0, ruleCheckKey, 3,'Code Style Rule: No #ifndef header guard found.')
    return
  if ifndef != headerGuardName:
    Error(filename, lines, ifndef_linenum, ruleCheckKey, 3,'Code Style Rule: The include guard has the wrong format, please use: %s' %headerGuardName)
    return
  if define_linenum == -1:
    Error(filename, lines, 0, ruleCheckKey, 3,'Code Style Rule: No #define header guard found.')
    return
  if ifndef_linenum + 1 != define_linenum:
    Error(filename, lines, ifndef_linenum, ruleCheckKey, 3,'Code Style Rule: The statement following the "#ifndef %s" should be "#define %s".' %(headerGuardName, headerGuardName))
    return
  if ifndef != define:
    Error(filename, lines, define_linenum, ruleCheckKey, 3,'Code Style Rule: #ifndef and #define do not match.')
    return
  if endif_linenum == -1:
    return
  else:
    m = strcmp.Search(r'\b' + headerGuardName + r'\b', rawlines[endif_linenum])
    if not m:
      Error(filename, lines, endif_linenum, ruleCheckKey, 3,'Code Style Rule: The "#endif" part of the include guard should be followed by comment like: /* %s */.' %headerGuardName)
  for i in xrange((endif_linenum + 1), clean_lines.NumLines()):
    if lines[i]:
      Error(filename, lines, i, ruleCheckKey, 3,'Code Style Rule: There should be no code after #endif, except for comments.')
      return