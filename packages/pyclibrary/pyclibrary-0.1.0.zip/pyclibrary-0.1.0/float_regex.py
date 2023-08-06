# -*- coding: utf-8 -*-
"""
Created on Wed Jan 21 09:05:46 2015

@author: Marul
"""

import re

fl = re.compile(r'[+-]?\s*((((\d(\.\d*)?)|(\.\d+))[eE][+-]?\d+)|((\d\.\d*)|(\.\d+)))')

print bool(fl.match('1.0'))
print bool(fl.match('+ 1.0'))
print bool(fl.match('- 1.0'))
print bool(fl.match('.0'))
print bool(fl.match('1E1'))
print bool(fl.match('+ 1e-1'))
print bool(fl.match('- 1e+2'))
print bool(fl.match('1.0e1'))

print bool(fl.match('1'))
