# -*- coding: utf-8 -*-
"""
Created on Wed Mar  2 14:45:19 2016

@author: navicloud
"""

import os
import sys

def lazyExit(code):
    pass

class RedirectStdStreams(object):
    def __init__(self, stdout=None, stderr=None, xit=None):
        stdout = stdout or sys.stdout
        stderr = stderr or sys.stderr
        xit    = xit if callable(xit) else sys.exit
        self._conf  = (stdout, stderr, xit)
        self._pconf = ()

    def __enter__(self):
        sys.stdout.flush()
        sys.stderr.flush()
        self._pconf = (sys.stdout, sys.stderr, sys.exit)
        sys.stdout, sys.stderr, sys.exit = self._conf

    def __exit__(self, exc_type, exc_value, traceback):
        sys.stdout.flush()
        sys.stderr.flush()
        sys.stdout, sys.stderr, sys.exit = self._pconf

if __name__ == '__main__':
    devnull = open(os.devnull, 'w')
    print('Fubar')

    with RedirectStdStreams(stdout=devnull, stderr=devnull):
        print("You'll never see me")

    print("I'm back!")