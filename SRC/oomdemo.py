# /////////////////////////////////////////////////////////////////////
#
#  oomdemo.py : Exercises OOM Northbound API
#
#  Copyright 2015  Finisar Inc.
#
#  Author: Don Bollinger don@thebollingers.org
#
# ////////////////////////////////////////////////////////////////////

# oomdemo.py
# driver to exercise OOM northbound API (decode layer)
# initially only exercises the raw interfaces (the southbound API)
#

import sfp
import qsfp
import decode
import oomlib

import glob
import os
import struct
import time
from ctypes import *
from array import *


# OOM setup requirements to call raw interfaces...
# open the southbound (C) library, define a port struct...
# get the number of ports, in order to size the port array...
# get the port list
oomsouth = cdll.LoadLibrary("./lib/oom_south.so")


class port_t(Structure):
    _fields_ = [("port_num", c_int),
                ("port_type", c_int),
                ("seq_num", c_int),
                ("port_flag", c_int)]

numports = oomsouth.oom_maxports()
port_array = port_t * numports
port_list = port_array()
portlist_num = oomsouth.oom_get_portlist(port_list)

print 'Port 0, address A2h, page 0, offset 0, 128 bytes:'
oomsouth.print_block_hex(
        oomlib.oom_get_memoryraw(port_list[0], 0xA2, 0, 0, 128))
print "VENDOR_SN: " + oomlib.oom_get_keyvalue(port_list[0], "VENDOR_SN")
print "XYZ: " + oomlib.oom_get_keyvalue(port_list[0], "XYZ")
print "IDENTIFIER: " + oomlib.oom_get_keyvalue(port_list[0], "IDENTIFIER")
print "DOM: " + str(oomlib.oom_get_memory(port_list[0], "DOM"))

# demo the presence of oom_getport
portnum = 2
print "Port " + str(portnum)
port = oomlib.oom_getport(portnum)
print "TX_POWER: " + str(oomlib.oom_get_keyvalue(port, "TX_POWER"))
print "X_POWER: " + str(oomlib.oom_get_memory(port, "X_POWER"))

# Manual demo:
#
# import oomlib
# port = oomlib.getport(0)
# print oomlib.oom_getkeyvalue(port, "IDENTIFIER")
# print oomlib.oom_get_memory(port, "DOM")
# try any other legal keys
# change ports
# port2 = oomlib.getport(2)
# print oomlib.oom_get_memory(port2, "DOM")
