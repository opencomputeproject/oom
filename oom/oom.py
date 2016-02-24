# /////////////////////////////////////////////////////////////////////
#
#  oom.py : Provides the Northbound API, hides the implementation in
#  oomlib.py decode.py and the module type definitions
#
#  Copyright 2015  Finisar Inc.
#
#  Author: Don Bollinger don@thebollingers.org
#
# ////////////////////////////////////////////////////////////////////

import oomlib
from oomlib import print_block_hex
from decode import get_string


#
# helper routine, provides a port without requiring the user to
# define the complicated port_t struct
#
def oom_get_port(n):
    port = oomlib.oom_get_port(n)
    return (port)


#
# get the full list of ports, allocates the
# memory, defines the data types
#
def oom_get_portlist():
    port_list = oomlib.oom_get_portlist()
    return(port_list)


#
# magic decoder - gets any attribute based on its key
# if there is no decoder for the port type, or the key is not
# listed in the memory map for that port type, then returns None
# NOTE: the type of the value returned depends on the key.
# Use 'str(oom_get_keyvalue(port, key))' to get a readable string
# for all return types
#
def oom_get_keyvalue(port, key):
    return oomlib.oom_get_keyvalue(port, key)


#
# Set a key to chosen value (write value to EEPROM)
# Be careful with this, this is likely to change the function
# of your module
#
def oom_set_keyvalue(port, key, value):
    return oomlib.oom_set_keyvalue(port, key, value)


#
# given a 'function', return a dictionary with the values of all the
# keys in that function, on the specified port
#
def oom_get_memory(port, function):
    return oomlib.oom_get_memory(port, function)


#
# TODO - throw an exception if len != length
#
def oom_get_memory_sff(port, address, page, offset, length):
    return oomlib.oom_get_memory_sff(port, address, page, offset, length)


def oom_set_memory_sff(port, address, page, offset, length, data):
    return oomlib.oom_set_memory_sff(port, address, page, offset, length, data)
