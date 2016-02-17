# /////////////////////////////////////////////////////////////////////
#
#  oomlib.py : Implements OOM decoding, all the routines that are not
#  visible in the Northbound API, calls decode routines
#  to decode raw data from the Southbound API
#  Also hides the messy data structures and allocates the memory
#  for the messy data
#
#  Copyright 2015  Finisar Inc.
#
#  Author: Don Bollinger don@thebollingers.org
#
# ////////////////////////////////////////////////////////////////////

import sfp
import qsfp_plus
import decode

import struct
from ctypes import *
import importlib
import glob
import sys

#
# link in the southbound shim
# note this means the southbound shim MUST be installed in
# this location (relative to this module, in lib, named oom_south.so)
#
oomsouth = cdll.LoadLibrary("./lib/oom_south.so")

# one time setup, get the names of the decoders in the decode library
decodelib = importlib.import_module('decode')

# and find any addons that should be incorporated
modulist = glob.glob('./addons/*.py')
addon_fns = []
sys.path.insert(0,'./addons')   # required, to get them imported
for i in range(len(modulist)):
    modulist[i] = modulist[i].split('/')[2]
    modulist[i] = modulist[i][0:len(modulist[i])-3]
    try:
        addlib = importlib.import_module(modulist[i])
    except ImportError:
        # skip that one (it is not a module?)
        pass
    else:
        try:
            addon_fns.append(getattr(addlib, 'add_features'))
        except:
            # skip that one ('add_features' is not there?)
            pass
sys.path = sys.path[1:]  # put the search path back

port_class_e = {
    'UNKNOWN': 0x00,
    'SFF': 0x01,
    'CFP': 0x02
    }


#
# This class recreates the port structure in the southbound API
#
class c_port_t(Structure):
    _fields_ = [("handle", c_void_p),
                ("oom_class", c_int),
                ("name", c_ubyte * 32)]


# This class is the python port, which includes the C definition
# of a port, plus other useful things, including the port type,
# and the keymap for that port.
class port:
    def __init__(self):
        self.ptype = 3   # hack, make this an SFP port for now

    # c_port is the c_port_t data structure returned
    # by the southbound API
    def add_c_port(self, c_port):
        self.c_port = c_port
        self.port_name = ''
        for i in range(32):
            self.port_name += chr(c_port.name[i])

    def add_port_type(self, port_type):
        self.port_type = port_type

        # initialize the key maps, potentially unique for each port
        for tname, ptype in port_type_e.iteritems():
            if ptype == port_type:
                typename = tname.lower()
        try:
            maps = importlib.import_module(typename, package=None)
            self.mmap = maps.MM
            self.fmap = maps.FM
            self.wmap = maps.WMAP
        except ImportError:
            self.mmap = {}
            self.fmap = {}
            self.wmap = {}
        for func in addon_fns:  # call all the addons to extend this port
            func(self)


#
# oom_get_port(n): helper routine, provides a port without requiring the prior
# definition of the complicated port_t struct
# returns port 'n' of the list of ports returned by the shim
# note, sketchy way to define a port
#
def oom_get_port(n):
    portlist = oom_get_portlist()
    return(portlist[n])


#
# similarly, provide the port list without requiring the definition
# of the port_t structure.  Allocate the memory here.
#
def oom_get_portlist():
    numports = oomsouth.oom_get_portlist(0, 0)
    cport_array = c_port_t * numports
    cport_list = cport_array()
    retval = oomsouth.oom_get_portlist(cport_list, numports)
    portcount = 0
    portlist = [port() for cport in cport_list]
    for cport in cport_list:
        portlist[portcount].add_c_port(cport)
        ptype = get_port_type(portlist[portcount])
        portlist[portcount].add_port_type(ptype)
        portcount += 1
    return portlist


#
# figure out the type of a port
#
def get_port_type(port):
    if port.c_port.oom_class == port_class_e['SFF']:
        data = oom_get_memory_sff(port, 0xA0, 0, 0, 1)
        ptype = ord(data[0])
        return(ptype)
    # TODO: get type for CFP modules, requires oom_get_memory_cfp()
    ptype = port_type_e['UNKNOWN']
    return (ptype)


#
# Allocate the memory for raw reads, return the data cleanly
#
def oom_get_memory_sff(port, address, page, offset, length):
    data = create_string_buffer(length)   # allocate space
    retlen = oomsouth.oom_get_memory_sff(byref(port.c_port), address,
                                         page, offset, length, data)
    return data


#
# Raw write
#
def oom_set_memory_sff(port, address, page, offset, length, data):
    # data = create_string_buffer(length)   # allocate space
    retlen = oomsouth.oom_set_memory_sff(byref(port.c_port), address,
                                         page, offset, length, data)
    return retlen


# set the chosen key to the specified value
def oom_set_keyvalue(port, key, value):
    mm = port.mmap
    wm = port.wmap
    if key not in mm:
        return -1
    if key not in wm:
        return -1
    par = (port,) + mm[key][1:]     # get the read parameters
    raw_data = oom_get_memory_sff(*par)    # get the current data
    encoder = getattr(decodelib, wm[key])  # find the encoder
    temp = encoder(raw_data, value)  # stuff value into raw_data if necessary
    # wpar = (par,) + temp
    # retval = oom_set_memory_sff(*wpar)    # and write it back!
    retval = oom_set_memory_sff(port, mm[key][1], mm[key][2], mm[key][3],
                                mm[key][4], temp)
    return retval


#
# Mapping of port_type numbers to user accessible names
# This is a copy of a matching table in oom_south.h
# Might be a problem keeping these in sync, but
# these mappings are based on the relevant standards,
# so they should be fairly stable
#
port_type_e = {
    'UNKNOWN': 0x00,
    'GBIC': 0x01,
    'SOLDERED': 0x02,
    'SFP': 0x03,
    'XBI': 0x04,
    'XENPAK': 0x05,
    'XFP': 0x06,
    'XFF': 0x07,
    'XFP_E': 0x08,
    'XPAK': 0x09,
    'X2': 0x0A,
    'DWDM_SFP': 0x0B,
    'QSFP': 0x0C,
    'QSFP_PLUS': 0x0D,
    'CXP': 0x0E,
    'SMM_HD_4X': 0x0F,
    'SMM_HD_8X': 0x10,
    'QSFP28': 0x11,
    'CXP2': 0x12,
    'CDFP': 0x13,
    'SMM_HD_4X_FANOUT': 0x14,
    'SMM_HD_8X_FANOUT': 0x15,
    'CDFP_STYLE_3': 0x16,
    'MICRO_QSFP': 0x17,

    #  next values are CFP types. Note that their spec
    #  (CFP MSA Management Interface Specification ver 2.4 r06b page 67)
    #  values overlap with the values for i2c type devices.  OOM has
    #  chosen to add 256 (0x100) to the values to make them unique

    'CFP': 0x10E,
    '168_PIN_5X7': 0x110,
    'CFP2': 0x111,
    'CFP4': 0x112,
    '168_PIN_4X5': 0x113,
    'CFP2_ACO': 0x114,

    #  special values to indicate that no module is in this port,
    #  as well as invalid type

    'INVALID': -1,
    'NOT_PRESENT': -2,
    }


# helper function, print raw data, in hex
def print_block_hex(data):
    dataptr = 0
    bytesleft = len(data)
    lines = (bytesleft + 15) / 16
    for i in range(lines):
        outstr = "       "
        blocks = (bytesleft + 3) / 4
        if blocks > 4:
            blocks = 4
        for j in range(blocks):
            nbytes = bytesleft
            if nbytes > 4:
                nbytes = 4
            for k in range(nbytes):
                temp = ord(data[dataptr])
                foo = hex(temp)
                if temp < 16:
                    outstr += '0'
                outstr += foo[2:4]
                dataptr += 1
                bytesleft -= 1
            outstr += ' '
        print outstr


# set or clear a bit, for writing one bit back to EEPROM
def set_bit(value, bit):
    return (value | (1 << bit))


def clear_bit(value, bit):
    return (value & ~(1 << bit))
