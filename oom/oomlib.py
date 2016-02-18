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

import struct
from ctypes import *
import importlib
import glob
import sys


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

# Southbound API will report the 'class' of a module, basically
# whether it uses i2c addresses, pages, and bytes (SFF) or
# it uses mdio, a flat 16 bit address space, and words (CFP)
port_class_e = {
    'UNKNOWN': 0x00,
    'SFF': 0x01,
    'CFP': 0x02
    }

#
# link in the southbound shim
# note this means the southbound shim MUST be installed in
# this location (relative to this module, in lib, named oom_south.so)
#
oomsouth = cdll.LoadLibrary("./lib/oom_south.so")

# one time setup, get the names of the decoders in the decode library
decodelib = importlib.import_module('decode')

# and find any addons that should be incorporated
addon_fns = []
sys.path.insert(0, './addons')   # required, to get them imported

# build a list of modules in the addons directory
modulist = []
modnamelist = glob.glob('./addons/*.py')
for name in modnamelist:
    name = name.split('/')[2]
    name = name[0:len(name)-3]
    modulist.append(name)
modnamelist = glob.glob('./addons/*.pyc')  # obfuscated modules!
for name in modnamelist:
    name = name.split('/')[2]
    name = name[0:len(name)-4]
    modulist.append(name)
modulist = list(set(modulist))  # eliminate dups, eg: x.py and x.pyc

for module in modulist:
    try:
        addlib = importlib.import_module(module)
    except:
        # skip that one (it is not a module?)
        pass
    else:
        try:
            addon_fns.append(getattr(addlib, 'add_features'))
        except:
            # skip that one ('add_features' is not there?)
            pass
sys.path = sys.path[1:]  # put the search path back


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
class Port:
    def __init__(self, cport):
        self.c_port = cport

        # copy the C character array into a more manageable python string
        self.port_name = ''
        for i in range(32):
            self.port_name += chr(cport.name[i])
        self.port_type = get_port_type(self)

        # initialize the key maps, potentially unique for each port
        typename = type_to_str(self.port_type).lower()
        try:
            # here is where the type is tied to the keymap file
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
    portlist = [Port(cport) for cport in cport_list]
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


# debug helper function, print raw data, in hex
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


# helper routine to return module type as string (reverse port_type_e)
def type_to_str(modtype):
    for tname, mtype in port_type_e.iteritems():
        if mtype == modtype:
            return tname
    return ''
