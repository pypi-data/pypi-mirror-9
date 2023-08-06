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
python-gammu - Phone communication libary

Gammu asynchronous wrapper example. This allows your application to care
only about handling received data and not about phone communication
details.
'''

from __future__ import print_function
import sys
import gammu
import gammu.worker


def callback(name, result, error, percents):
    '''
    Callback which is executed when something is done. Please remember
    this is called from different thread so it does not have to be save
    to work with GUI here.
    '''
    print(
        '-> %s completed %d%% with error %s , return value:' % (
            name,
            percents,
            error
        )
    )
    print(result)


def read_config():
    '''
    Reads gammu configuration.
    '''
    state_machine = gammu.StateMachine()
    # This is hack and should be as parameter of this function
    if len(sys.argv) == 2:
        state_machine.ReadConfig(Filename=sys.argv[1])
    else:
        state_machine.ReadConfig()
    return state_machine.GetConfig()


def main():
    '''
    Main code to talk with worker.
    '''
    worker = gammu.worker.GammuWorker(callback)
    worker.configure(read_config())
    # We can directly invoke commands
    worker.enqueue('GetManufacturer')
    worker.enqueue('GetSIMIMSI')
    worker.enqueue('GetIMEI')
    worker.enqueue('GetOriginalIMEI')
    worker.enqueue('GetManufactureMonth')
    worker.enqueue('GetProductCode')
    worker.enqueue('GetHardware')
    worker.enqueue('GetDateTime')
    # We can create compound tasks
    worker.enqueue('CustomGetInfo', commands=[
        'GetModel',
        'GetBatteryCharge'
        ])
    # We can pass parameters
    worker.enqueue('GetMemory', ('SM', 1))
    # We can create compound tasks with parameters:
    worker.enqueue('CustomGetAllMemory', commands=[
        ('GetMemory', ('SM', 1)),
        ('GetMemory', ('SM', 2)),
        ('GetMemory', ('SM', 3)),
        ('GetMemory', ('SM', 4)),
        ('GetMemory', ('SM', 5))
        ])
    print('All commands submitted')
    worker.initiate()
    print('Worker started')
    # We can also pass commands with named parameters
    worker.enqueue('GetSMSC', {'Location': 1})
    print('Submitted additional command')
    worker.terminate()
    print('Worker done')

if __name__ == '__main__':
    main()
