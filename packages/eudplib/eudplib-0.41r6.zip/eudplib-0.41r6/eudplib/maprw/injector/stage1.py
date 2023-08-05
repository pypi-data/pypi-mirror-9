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

''' Stage 1 : works in TRIG section.
- Check if EUD is available. If not, defeat
- Initialize stage 2 & execute it
- Modifies TRIG rawtrigger's nextptr. Modification is fixed in stage 3.
'''

from ... import core as c
from eudplib import utils as ut
from ...trigtrg import trigtrg as tt


trglist = []


def Trigger(*args, **kwargs):
    global trglist
    trglist.append(tt.Trigger(*args, **kwargs))


def CopyDeaths(iplayer, oplayer, copyepd=False, initvalue=None):
    tmpplayer = 11

    if initvalue is None:
        if copyepd:
            initvalue = tt.EPD(0)
        else:
            initvalue = 0

    Trigger(
        actions=[
            tt.SetDeaths(oplayer, tt.SetTo, initvalue, 0),
            tt.SetDeaths(tmpplayer, tt.SetTo, 0, 0),
        ]
    )

    for i in range(31, 1, -1):
        if copyepd:
            subval = 2 ** (i - 2)

        else:
            subval = 2 ** i

        Trigger(
            conditions=[tt.Deaths(iplayer, tt.AtLeast, 2 ** i, 0)],
            actions=[
                tt.SetDeaths(iplayer, tt.Subtract, 2 ** i, 0),
                tt.SetDeaths(tmpplayer, tt.Add, 2 ** i, 0),
                tt.SetDeaths(oplayer, tt.Add, subval, 0),
            ]
        )

    for i in range(31, 1, -1):
        Trigger(
            players=[tt.AllPlayers],
            conditions=[tt.Deaths(tmpplayer, tt.AtLeast, 2 ** i, 0)],
            actions=[
                tt.SetDeaths(iplayer, tt.Add, 2 ** i, 0),
                tt.SetDeaths(tmpplayer, tt.Subtract, 2 ** i, 0),
            ]
        )


def CreateAndApplyStage1(chkt, payload):
    global trglist

    # Append 'Require EUD enabler' to string table
    str_section = chkt.getsection('STR')
    strtb = c.TBL(str_section)
    eude_needed = strtb.GetStringIndex('This map requires EUD Enabler to run')
    str_section = strtb.SaveTBL()

    '''
    Algorithm credit to klassical_31@naver.com

    Overall algorithm : STR <-> MRGN cycle

    MRGN:
      SetMemory(payload, Add, payload_offset // 4)

    MRGN <-> STR0  =  Trigger(actions=[
             STR1        [SetMemory(
                            mrgn.action[i].player,
                            Add,
                            prttable[j+packn] - prttable[j]
                          ) for i in range(packn)],
             STR2        SetNextPtr(mrgn, STR[k+1])
             ...      )
    '''

    mrgn = 0x58DC60
    packn = 15

    #############
    # STR SECTION
    #############
    str_sled = []
    sledheader_prt = b'\0\0\0\0' + ut.i2b4(mrgn)
    sledheader_ort = b'\0\0\0\0' + ut.i2b4(mrgn + 2408)

    # apply prt
    prttrg_start = 2408 * len(str_sled)  # = 0
    # mrgn.action[i].player = EPD(payload_offset) + prevoffset[i]
    prevoffset = [-1] * packn
    for i in range(0, len(payload.prttable), packn):
        prts = list(map(lambda x: x // 4, payload.prttable[i: i + packn]))
        prts = prts + [-1] * (packn - len(prts))  # -1 : dummy space
        pch = [prts[j] - prevoffset[j] for j in range(packn)]
        str_sled.append(sledheader_prt + tt.Trigger(
            actions=[
                [tt.SetMemory(mrgn + 328 + 32 * j + 16, tt.Add, pch[j])
                 for j in range(packn)],
            ]
        ))

        prevoffset = prts

    # apply ort
    orttrg_start = 2408 * len(str_sled)  # = 0
    # mrgn.action[i].player = EPD(payload_offset) + prevoffset[i]
    prevoffset = [-1] * packn
    for i in range(0, len(payload.orttable), packn):
        orts = list(map(lambda x: x // 4, payload.orttable[i: i + packn]))
        orts = orts + [-1] * (packn - len(orts))  # -1 : dummy space
        pch = [orts[j] - prevoffset[j] for j in range(packn)]
        str_sled.append(sledheader_ort + tt.Trigger(
            actions=[
                [tt.SetMemory(mrgn + 2408 + 328 + 32 * j + 16, tt.Add, pch[j])
                 for j in range(packn)],
            ]
        ))

        prevoffset = orts

    # jump to ort
    str_sled.append(sledheader_ort + tt.Trigger(
        actions=[
            [tt.SetMemory(mrgn + 2408 + 328 + 32 * j + 16, tt.Add,
                          0xFFFFFFFF - prevoffset[j]) for j in range(packn)],
            tt.SetMemory(mrgn + 2408 + 4, tt.Add, 4)  # skip garbage area
        ]
    ))

    # sled completed
    str_sled = b''.join(str_sled)

    str_padding_length = -len(str_section) & 3
    strsled_offset = len(str_section) + str_padding_length
    payload_offset = strsled_offset + len(str_sled) + 4
    str_section = str_section + \
        bytes(str_padding_length) + str_sled + b'\0\0\0\0' + payload.data
    chkt.setsection('STR', str_section)

    ##############
    # MRGN SECTION
    ##############
    mrgn_trigger = []
    mrgn_trigger.append(
        bytes(4) + ut.i2b4(prttrg_start + strsled_offset) +
        tt.Trigger(
            actions=[
                # SetDeaths actions in MRGN initially points to EPD(payload -
                # 4)
                [tt.SetMemory(payload_offset - 4, tt.Add, payload_offset // 4)
                 for _ in range(packn)],
                tt.SetMemory(mrgn + 4, tt.Add, 2408)
            ]
        )
    )

    mrgn_trigger.append(
        bytes(4) + ut.i2b4(orttrg_start + strsled_offset) +
        tt.Trigger(
            actions=[
                [tt.SetMemory(payload_offset - 4, tt.Add, payload_offset)
                 for _ in range(packn)],
                tt.SetMemory(mrgn + 2408 + 4, tt.Add, 2408)
            ]
        )
    )

    mrgn_section = b''.join(mrgn_trigger) + bytes(5100 - 2408 * 2)
    chkt.setsection('MRGN', mrgn_section)

    ##############
    # TRIG SECTION
    ##############
    trglist.clear()

    # Check if epd is supported
    Trigger(actions=[
        tt.SetDeaths(-12, tt.SetTo, 1, 1)
    ])

    Trigger(
        conditions=[
            tt.Deaths(0, tt.Exactly, 0, 0)
        ],
        actions=[
            tt.DisplayTextMessage(eude_needed),
            tt.Draw()
        ]
    )

    Trigger(actions=[
        tt.SetDeaths(-12, tt.SetTo, 0, 1)
    ])

    # -------

    # Init mrgn rawtrigger
    strs = 0x5993D4
    for e in range(31, 1, -1):
        # prt table
        # player
        Trigger(
            conditions=tt.Memory(strs, tt.AtLeast, 2 ** e),
            actions=[
                [tt.SetMemory(mrgn + 328 + 32 * i + 16, tt.Add, 2 ** (e - 2))
                 for i in range(packn)],
                tt.SetDeaths(11, tt.Add, 2 ** e, 0),
                [tt.SetMemory(mrgn + 328 + 32 * i + 20, tt.Add, 2 ** (e - 2))
                 for i in range(packn)],
                tt.SetMemory(mrgn + 4, tt.Add, 2 ** e),
                [tt.SetMemory(
                    mrgn + 2408 + 328 + 32 * i + 16, tt.Add, 2 ** (e - 2)) for i in range(packn)],
                tt.SetMemory(mrgn + 2408 + 4, tt.Add, 2 ** e),
                [tt.SetMemory(mrgn + 2408 + 328 + 32 * i + 20, tt.Add, 2 ** e)
                 for i in range(packn)],
                tt.SetMemory(strs, tt.Subtract, 2 ** e),
            ]
        )

    for e in range(31, 1, -1):
        Trigger(
            conditions=tt.Deaths(11, tt.AtLeast, 2 ** e, 0),
            actions=[
                tt.SetDeaths(11, tt.Subtract, 2 ** e, 0),
                tt.SetMemory(strs, tt.Add, 2 ** e)
            ]
        )

    # Payload update
    curpl = 0x6509B0

    # -------

    # pts[player].lasttrigger->next = value(strs) + strsled_offset

    pts = 0x51A280

    for player in range(8):
        ptsprev = pts + 12 * player + 4  # address of pts[player].lasttrigger
        triggerend = ~(0x51A284 + player * 12)

        Trigger(
            players=[player],
            actions=[
                tt.SetMemory(curpl, tt.SetTo, ut.EPD(pts + 12 * player + 4)),
                tt.SetDeaths(9, tt.SetTo, triggerend, 0)  # Used in stage 2
            ]
        )

    # read pts[player].lasttrigger
    for e in range(31, 1, -1):
        Trigger(
            conditions=tt.Deaths(tt.CurrentPlayer, tt.AtLeast, 2 ** e, 0),
            actions=[
                tt.SetDeaths(tt.CurrentPlayer, tt.Subtract, 2 ** e, 0),
                tt.SetDeaths(10, tt.Add, 2 ** e, 0),
                tt.SetDeaths(11, tt.Add, 2 ** e, 0),
            ]
        )

    for e in range(31, 1, -1):
        Trigger(
            conditions=tt.Deaths(10, tt.AtLeast, 2 ** e, 0),
            actions=[
                tt.SetDeaths(10, tt.Subtract, 2 ** e, 0),
                tt.SetDeaths(tt.CurrentPlayer, tt.Add, 2 ** e, 0)
            ]
        )

    # apply to curpl
    Trigger(actions=[
        tt.SetDeaths(10, tt.SetTo, ut.EPD(4), 0),
        tt.SetMemory(curpl, tt.SetTo, ut.EPD(4))
    ])
    for e in range(31, 1, -1):
        Trigger(
            conditions=tt.Deaths(11, tt.AtLeast, 2 ** e, 0),
            actions=[
                tt.SetDeaths(11, tt.Subtract, 2 ** e, 0),
                # used for nextptr recovery in stage 3
                tt.SetDeaths(10, tt.Add, 2 ** (e - 2), 0),
                tt.SetMemory(curpl, tt.Add, 2 ** (e - 2))
            ]
        )

    # now curpl = EPD(value(ptsprev) + 4)
    # value(EPD(value(ptsprev) + 4)) = strs + payload_offset
    CopyDeaths(tt.EPD(strs), tt.CurrentPlayer, False, strsled_offset)

    # Done!
    trigdata = b''.join(trglist)

    # Stage 1 created

    # -------

    # Previous rawtrigger datas

    oldtrigraw = chkt.getsection('TRIG')
    oldtrigs = [oldtrigraw[i:i + 2400]
                for i in range(0, len(oldtrigraw), 2400)]
    proc_trigs = []

    # Collect only enabled triggers
    for trig in oldtrigs:
        trig = bytearray(trig)
        flag = ut.b2i4(trig, 320 + 2048)
        if flag & 8:  # Trigger already disabled
            pass

        flag ^= 8  # Disable it temporarilly. It will be re-enabled at stage 3
        trig[320 + 2048: 320 + 2048 + 4] = ut.i2b4(flag)
        proc_trigs.append(bytes(trig))

    oldtrigraw_processed = b''.join(proc_trigs)
    chkt.setsection('TRIG', trigdata + oldtrigraw_processed)
