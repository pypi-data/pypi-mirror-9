#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# vim: expandtab sw=4 ts=4 sts=4:
#
# Copyright © 2003 - 2015 Michal Čihař <michal@cihar.com>
#
# This file is part of Gammu <http://wammu.eu/>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
'''
python-gammu - Test script to test several Gammu operations
(usually using dummy driver, but it depends on config)
'''

from __future__ import print_function
import gammu
import sys


def get_all_memory(state_machine, memory_type):
    status = state_machine.GetMemoryStatus(Type=memory_type)

    remain = status['Used']

    start = True

    while remain > 0:
        if start:
            entry = state_machine.GetNextMemory(Start=True, Type=memory_type)
            start = False
        else:
            entry = state_machine.GetNextMemory(
                Location=entry['Location'], Type=memory_type
            )
        remain = remain - 1

        print()
        print(('%-15s: %d' % ('Location', entry['Location'])))
        for v in entry['Entries']:
            if v['Type'] in ('Photo'):
                print(('%-15s: %s...' % (v['Type'], repr(v['Value'])[:30])))
            else:
                print((
                    '%-15s: %s' % (v['Type'], str(v['Value']).encode('utf-8'))
                ))


def get_all_calendar(state_machine):
    status = state_machine.GetCalendarStatus()

    remain = status['Used']

    start = True

    while remain > 0:
        if start:
            entry = state_machine.GetNextCalendar(Start=True)
            start = False
        else:
            entry = state_machine.GetNextCalendar(Location=entry['Location'])
        remain = remain - 1

        print()
        print(('%-20s: %d' % ('Location', entry['Location'])))
        print(('%-20s: %s' % ('Type', entry['Type'])))
        for v in entry['Entries']:
            print(('%-20s: %s' % (v['Type'], str(v['Value']).encode('utf-8'))))


def get_battery_status(state_machine):
    status = state_machine.GetBatteryCharge()

    for x in status:
        if status[x] != -1:
            print(("%20s: %s" % (x, status[x])))


def get_all_sms(state_machine):
    status = state_machine.GetSMSStatus()

    remain = status['SIMUsed'] + status['PhoneUsed'] + status['TemplatesUsed']

    start = True

    while remain > 0:
        if start:
            sms = state_machine.GetNextSMS(Start=True, Folder=0)
            start = False
        else:
            sms = state_machine.GetNextSMS(
                Location=sms[0]['Location'], Folder=0
            )
        remain = remain - len(sms)

    return sms


def print_sms_header(message, folders):
    print()
    print('%-15s: %s' % ('Number', message['Number'].encode('utf-8')))
    print('%-15s: %s' % ('Date', str(message['DateTime'])))
    print('%-15s: %s' % ('State', message['State']))
    print('%-15s: %s %s (%d)' % (
        'Folder',
        folders[message['Folder']]['Name'].encode('utf-8'),
        folders[message['Folder']]['Memory'].encode('utf-8'),
        message['Folder']
    ))
    print('%-15s: %s' % ('Validity', message['SMSC']['Validity']))


def print_all_sms(sms, folders):
    for m in sms:
        print_sms_header(m, folders)
        print('\n%s' % m['Text'].encode('utf-8'))


def link_all_sms(sms, folders):
    data = gammu.LinkSMS([[msg] for msg in sms])

    for x in data:
        v = gammu.DecodeSMS(x)

        m = x[0]
        print_sms_header(m, folders)
        loc = []
        for m in x:
            loc.append(str(m['Location']))
        print('%-15s: %s' % ('Location(s)', ', '.join(loc)))
        if v is None:
            print('\n%s' % m['Text'].encode('utf-8'))
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
                    print(e['Buffer'].encode('utf-8'))
                    print()


def get_all_todo(state_machine):
    status = state_machine.GetToDoStatus()

    remain = status['Used']

    start = True

    while remain > 0:
        if start:
            entry = state_machine.GetNextToDo(Start=True)
            start = False
        else:
            entry = state_machine.GetNextToDo(Location=entry['Location'])
        remain = remain - 1

        print()
        print('%-15s: %d' % ('Location', entry['Location']))
        print('%-15s: %s' % ('Priority', entry['Priority']))
        for v in entry['Entries']:
            print('%-15s: %s' % (v['Type'], str(v['Value']).encode('utf-8')))


def get_sms_folders(state_machine):
    folders = state_machine.GetSMSFolders()
    for i, folder in enumerate(folders):
        print('Folder %d: %s (%s)' % (
            i,
            folder['Name'].encode('utf-8'),
            folder['Memory'].encode('utf-8')
        ))
    return folders


def get_set_date_time(state_machine):
    dt = state_machine.GetDateTime()
    print(dt)
    state_machine.SetDateTime(dt)
    return dt


def main():
    if len(sys.argv) != 2:
        print('This requires one parameter with location of config file!')
        sys.exit(1)

    state_machine = gammu.StateMachine()
    state_machine.ReadConfig(Filename=sys.argv[1])
    state_machine.Init()
    smsfolders = get_sms_folders(state_machine)
    get_all_memory(state_machine, 'ME')
    get_all_memory(state_machine, 'SM')
    get_all_memory(state_machine, 'MC')
    get_all_memory(state_machine, 'RC')
    get_all_memory(state_machine, 'DC')
    get_battery_status(state_machine)
    get_all_calendar(state_machine)
    get_all_todo(state_machine)
    smslist = get_all_sms(state_machine)
    print_all_sms(smslist, smsfolders)
    link_all_sms(smslist, smsfolders)
    get_set_date_time(state_machine)

if __name__ == '__main__':
    main()
