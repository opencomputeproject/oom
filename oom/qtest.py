# /////////////////////////////////////////////////////////////////////
#
#  keytest.py : Automatically detects all available keys (on port 0),
#  decodes the value for each key.  For raw byte keys, reports their
#  hex values.  Finally, detects avaliable 'functions' (bundles of keys)
#  and reports their values.
#
#  Copyright 2015  Finisar Inc.
#
#  Author: Don Bollinger don@thebollingers.org
#
# ////////////////////////////////////////////////////////////////////

from oom import *                   # the published OOM Northbound API
from oomlib import getmm, getfm     # oom internals to get the key lists
from decode import hexstr           # helper function from the decode pack


# open port 5
port = oom_get_port(5)
print_block_hex(oom_get_memoryraw(port, 0xA0, 0, 0, 128))

# get the internal list of keys and decoders for this type of module
# report their values for this port
keymap = getmm(port.port_type)
for keyx in sorted(keymap.keys()):
    if len(keymap[keyx]) == 5:
        print keyx + ': ' + str(oom_get_keyvalue(port, keyx))
print
print 'byte string keys, in hex:'
print
bytekeys = ('L_TX_RX_LOS',
            'L_RX1_RX2_POWER',
            'L_RX3_RX4_POWER',
            'L_TX1_TX2_BIAS',
            'L_TX3_TX4_BIAS',
            'VENDOR_SPECIFIC_19',
            'VENDOR_SPECIFIC_30',
            'VENDOR_SPECIFIC_66',
            'RX_RATE_SELECT',
            'TX_RATE_SELECT',
            )

for keyx in bytekeys:
    val = oom_get_keyvalue(port, keyx)
    print keyx + ': ' + hexstr(val)

"""

# similarly, get the function keys for this module type,
# report their values for this port
print ' '
print 'functions, with their keys and values:'
print ' '
fnkeys = getfm(port.port_type)
for keyx in fnkeys:
    val = oom_get_memory(port, keyx)
    print keyx + ': '
    print str(val)
    print
"""
