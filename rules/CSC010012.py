#!/usr/bin/python  
#-*- coding: utf-8 -*-
'''
Created on 2014-2-10

@author: wangxc
'''

def CheckCSC010012(filename, file_extension, clean_lines, rawlines, nesting_state, ruleCheckKey, Error, cpplines, fileErrorCount):
  if file_extension != file_extension.lower():
    Error(filename, [], 0, ruleCheckKey, 3,'Code Style Rule: The file extension must be in lowercase.')