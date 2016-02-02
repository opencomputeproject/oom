# /////////////////////////////////////////////////////////////////////
#
#  oomdemo.py : Exercises OOM Northbound API
#
#  Copyright 2015  Finisar Inc.
#
#  Author: Don Bollinger don@thebollingers.org
#
# ////////////////////////////////////////////////////////////////////

from oom import *
from ctypes import *

# get the list of available ports (port_list is a list of port structures)
port_list = oom_get_portlist()

# Demo the raw memory access API
print 'Port 0, address A2h, page 0, offset 0, 128 bytes:'
print_block_hex(oom_get_memoryraw(port_list[0], 0xA2, 0, 0, 128))

# demo the get_keyvalue() API
print "VENDOR_SN: " + oom_get_keyvalue(port_list[0], "VENDOR_SN")
print "XYZ: " + oom_get_keyvalue(port_list[0], "XYZ")
print "IDENTIFIER: " + str(oom_get_keyvalue(port_list[0], "IDENTIFIER"))

# demo the oom_get_memory() API...  DOM shows the values for 5 keys
print "DOM: " + str(oom_get_memory(port_list[0], "DOM"))

# demo the oom_getport() API, by getting port 2.  Note that the keys
# have different values on this different port
portnum = 2
print "Port " + str(portnum)
port = oom_get_port(portnum)
print "VENDOR_SN: " + str(oom_get_keyvalue(port, "VENDOR_SN"))
print "DOM: " + str(oom_get_memory(port, "DOM"))

# demo the raw write API
# SFP address A2h, page 0, offset 128-247 are user writable, scribble there
print '*******************'
content = oom_get_memoryraw(port, 0xA2, 0, 128, 16)
print 'oom_set_memoryraw demo'
print '0xA2, page 0, offset 128, 16 bytes, initial content:'
print_block_hex(content)
content = '16 changed bytes'
length = oom_set_memoryraw(port, 0xA2, 0, 128, 16, content)
content = oom_get_memoryraw(port, 0xA2, 0, 128, 16)
print '0xA2, page 0, offset 128, 16 bytes, changed content:'
print get_string(content)
print '*******************'
