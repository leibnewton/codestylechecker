#!/usr/bin/python  
#-*- coding: utf-8 -*-
'''
Created on 2014-1-24

@author: wangxc
'''
def cpplint_score_to_cppcheck_severity(score):
  if score == 1:
    return 'Info'
  elif score == 2:
    return 'Minor'
  elif score == 3:
    return 'Major'
  elif score == 4:
    return 'Critical'
  elif score == 5:
    return 'Blocker'