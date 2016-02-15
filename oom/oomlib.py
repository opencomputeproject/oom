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

#
# link in the southbound shim
# note this means the southbound shim MUST be installed in
# this location (relative to this module, in lib, named oom_south.so)
#
oomsouth = cdll.LoadLibrary("./lib/oom_south.so")

# one time setup, get the names of the decoders in the decode library
decodelib = importlib.import_module('decode')


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

    def add_c_port(self, c_port):
        self.c_port = c_port
        self.port_name = ''
        for i in range(32):
            self.port_name += chr(c_port.name[i])

    def add_port_type(self, port_type):
        self.port_type = port_type


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
    wmap = getwmap(port.port_type)  # need encoders
    mm = getmm(port.port_type)      # reuse read parameters for writes
    if key not in wmap:
        return -1
    if key not in mm:
        return -1
    par = (port,) + mm[key][1:]     # get the read parameters
    raw_data = oom_get_memory_sff(*par)    # get the current data
    encoder = getattr(decodelib, wmap[key])  # find the encoder
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


#
# Get the mapping, for each key, what is it's decoder, and where
# in the EEPROM (address, page, offset, len) is the data
# TODO:  Kludge here, want a way to map type to a memmap, on demand
# like if (mmbytpe[type] == []: mmbytpe[type] = "type".MM
# current implementation ties SFP and QSFP to the numbers '0' and '1'
# Kludgy
#
# mmbytype = [[]*2]
mmbytype = [sfp.MM, qsfp_plus.MM]


def getmm(type):
    if type == port_type_e['SFP']:
        if mmbytype[0] == []:
            mmbytype[0] = sfp.MM
        return(mmbytype[0])
    if type == port_type_e['QSFP_PLUS']:
        if mmbytype[1] == []:
            mmbytype[1] = qsfp_plus.MM
        return(mmbytype[1])
    return []


#
# get the mapping, which functions include which keys
#
fmbytype = [sfp.FM, qsfp_plus.FM]


def getfm(type):
    if type == port_type_e['SFP']:
        if fmbytype[0] == []:
            fmbytype[0] = sfp.FM
        return(fmbytype[0])
    if type == port_type_e['QSFP_PLUS']:
        if fmbytype[1] == []:
            fmbytype[1] = qsfp_plus.FM
        return(fmbytype[1])
    return []


#
# get the mapping for writable keys, IDs the decoder
#
wmapbytype = [sfp.WMAP, qsfp_plus.WMAP]


def getwmap(type):
    if type == port_type_e['SFP']:
        if wmapbytype[0] == []:
            wmapbytype[0] = sfp.WMAP
        return(wmapbytype[0])
    if type == port_type_e['QSFP_PLUS']:
        if wmapbytype[1] == []:
            wmapbytype[1] = qsfp_plus.WMAP
        return(wmapbytype[1])
    return []


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
