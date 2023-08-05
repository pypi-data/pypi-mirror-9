#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
Copyright (c) 2014 trgk

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
'''

from .allocator import *
from .eudobj import *
from .rawtrigger import *
from .mapdata import *
from .varfunc import *
from .calcf import *

# Re-define Memory, SetMemory here
# Stock Memory/SetMemory uses // operator, which cannot be applied to EUDVariable thing
# Somewhat hacky.
# TODO : check whether non-SC operators should be supported in EUDVariable
del Memory
del SetMemory

def Memory(addr, cmptype, number):
    if isinstance(addr, EUDVariable):
        return Deaths(f_div(addr - 0x58A364, 4), cmptype, number, 0)
    else:
        return Deaths((addr - 0x58A364) // 4, cmptype, number, 0)

def SetMemory(addr, modtype, number):
    if isinstance(addr, EUDVariable):
        return SetDeaths(f_div(addr - 0x58A364, 4), modtype, number, 0)
    else:
        return SetDeaths((addr - 0x58A364) // 4, modtype, number, 0)
