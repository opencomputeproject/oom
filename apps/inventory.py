#! /usr/bin/python
#
# inventory.py
#
# OOM script to inventory the modules in a switch
#
from oom import *
from oom.oomlib import type_to_str

formatstr = '%-10s %-16s %-13s %-16s %-16s'
print
print formatstr % ('Port Name', 'Vendor', 'Type', 'Part #', 'Serial #')
print
for port in oom_get_portlist():
    modtype = type_to_str(port.port_type)
    if modtype == 'UNKNOWN':
        modtype = 'No Module'
    print formatstr % (port.port_name,
                       oom_get_keyvalue(port, 'VENDOR_NAME'),
                       modtype,
                       oom_get_keyvalue(port, 'VENDOR_PN'),
                       oom_get_keyvalue(port, 'VENDOR_SN'))
print
