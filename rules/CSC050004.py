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

def codeCorrect(lines, lineNo, cpplines, fileErrorCount):
  m1 = strcmp.Search(r'(\w+)\s*(==|!=)\s*(false|true)\s*', lines[lineNo])
  m2 = strcmp.Search(r'\s*(false|true)\s*(==|!=)\s*(\w+)', lines[lineNo])
  while m1 or m2:
    booleanReplaceTag = ''
    if (m1 and m1.group(3) == 'true') or (m2 and m2.group(1) == 'true'):
      booleanReplaceTag = ''
    elif (m1 and m1.group(3) == 'false') or (m2 and m2.group(1) == 'false'):
      booleanReplaceTag = '!'
    
    index = -1
    searchStr = ''
    replaceStr = ''
    if m1:
      searchStr = m1.group(0)
      replaceStr = booleanReplaceTag + m1.group(1)
      index = lines[lineNo].find(searchStr)
    elif m2:
      searchStr = m2.group(0)
      replaceStr = booleanReplaceTag + m2.group(3)
      index = lines[lineNo].find(searchStr)
    
    cpplines[lineNo] = cpplines[lineNo].replace(searchStr, ' ' + replaceStr + ' ')
    fileErrorCount[0] =  fileErrorCount[0] + 1
    
    m1 = strcmp.Search(r'(\w+)\s*(==|!=)\s*(false|true)\s*', lines[lineNo][index + len(searchStr):])
    m2 = strcmp.Search(r'\s*(false|true)\s*(==|!=)\s*(\w+)', lines[lineNo][index + len(searchStr):]) 

def CheckCSC050004(filename, file_extension, clean_lines, rawlines, nesting_state, ruleCheckKey, Error, cpplines, fileErrorCount):
  lines = clean_lines.elided
  for i in xrange(clean_lines.NumLines()):
    if common.IsBlankLine(lines[i]):
      continue
    m1 = strcmp.Search(r'(\w+)\s*(==|!=)\s*(false|true)\s*', lines[i])
    m2 = strcmp.Search(r'\s*(false|true)\s*(==|!=)\s*(\w+)', lines[i])
    if m1 or m2:
      Error(filename, lines, i, ruleCheckKey, 3, "Code Style Rule: Please don\'t compare a bool variable with \"true\" or \"false\" using == or !=, use \"if(b)\" or \"if(!b)\" instead.")
      
      codeCorrect(lines, i, cpplines, fileErrorCount)