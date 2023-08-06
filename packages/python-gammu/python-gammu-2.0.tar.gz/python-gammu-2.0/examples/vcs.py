#!/usr/bin/env python

# Example for reading data from phone and convering it to and from
# vCard, vTodo, vCalendar

from __future__ import print_function
import gammu
import sys


def main():
    state_machine = gammu.StateMachine()
    if len(sys.argv) == 2:
        state_machine.ReadConfig(Filename=sys.argv[1])
    else:
        state_machine.ReadConfig()
    state_machine.Init()

    # For calendar entry

    # Read entry from phone
    entry = state_machine.GetNextCalendar(Start=True)

    # Convert it to vCard
    vc_entry = gammu.EncodeVCALENDAR(entry)
    ic_entry = gammu.EncodeICALENDAR(entry)

    # Convert it back to entry
    print(gammu.DecodeVCS(vc_entry))
    print(gammu.DecodeICS(ic_entry))

    # For todo entry

    # Read entry from phone
    entry = state_machine.GetNextToDo(Start=True)

    # Convert it to vCard
    vt_entry = gammu.EncodeVTODO(entry)
    it_entry = gammu.EncodeITODO(entry)

    # Convert it back to entry
    print(gammu.DecodeVCS(vt_entry))
    print(gammu.DecodeICS(it_entry))

    # For memory entry

    # Read entry from phone
    entry = state_machine.GetNextMemory(Start=True, Type='ME')

    # Convert it to vCard
    vc_entry = gammu.EncodeVCARD(entry)

    # Convert it back to entry
    print(gammu.DecodeVCARD(vc_entry))


if __name__ == '__main__':
    main()
