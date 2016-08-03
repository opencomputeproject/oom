# /////////////////////////////////////////////////////////////////////
#
#  oomtypes.py : Common type definitions used by multiple OOM modules
#
#  Copyright 2015  Finisar Inc.
#
#  Author: Don Bollinger don@thebollingers.org
#
# ////////////////////////////////////////////////////////////////////

import struct
from ctypes import *


#
# This class recreates the port structure in the southbound API
#
class c_port_t(Structure):
    _fields_ = [("handle", c_void_p),
                ("oom_class", c_int),
                ("name", c_ubyte * 32)]
