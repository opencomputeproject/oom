
# demosetup.py
# sets up oom (numports, get_portlist)
# returns a pointer to port <n>
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


def getport(portnum):

    oomlib = cdll.LoadLibrary("./lib/oom_south.so")

    class port_t(Structure):
        _fields_ = [("port_num", c_int),
                    ("port_type", c_int),
                    ("seq_num", c_int),
                    ("port_flag", c_int)]

    numports = oomlib.oom_maxports()
    port_array = port_t * numports
    port_list = port_array()
    portlist_num = oomlib.oom_get_portlist(port_list)
    return port_list[portnum]
