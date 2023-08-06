#!/usr/bin/env python

from __future__ import print_function
import gammu

state_machine = gammu.StateMachine()
state_machine.ReadConfig()
state_machine.Init()

status = state_machine.GetSMSStatus()

remain = status['SIMUsed'] + status['PhoneUsed'] + status['TemplatesUsed']

sms = []
start = True

try:
    while remain > 0:
        if start:
            cursms = state_machine.GetNextSMS(Start=True, Folder=0)
            start = False
        else:
            cursms = state_machine.GetNextSMS(
                Location=cursms[0]['Location'], Folder=0
            )
        remain = remain - len(cursms)
        sms.append(cursms)
except gammu.ERR_EMPTY:
    # This error is raised when we've reached last entry
    # It can happen when reported status does not match real counts
    print('Failed to read all messages!')

data = gammu.LinkSMS(sms)

for x in data:
    v = gammu.DecodeSMS(x)

    m = x[0]
    print()
    print('%-15s: %s' % ('Number', m['Number']))
    print('%-15s: %s' % ('Date', str(m['DateTime'])))
    print('%-15s: %s' % ('State', m['State']))
    print('%-15s: %s' % ('Folder', m['Folder']))
    print('%-15s: %s' % ('Validity', m['SMSC']['Validity']))
    loc = []
    for m in x:
        loc.append(str(m['Location']))
    print('%-15s: %s' % ('Location(s)', ', '.join(loc)))
    if v is None:
        print('\n%s' % m['Text'])
    else:
        for e in v['Entries']:
            print()
            print('%-15s: %s' % ('Type', e['ID']))
            if e['Bitmap'] is not None:
                for bmp in e['Bitmap']:
                    print('Bitmap:')
                    for row in bmp['XPM'][3:]:
                        print(row)
                print()
            if e['Buffer'] is not None:
                print('Text:')
                print(e['Buffer'])
                print()
