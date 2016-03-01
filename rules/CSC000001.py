#!/usr/bin/python  
#-*- coding: utf-8 -*-
'''
Created on 2014-2-11
rule:Logs an error if no Copyright message appears at the top of the file.
@author: wangxc
'''
import os
import sys
syspath = os.path.dirname(os.path.dirname(__file__))
if not os.path.join(syspath, "tools") in sys.path:
  sys.path.append(os.path.join(syspath, "tools"))
import CopyRightContents
import common
strcmp = common.StringCompareInfo()

def CheckCSC000001(filename, file_extension, clean_lines, rawlines, nesting_state, ruleCheckKey, Error, cpplines, fileErrorCount):
  
  errorMessage = 'Code Style Rule: Wrong format of the \"Copyright\" message in this line.'
  errorMessage2 = 'Code Style Rule: There should be copyright messages in this file.'
  errorMessage3 = 'Code Style Rule: The first line of the header file should be \"Copyright\" message.'
      
  #检查是是否有copyright的头
  i = -1
  for i in xrange(1,len(rawlines)):
    if strcmp.Search(r'\*\s+Copyright\s+@', rawlines[i]):
      break
  
  if i == len(rawlines) - 1:
    Error(filename, [], 1, ruleCheckKey, 3, errorMessage2)
    return

  # 查找不到/*
  if -1 == rawlines[1].find('/*'):
    Error(filename, [], 1, ruleCheckKey, 3, errorMessage3)
    return

  copyrightFixStr='Copyright @ '
  companyFixStr='Suntec Software'
  for i in xrange(1,len(CopyRightContents.contentsList)):
    
    #找到宏定义或者头文件引用，则文件头必然结束
    if strcmp.Search(r'^\s*#\s*define\s+', rawlines[i]):
      return
  
    pos = CopyRightContents.contentsList[i].find(copyrightFixStr)
    pos2 = CopyRightContents.contentsList[i].find(companyFixStr)
    pos3 = rawlines[i].find(companyFixStr)
    if -1 != pos:
      if -1 == pos2 or -1 == pos3 or CopyRightContents.contentsList[i][0:pos + len(copyrightFixStr)] != rawlines[i][0:pos + len(copyrightFixStr)] or \
          CopyRightContents.contentsList[i][pos2:] != rawlines[i][pos3:]:
        Error(filename, [], i, ruleCheckKey, 3, errorMessage)
        return 
      else :
        if not strcmp.SearchByPosition(r'\d{4}\s-\s\d{4}\s', rawlines[i], pos + len(copyrightFixStr), pos + len(copyrightFixStr) + 12) and \
            not strcmp.SearchByPosition(r'\d{4}\s' + companyFixStr, rawlines[i], pos + len(copyrightFixStr), pos + len(copyrightFixStr) + 5 + len(companyFixStr)) :
          Error(filename, [], i, ruleCheckKey, 3, errorMessage)
          return  
    
    else :
      if CopyRightContents.contentsList[i].strip() != rawlines[i].strip() :
        Error(filename, [], i, ruleCheckKey, 3, errorMessage)
        return
      