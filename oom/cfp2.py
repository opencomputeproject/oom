# cfp2.py
# cfp memory map
# Based on CFP MSA Management Interface Specification
# Version 2.6 r04a, October 7, 2016 (See Tables 23-32)
#
# Note that the CFP spec is notably different from the i2c (SFP/QSFP
# devices spec (SFF 8436 and SFF 8472)
#
# Unlike those devices, CFP/MDIO devices are organized as 16 bit words,
# linearly addressed (no i2c addresses, no pages, word - not byte - addressed)
#
# Also, MOST but not all registers actually only use the low order byte
# of each register.  Even for strings, the raw data appears as
# (using a Vendor Name of 'FINISAR CORP.'for example):
#
#  \0F\0I\0N\0I\0S\0A\0R\0 \0C\0O\0R\0P\0.\0
#
# Hence, there is a code to indicate this (and routines in OOM decode)
# to collapse(expand) such a string by removing(adding) all the even
# numbered bytes
#
# Note that values that range from 0-n are returned as integers (get_int)
# Keys encoded as multi-byte fields are returned as raw bytes (get_bytes)
# Keys encoded as bit fields of 8 bits or less are integers (get_bits)
#     with the bit field in the low order bits
#
# Key attributes are:
#   Dynamic: 0 if not dynamic, 1 if it is (OOM doesn't currently cache CFP)
#   Decoder: name of the decoder function (these are in decode.py)
#   Collapse: 0 if 16 bits of the register are used, 1 if only 8 bits
#   Address: WORD address where the data starts (matches the spec)
#   Length: number of WORDS of data for this key
#   Bit Offset: (optional), highest order bit, within a byte, of a bit field
#   Bit Length: (optional), number of bits in a bit field
#       Note: Bit offset and bit length are only used by get_bits and set_bits
#       LSB is bit 0, MSB is bit 15


MM = {             # dynamic?, decoder, collapse, addr, length, BO, BL
     'IDENTIFIER':       (0, 'get_int',         1, 0x8000,  1),
     'VENDOR_NAME':      (0, 'get_string',      1, 0x8021, 16),
     'TEMPERATURE':      (0, 'get_temperature', 0, 0xA02F, 1),
     'SUPPLY_VOLTAGE':   (0, 'get_voltage',     0, 0xA030, 1),


    }

FM = {
    'SERIAL_ID': ('IDENTIFIER',
                  'VENDOR_NAME',
                  ),

    'DOM': ('TEMPERATURE',
            'SUPPLY_VOLTAGE',
            ),
    }


WMAP = {
         'VENDOR_NAME': 'set_string',
       }
