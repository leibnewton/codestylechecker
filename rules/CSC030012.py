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

def CheckCSC030012(filename, file_extension, clean_lines, rawlines, nesting_state, ruleCheckKey, Error, cpplines, fileErrorCount):
  lines = clean_lines.elided
  errMessage = 'Code Style Rule: There must be a space after keywords like "if", "for", "while", etc. For example: if (...).'
  for i in xrange(clean_lines.NumLines()):
    if common.IsBlankLine(lines[i]):
      continue
    m = strcmp.Search(r'(\bif\b|\bfor\b|\bwhile\b|\bswitch\b|\bcatch\b)\(', lines[i])
    m2 = strcmp.Search(r'\bif\b|\bfor\b|\bwhile\b|\bswitch\b|\bcatch\b', lines[i].strip())
    if m or (m2 and m2.end() == len(lines[i].strip())):
      Error(filename, lines, i, ruleCheckKey, 3, errMessage)
      if m:
        fileErrorCount[0] += 1
        cpplines[i] = cpplines[i].replace("if(", "if (")
        cpplines[i] = cpplines[i].replace("for(", "for (")
        cpplines[i] = cpplines[i].replace("while(", "while (")
        cpplines[i] = cpplines[i].replace("switch(", "switch (")
        cpplines[i] = cpplines[i].replace("catch(", "catch (")