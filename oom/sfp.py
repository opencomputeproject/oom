# sfp.py
# sfp memory map
# based on SFF-8472, ver 12.2 and SFF-8024
# Table 4-1, page 14 and table 4-2, page 15
# Note that values that range from 0-n are returned as integers (get_int)
# Keys encoded as multi-byte fields are returned as raw bytes (get_bytes)
# Keys encoded as bit fields of 8 bits or less are integers (get_bits)
#     with the bit field in the low order bits
#
# Key attributes are:
#   Dynamic: 0 if not dynamic, 1 if it is (don't cache dynamic keys)
#   Decoder: name of the decoder function (these are in decode.py)
#   Addr: i2c address (usually 0xA0 or 0xA2)
#   Page: page the data lives in
#   Offset: byte address where the data starts
#       Note: if offset < 128, then the page value is not used
#       Offsets from 0-127 are in the low memory of Addr
#   Length: number of bytes of data for this key
#   Bit Offset: (optional), highest order bit, within a byte, of a bit field
#   Bit Length: (optional), number of bits in a bit field
#       Note: Bit offset and bit length are only used by get_bits
#       LSB is bit 0, MSB is bit 7


MM = {             # dynamic?, decoder, addr, page, offset,length, BO, BL
     'IDENTIFIER':       (0, 'get_int', 0xA0, 0, 0, 1),
     'EXT_IDENTIFIER':   (0, 'get_int', 0xA0, 0, 1, 1),
     'CONNECTOR':        (0, 'get_int', 0xA0, 0, 2, 1),
     'TRANSCEIVER':      (0, 'get_bytes', 0xA0, 0, 3, 8),       # see table 5-3
     'ENCODING':         (0, 'get_int', 0xA0, 0, 11, 1),
     'BR_NOMINAL':       (0, 'get_bitrate', 0xA0, 0, 12, 55),  # bytes 12 & 66!
     'RATE_IDENTIFIER':  (0, 'get_int', 0xA0, 0, 13, 1),

     'LENGTH_SMF_KM':    (0, 'get_length_km', 0xA0, 0, 14, 1),
     'LENGTH_SMF':       (0, 'get_length_100m', 0xA0, 0, 15, 1),
     'LENGTH_50UM':      (0, 'get_length_10m', 0xA0, 0, 16, 1),
     'LENGTH_62_5UM':    (0, 'get_length_10m', 0xA0, 0, 17, 1),
     'LENGTH_OM4_OR_CU': (0, 'get_length_omcu', 0xA0, 0, 8, 11),  # bytes 8&18
     'LENGTH_OM3':       (0, 'get_length_10m', 0xA0, 0, 19, 1),

     'VENDOR_NAME':      (0, 'get_string', 0xA0, 0, 20, 16),
     'TRANSCEIVER_EXT':  (0, 'get_int', 0xA0, 0, 36, 1),      # 8024, table 4-4
     'VENDOR_OUI':       (0, 'get_bytes', 0xA0, 0, 37, 3),
     'VENDOR_PN':        (0, 'get_string', 0xA0, 0, 40, 16),
     'VENDOR_REV':       (0, 'get_string', 0xA0, 0, 56, 4),
     'WAVELENGTH':       (0, 'get_wavelength', 0xA0, 0, 8, 54),  # 1 field,
     'CABLE_SPEC':       (0, 'get_cablespec', 0xA0, 0, 8, 54),   # 2 keys

     'OPTIONS':          (0, 'get_bytes', 0xA0, 0, 64, 2),
     'BR_MAX':           (0, 'get_brmax', 0xA0, 0, 12, 56),  # bytes 12, 66, 67
     'BR_MIN':           (0, 'get_brmin', 0xA0, 0, 12, 56),  # bytes 12, 66, 67
     'VENDOR_SN':        (0, 'get_string', 0xA0, 0, 68, 16),
     'DATE_CODE':        (0, 'get_string', 0xA0, 0, 84, 8),
     'DIAGNOSTIC_MONITORING_TYPE': (0, 'get_int', 0xA0, 0, 92, 1),
     'ENHANCED_OPTIONS': (0, 'get_int', 0xA0, 0, 93, 1),
     'SFF_8472_COMPLIANCE': (0, 'get_int', 0xA0, 0, 94, 1),
     'VENDOR_SPECIFIC_96': (0, 'get_bytes', 0xA0, 0, 96, 32),

     'TEMPERATURE':      (1, 'get_temperature', 0xA2, 0, 96, 2),
     'VCC':              (1, 'get_voltage', 0xA2, 0, 98, 2),
     'TX_BIAS':          (1, 'get_current', 0xA2, 0, 100, 2),
     'TX_POWER':         (1, 'get_power', 0xA2, 0, 102, 2),
     'RX_POWER':         (1, 'get_power', 0xA2, 0, 104, 2),
     'OPT_LASER_TEMP':   (1, 'get_temperature', 0xA2, 0, 106, 2),
     'OPT_TEC':          (1, 'get_signed_current', 0xA2, 0, 108, 2),

     'STATUS_CONTROL':         (1, 'get_bits', 0xA2, 0, 110, 1, 7, 8),
     'TX_DISABLE_STATE':       (1, 'get_bits', 0xA2, 0, 110, 1, 7, 1),
     'SOFT_TX_DISABLE_SELECT': (1, 'get_bits', 0xA2, 0, 110, 1, 6, 1),
     'RS_1_STATE':             (1, 'get_bits', 0xA2, 0, 110, 1, 5, 1),
     'RATE_SELECT_STATE':      (1, 'get_bits', 0xA2, 0, 110, 1, 4, 1),
     'SOFT_RATE_SELECT':       (1, 'get_bits', 0xA2, 0, 110, 1, 3, 1),
     'TX_FAULT_STATE':         (1, 'get_bits', 0xA2, 0, 110, 1, 2, 1),
     'RX_LOS_STATE':           (1, 'get_bits', 0xA2, 0, 110, 1, 1, 1),
     'DATA_READY_BAR_STATE':   (1, 'get_bits', 0xA2, 0, 110, 1, 0, 1),
    }

FM = {
    'SERIAL_ID': ('IDENTIFIER',
                  'EXT_IDENTIFIER',
                  'CONNECTOR',
                  'TRANSCEIVER',
                  'ENCODING',
                  'BR_NOMINAL',
                  'RATE_IDENTIFIER',
                  'LENGTH_SMF_KM',
                  'LENGTH_SMF',
                  'LENGTH_50UM',
                  'LENGTH_62_5UM',
                  'LENGTH_OM4_OR_CU',
                  'LENGTH_OM3',
                  'VENDOR_NAME',
                  'TRANSCEIVER_EXT',
                  'VENDOR_OUI',
                  'VENDOR_PN',
                  'VENDOR_REV',
                  'WAVELENGTH',
                  'CABLE_SPEC',
                  'OPTIONS',
                  'BR_MAX',
                  'BR_MIN',
                  'VENDOR_SN',
                  'DATE_CODE',
                  'DIAGNOSTIC_MONITORING_TYPE',
                  'ENHANCED_OPTIONS',
                  'SFF_8472_COMPLIANCE'
                  ),

    'DOM': ('TEMPERATURE', 'VCC', 'TX_BIAS', 'TX_POWER',
            'RX_POWER'),
    }


WMAP = {
         'SOFT_TX_DISABLE_SELECT': 'set_bits',
       }
