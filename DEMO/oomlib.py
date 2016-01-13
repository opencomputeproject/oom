# oom.py

import sfp
import qsfp
import decode

import glob, os
import struct
import time
from ctypes import * 
from array import *
import importlib

#
# link in the southbound shim
# TODO - pick a standard name for this, so that anyone
# can put their own shim (NOS, switch vendor) in the 
# right place and get called
#
oomsouth = cdll.LoadLibrary("./lib/oom_south.so")

#
# TODO - how does this get exported so users can consume
# it without having to copy it?
#
class port_t(Structure):
    _fields_ = [("port_num", c_int),
                ("port_type", c_int),
                ("seq_num", c_int),
                ("port_flag", c_int)]


#
# This is a copy of a matching table in oom_south.h
# Might be a problem keeping these in sync, but for 
# now, these mappings are based on the relevant standards
#
port_type_e = {
	'UNKNOWN' : 0x00,
	'GBIC' : 0x01,
	'SOLDERED' : 0x02,
	'SFP' : 0x03,
	'XBI' : 0x04,
	'XENPAK' : 0x05,
	'XFP' : 0x06,
	'XFF' : 0x07,
	'XFP_E' : 0x08,
	'XPAK' : 0x09,
	'X2' : 0x0A,
	'DWDM_SFP' : 0x0B,
	'QSFP' : 0x0C,
	'QSFP_PLUS' : 0x0D,
	'CXP' : 0x0E,
	'SMM_HD_4X' : 0x0F,
	'SMM_HD_8X' : 0x10,
	'QSFP28' : 0x11,
	'CXP2' : 0x12,
	'CDFP' : 0x13,
	'SMM_HD_4X_FANOUT' : 0x14,
	'SMM_HD_8X_FANOUT' : 0x15,
	'CDFP_STYLE_3' : 0x16,
	'MICRO_QSFP' : 0x17,

#  next values are CFP types. Note that their spec 
#  (CFP MSA Management Interface Specification ver 2.4 r06b page 67) 
#  values overlap with the values for i2c type devices.  OOM has 
#  chosen to add 256 (0x100) to the values to make them unique

	'CFP' : 0x10E,
	'168_PIN_5X7' : 0x110,
	'CFP2' : 0x111,
	'CFP4' : 0x112,
	'168_PIN_4X5' : 0x113,
	'CFP2_ACO' : 0x114,

#  special values to indicate that no module is in this port, 
#  as well as invalid type 

	'INVALID' : -1,
	'NOT_PRESENT' : -2,
    }

#
# TODO:  Kludge here, want a way to map type to a memmap, on demand
# like if (mmbytpe[type] == []: mmbytpe[type] = "type".MM
# current implementation ties SFP and QSFP to the numbers '0' and '1'
# Kludgy
#
mmbytype = [[]*2]
def getmm(type) :
    if type == port_type_e['SFP']:
        if mmbytype[0] == [] : mmbytype[0] = sfp.MM
        return(mmbytype[0])
    if type == port_type_e['QSFP']:
        if mmbytype[1] == [] : mmbytype[1] = qsfp.MM
        return(mmbytype[1])
    return []


# one time setup, get the names of the decoders in the decode library
decodelib = importlib.import_module('decode')

#
# magic decoder - gets any attribute based on its key attributes
#
def oom_get_keyvalue(port, key):
    mm = getmm(port.port_type)            # get the memory map for this type
    if key not in mm :
        tempstr = "no such key: " + key
        return{"OOM_ERROR": tempstr}
    if mm == []: 
        tempstr = "no decoder for for port type " + str(port.port_type)
        return {"OOM_ERROR": tempstr}
    par = (port,) + mm[key][1:]           # get the parameters
    raw_data = oom_get_memoryraw(*par)    #get the data
    decoder = getattr(decodelib, mm[key][0])  # get the decoder
    temp = decoder(raw_data);             # get the value
    retval = {key : temp}                 # make a key/value pair
    return retval                         # and return it


#
# TODO - should the southbound API be changed to return 'data'?
#
def oom_get_memoryraw(port, address, page, offset, length):

    port_ptr = pointer(port)

    data = '0'*256
    result = ''
    len = oomsouth.oom_get_memoryraw(port_ptr, address, page, offset, length, data)

#
# TODO - this bit of code makes everything in the decode layer operate on
# hex characters, 2 hex chars per byte, rather than raw data.  
# Is this really what we want?
#
    for i in range(len):
        result += data[i].encode("hex")
    
    return result


def oom_get_memory(port, function):
 
    if function.upper() == "VENDOR_SN":
        return oom_get_keyvalue(port, 'VENDOR_SN')

    elif function.upper() == "IDENTIFIER":
        return oom_get_keyvalue(port, 'IDENTIFIER')

    elif function.upper() == 'DOM':
        return [
            oom_get_keyvalue(port, 'TEMPERATURE'),
            oom_get_keyvalue(port, 'VCC'),
            oom_get_keyvalue(port, 'TX_BIAS'),
            oom_get_keyvalue(port, 'TX_POWER'),
            oom_get_keyvalue(port, 'RX_POWER')
            ]

    elif function == "FAWS":
        print "FAWS"
        return
