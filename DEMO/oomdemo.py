# oomdemo.py
# driver to exercise OOM northbound API (decode layer)
# initially only exercises the raw interfaces (the southbound API)
#

import sfp
import qsfp
import decode
import oomlib

import glob, os
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

print oomlib.oom_get_memoryraw(port_list[0], 0xA2, 3, 128, 128)
print oomlib.oom_get_keyvalue(port_list[0], "VENDOR_SN")
print oomlib.oom_get_keyvalue(port_list[0], "XYZ")
print oomlib.oom_get_keyvalue(port_list[0], "IDENTIFIER")
print oomlib.oom_get_memory(port_list[0], "DOM")

# Manual demo:
#
# import demosetup
# import oomlib
# port = demosetup.getport(0)
# print oomlib.oom_getkeyvalue(port, "IDENTIFIER")
# print oomlib.oom_get_memory(port, "DOM")
# try any other legal keys
# change ports
# port2 = demosetup.getport(2)
# print oomlib.oom_get_memory(port2, "DOM")
