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

import math

from eudplib import (
    core as c,
    ctrlstru as cs,
    utils as ut,
)

from ..memiof import f_dwread_epd


@c.EUDFunc
def f_lengthdir(length, angle):
    # sin, cos table
    clist = []
    slist = []

    cs.DoActions(c.SetDeaths(1, c.Add, 1, 0))
    for i in range(91):
        cosv = math.floor(math.cos(math.pi / 180 * i) * 65536 + 0.5)
        sinv = math.floor(math.sin(math.pi / 180 * i) * 65536 + 0.5)
        clist.append(ut.i2b4(cosv))
        slist.append(ut.i2b4(sinv))

    cdb = c.Db(b''.join(clist))
    sdb = c.Db(b''.join(slist))

    # MAIN LOGIC

    cs.DoActions(c.SetDeaths(1, c.Add, 1, 0))
    if cs.EUDIf(angle >= 360):
        angle << c.f_div(angle, 360)[1]
    cs.EUDEndIf()

    cs.DoActions(c.SetDeaths(1, c.Add, 1, 0))
    ldir_x, ldir_y = c.EUDVariable(), c.EUDVariable()  # cos, sin * 65536
    # sign of cos, sin
    csign, ssign = c.EUDLightVariable(), c.EUDLightVariable()
    tableangle = c.EUDVariable()

    cs.DoActions(c.SetDeaths(1, c.Add, 1, 0))
    # get cos, sin from table
    if cs.EUDIf(angle <= 89):
        tableangle << angle
        csign << 1
        ssign << 1

    if cs.EUDElseIf(angle <= 179):
        tableangle << 180 - angle
        csign << -1
        ssign << 1

    if cs.EUDElseIf(angle <= 269):
        tableangle << angle - 180
        csign << -1
        ssign << -1

    if cs.EUDElse():
        tableangle << 360 - angle
        csign << 1
        ssign << -1

    cs.EUDEndIf()

    cs.DoActions(c.SetDeaths(1, c.Add, 1, 0))
    tablecos = f_dwread_epd(ut.EPD(cdb) + tableangle)
    tablesin = f_dwread_epd(ut.EPD(sdb) + tableangle)

    cs.DoActions(c.SetDeaths(1, c.Add, 1, 0))
    # calculate lengthdir
    ldir_x << c.f_div(c.f_mul(tablecos, length), 65536)[0]
    ldir_y << c.f_div(c.f_mul(tablesin, length), 65536)[0]

    cs.DoActions(c.SetDeaths(1, c.Add, 1, 0))
    # restore sign of cos, sin
    if cs.EUDIf(csign == -1):
        ldir_x << 0xFFFFFFFF - ldir_x + 1
    cs.EUDEndIf()

    if cs.EUDIf(ssign == -1):
        ldir_y << 0xFFFFFFFF - ldir_y + 1
    cs.EUDEndIf()

    cs.DoActions(c.SetDeaths(1, c.Add, 1, 0))
    return ldir_x, ldir_y
