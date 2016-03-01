#!/usr/bin/python  
#-*- coding: utf-8 -*-
'''
Created on 2014-3-19

@author: wangxc
'''
import sre_compile
import re
import unicodedata

_RE_STARTWITH_SPACE_HASHKEY = sre_compile.compile(r'^\s*#')
_RE_STARTWITH_SPACE_HASHKEY_DEFINE = sre_compile.compile(r'^\s*#\s*define\s+')

def getDefineMacroEndLineNo(lines, startLineNo):
  lengthOfLines = len(lines)
  for i in xrange(startLineNo, lengthOfLines):
    if not lines[i].rstrip().endswith("\\"):
      return i
  return startLineNo

def isClassDeclareCheck(lines, startLineNo):
  openCurlyBraceQty = 0
  closeCurlyBraceQty = 0
  lengthOfLines = len(lines)
  skipEndLno = -1
  endLineNo = -1
  checkStartLineNo = -1
  line = ''
  startLine = lines[startLineNo][lines[startLineNo].find('class'):]
  for i in xrange(startLineNo, lengthOfLines):
    endLineNo = i
    line = lines[i]
    if i == startLineNo:
      line = startLine
    if IsBlankLine(line):
      continue
    if _RE_STARTWITH_SPACE_HASHKEY.search(line):
      continue
    if i <= skipEndLno:
      continue
    if _RE_STARTWITH_SPACE_HASHKEY_DEFINE.search(line):
      skipEndLno = getDefineMacroEndLineNo(lines, i)
      continue
    openCurlyBraceQty = openCurlyBraceQty + line.count('{')
    closeCurlyBraceQty = closeCurlyBraceQty + line.count('}')
    if openCurlyBraceQty > 0 and checkStartLineNo == -1:
      checkStartLineNo = i
    if openCurlyBraceQty == closeCurlyBraceQty and line.rstrip().endswith(';'):
      break
  if openCurlyBraceQty != closeCurlyBraceQty:
    return False, checkStartLineNo, endLineNo
  if openCurlyBraceQty == 0:
    return False, checkStartLineNo, endLineNo
  if not line.rstrip().endswith(';'):
    return False, checkStartLineNo, endLineNo
  return True, checkStartLineNo, endLineNo

def IsBlankLine(line):
  """Returns true if the given line is blank.

  We consider a line to be blank if the line is empty or consists of
  only white spaces.

  Args:
    line: A line of a string.

  Returns:
    True, if the given line is blank.
  """
  return not line or line.isspace()

def hasChangeLineCharInCurrentLineOrPrevLine(lines, startLineNo):
  """Returns true if current line or previous line has change line character.

  Args:
    lines: line list.
    startLineNo: the current line's index in line list.

  Returns:
    True, if current line or previous line has change line character.
  """
  if len(lines) == 0:
    return False
  if lines[startLineNo].strip().endswith('\\'):
    return True
  i = startLineNo - 1
  while i < startLineNo and i >= 0:
    if IsBlankLine(lines[i]):
      i -= 1
      continue
    if lines[i].strip().endswith('\\'):
      return True
    else:
      return False
  return False

def GetLineWidth(line):
  """Determines the width of the line in column positions.

  Args:
    line: A string, which may be a Unicode string.

  Returns:
    The width of the line in column positions, accounting for Unicode
    combining characters and wide characters.
  """
  if isinstance(line, unicode):
    width = 0
    for uc in unicodedata.normalize('NFC', line):
      if unicodedata.east_asian_width(uc) in ('W', 'F'):
        width += 2
      elif not unicodedata.combining(uc):
        width += 1
    return width
  else:
    return len(line)

class StringCompareInfo(object):
  def __init__(self):
    self._regexp_compile_cache = {}

  def Sub(self, pattern, repl, s):
    """Replace the string for the pattern by the paramter repl, caching the compiled regexp."""
    # for example: s='a1234a' ,repl='OOOO' pattern = r'd+'
    # result is 'aOOOOa'
    #
    if not pattern in self._regexp_compile_cache:
      self._regexp_compile_cache[pattern] = sre_compile.compile(pattern)
    return self._regexp_compile_cache[pattern].sub(repl,s)

  def Match(self, pattern, s):
    """Matches the string with the pattern, caching the compiled regexp."""
    # The regexp compilation caching is inlined in both Match and Search for
    # performance reasons; factoring it out into a separate function turns out
    # to be noticeably expensive.
    if not pattern in self._regexp_compile_cache:
      self._regexp_compile_cache[pattern] = sre_compile.compile(pattern)
    return self._regexp_compile_cache[pattern].match(s)


  def FindAll(self, pattern, s):
    """Searches the string for the pattern, caching the compiled regexp."""
    if not pattern in self._regexp_compile_cache:
      self._regexp_compile_cache[pattern] = sre_compile.compile(pattern)
    return self._regexp_compile_cache[pattern].findall(s)

  def Search(self, pattern, s):
    """Searches the string for the pattern, caching the compiled regexp."""
    if not pattern in self._regexp_compile_cache:
      self._regexp_compile_cache[pattern] = sre_compile.compile(pattern)
    return self._regexp_compile_cache[pattern].search(s)

  def SearchByPosition(self, pattern, s, startPos, endPos):
    """Searches the string for the pattern, caching the compiled regexp."""
    if not pattern in self._regexp_compile_cache:
      self._regexp_compile_cache[pattern] = sre_compile.compile(pattern)
    return self._regexp_compile_cache[pattern].search(s, startPos, endPos)