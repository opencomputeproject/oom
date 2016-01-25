# /////////////////////////////////////////////////////////////////////
#
#  oomlib.py : Implements OOM Northbound API, calls decode routines
#  to decode raw data from the Southbound API
#
#  Copyright 2015  Finisar Inc.
#
#  Authors: Yuan Yu yuan.yu@finisar.com
#           Don Bollinger don@thebollingers.org
#
# ////////////////////////////////////////////////////////////////////

import sfp
import qsfp
import decode

import glob
import os
import struct
import time
from ctypes import *
from array import *
import importlib

#
# link in the southbound shim
# note this means the southbound shim MUST be installed in
# this location (relative to this module, in lib, named oom_south.so)
#
oomsouth = cdll.LoadLibrary("./lib/oom_south.so")


#
# This class recreates the port structure in the southbound API
#
class port_t(Structure):
    _fields_ = [("port_num", c_int),
                ("port_type", c_int),
                ("seq_num", c_int),
                ("port_flag", c_int)]


# helper routine, provides a port without requiring the prior
# definition of the complicated port_t struct
def oom_getport(portnum):
    numports = oomsouth.oom_maxports()
    port_array = port_t * numports
    port_list = port_array()
    portlist_num = oomsouth.oom_get_portlist(port_list)
    return port_list[portnum]


#
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
# TODO:  Kludge here, want a way to map type to a memmap, on demand
# like if (mmbytpe[type] == []: mmbytpe[type] = "type".MM
# current implementation ties SFP and QSFP to the numbers '0' and '1'
# Kludgy
#
mmbytype = [[]*2]


def getmm(type):
    if type == port_type_e['SFP']:
        if mmbytype[0] == []:
            mmbytype[0] = sfp.MM
        return(mmbytype[0])
    if type == port_type_e['QSFP']:
        if mmbytype[1] == []:
            mmbytype[1] = qsfp.MM
        return(mmbytype[1])
    return []


#
# get the mapping, which functions include which keys
#
fmbytype = [[]*2]


def getfm(type):
    if type == port_type_e['SFP']:
        if fmbytype[0] == []:
            fmbytype[0] = sfp.FM
        return(fmbytype[0])
    if type == port_type_e['QSFP']:
        if fmbytype[1] == []:
            fmbytype[1] = qsfp.fM
        return(fmbytype[1])
    return []


# one time setup, get the names of the decoders in the decode library
decodelib = importlib.import_module('decode')


#
# magic decoder - gets any attribute based on its key attribute
# if there is no decoder for the port type, or the key is not
# listed in the memory map for that port type, then returns ''
# NOTE: the type of the value returned depends on the key.
# Use 'str(oom_get_keyvalue(port, key))' to get a readable string
# for all return types
#
def oom_get_keyvalue(port, key):
    mm = getmm(port.port_type)            # get the memory map for this type
    if key not in mm:
        return ''
    par = (port,) + mm[key][1:]           # get the parameters
    raw_data = oom_get_memoryraw(*par)    # get the data
    decoder = getattr(decodelib, mm[key][0])  # get the decoder
    temp = decoder(raw_data)              # get the value
    return temp                           # and return it


#
# TODO - throw an exception if len != length
#
def oom_get_memoryraw(port, address, page, offset, length):

    data = create_string_buffer(length)   # allocate space
    len = oomsouth.oom_get_memoryraw(byref(port), address,
                                     page, offset, length, data)

    return data


#
# given a 'function', return a dictionary with the values of all the
# keys in that function, on the specified port
#
def oom_get_memory(port, function):

    funcmap = getfm(port.port_type)
    retval = {}
    for keys in funcmap[function]:
        retval[keys] = oom_get_keyvalue(port, keys)
    return retval
