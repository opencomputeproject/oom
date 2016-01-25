# sfp.py
# sfp memory map
# based on SFF-8472, ver 12.2 and SFF-8024
# Table 4-1, page 14 and table 4-2, page 15
# Note that values that range from 0-n are returned as integers (get_int)
# Keys that are encoded as bit fields are returned as raw bytes (get_bytes)


MM = {
     'IDENTIFIER':       ('get_int', 0xA0, 0, 0, 1),
     'EXT_IDENTIFIER':   ('get_int', 0xA0, 0, 1, 1),
     'CONNECTOR':        ('get_int', 0xA0, 0, 2, 1),
     'TRANSCEIVER':      ('get_bytes', 0xA0, 0, 3, 8),       # see table 5-3
     'ENCODING':         ('get_int', 0xA0, 0, 11, 1),
     'BR_NOMINAL':       ('get_bitrate', 0xA0, 0, 12, 55),  # bytes 12 and 66!
     'RATE_IDENTIFIER':  ('get_int', 0xA0, 0, 13, 1),

     'LENGTH_SMF_KM':    ('get_length_km', 0xA0, 0, 14, 1),
     'LENGTH_SMF':       ('get_length_100m', 0xA0, 0, 15, 1),
     'LENGTH_50UM':      ('get_length_10m', 0xA0, 0, 16, 1),
     'LENGTH_62_5UM':   ('get_length_10m', 0xA0, 0, 17, 1),
     'LENGTH_OM4_OR_CU': ('get_length_omcu', 0xA0, 0, 8, 11),  # bytes 8 and 18
     'LENGTH_OM3':       ('get_length_10m', 0xA0, 0, 19, 1),

     'VENDOR_NAME':      ('get_string', 0xA0, 0, 20, 16),
     'TRANSCEIVER_EXT':  ('get_int', 0xA0, 0, 36, 1),       # 8024, table 4-4
     'VENDOR_OUI':       ('get_bytes', 0xA0, 0, 37, 3),
     'VENDOR_PN':        ('get_string', 0xA0, 0, 40, 16),
     'VENDOR_REV':       ('get_string', 0xA0, 0, 56, 4),
     'WAVELENGTH':       ('get_wavelength', 0xA0, 0, 8, 54),  # 1 field, 2 keys
     'CABLE_SPEC':       ('get_cablespec', 0xA0, 0, 8, 54),   # 1 field, 2 keys

     'OPTIONS':          ('get_bytes', 0xA0, 0, 64, 2),
     'BR_MAX':           ('get_brmax', 0xA0, 0, 12, 56),  # bytes 12, 66, 67!
     'BR_MIN':           ('get_brmin', 0xA0, 0, 12, 56),  # bytes 12, 66, 67!
     'VENDOR_SN':        ('get_string', 0xA0, 0, 68, 16),
     'DATE_CODE':        ('get_string', 0xA0, 0, 84, 8),
     'DIAGNOSTIC_MONITORING_TYPE': ('get_bytes', 0xA0, 0, 92, 1),
     'ENHANCED_OPTIONS': ('get_bytes', 0xA0, 0, 93, 1),
     'SFF_8472_COMPLIANCE': ('get_int', 0xA0, 0, 94, 1),
     'VENDOR_SPECIFIC_EEPROM': ('get_bytes', 0xA0, 0, 96, 32),

     'TEMPERATURE':      ('get_temperature', 0xA2, 0, 96, 2),
     'VCC':              ('get_voltage', 0xA2, 0, 98, 2),
     'TX_BIAS':          ('get_current', 0xA2, 0, 100, 2),
     'TX_POWER':         ('get_power', 0xA2, 0, 102, 2),
     'RX_POWER':         ('get_power', 0xA2, 0, 104, 2),
     'OPT_LASER_TEMP':   ('get_temperature', 0xA2, 0, 106, 2),
     'OPT_TEC':          ('get_signed_current', 0xA2, 0, 108, 2),

     'STATUS_CONTROL':   ('get_bytes', 0xA2, 0, 110, 1),
     'TX_DISABLE_STATE': ('get_bit7', 0xA2, 0, 110, 1),
     'SOFT_TX_DISABLE_SELECT': ('get_bit6', 0xA2, 0, 110, 1),
     'RS_1_STATE':       ('get_bit5', 0xA2, 0, 110, 1),
     'RATE_SELECT_STATE': ('get_bit4', 0xA2, 0, 110, 1),
     'SOFT_RATE_SELECT': ('get_bit3', 0xA2, 0, 110, 1),
     'TX_FAULT_STATE':   ('get_bit2', 0xA2, 0, 110, 1),
     'RX_LOS_STATE':     ('get_bit1', 0xA2, 0, 110, 1),
     'DATA_READY_BAR_STATE': ('get_bit0', 0xA2, 0, 110, 1),
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
                  'TRANSCEIVER',
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
