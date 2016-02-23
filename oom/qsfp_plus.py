# qsfp_plus.py
# qsfp+ memory map
# based on SFF-8636, rev 2.6, Section 6, and SFF-8024
# Note that values that range from 0-n are returned as integers (get_int)
# Keys that are encoded as bit fields are returned as raw bytes (get_bytes)


MM = {                  # decoder, addr, page, offset,length
    # ID and status bytes (0-2)
    'IDENTIFIER':       ('get_int', 0xA0, 0, 0, 1),
    'REV_COMPLIANCE':   ('get_int', 0xA0, 0, 1, 1),
    'FLAT_MEM':         ('get_bits', 0xA0, 0, 2, 1, 2, 1),
    'INT_L':            ('get_bits', 0xA0, 0, 2, 1, 1, 1),
    'DATA_NOT_READY':   ('get_bits', 0xA0, 0, 2, 1, 0, 1),

    # Interrupt Flags bytes (3-21)
    'L_TX_RX_LOS':      ('get_bits', 0xA0, 0, 3, 1, 7, 8),  # All 8 LOS bits
    'L_TX4_LOS':        ('get_bits', 0xA0, 0, 3, 1, 7, 1),
    'L_TX3_LOS':        ('get_bits', 0xA0, 0, 3, 1, 6, 1),
    'L_TX2_LOS':        ('get_bits', 0xA0, 0, 3, 1, 5, 1),
    'L_TX1_LOS':        ('get_bits', 0xA0, 0, 3, 1, 4, 1),
    'L_RX4_LOS':        ('get_bits', 0xA0, 0, 3, 1, 3, 1),
    'L_RX3_LOS':        ('get_bits', 0xA0, 0, 3, 1, 2, 1),
    'L_RX2_LOS':        ('get_bits', 0xA0, 0, 3, 1, 1, 1),
    'L_RX1_LOS':        ('get_bits', 0xA0, 0, 3, 1, 0, 1),

    'L_TX_FAULT':       ('get_bits', 0xA0, 0, 4, 1, 7, 8),  # all 8 Fault bits
    'L_TX4_ADAPT_EQ_FAULT': ('get_bits', 0xA0, 0, 4, 1, 7, 1),
    'L_TX3_ADAPT_EQ_FAULT': ('get_bits', 0xA0, 0, 4, 1, 6, 1),
    'L_TX2_ADAPT_EQ_FAULT': ('get_bits', 0xA0, 0, 4, 1, 5, 1),
    'L_TX1_ADAPT_EQ_FAULT': ('get_bits', 0xA0, 0, 4, 1, 4, 1),
    'L_TX4_FAULT':      ('get_bits', 0xA0, 0, 4, 1, 3, 1),
    'L_TX3_FAULT':      ('get_bits', 0xA0, 0, 4, 1, 2, 1),
    'L_TX2_FAULT':      ('get_bits', 0xA0, 0, 4, 1, 1, 1),
    'L_TX1_FAULT':      ('get_bits', 0xA0, 0, 4, 1, 0, 1),

    'L_TX_RX_LOL':      ('get_bits', 0xA0, 0, 5, 1, 7, 8),  # All 8 LOL bits
    'L_TX4_LOL':        ('get_bits', 0xA0, 0, 5, 1, 7, 1),   # Laugh Out Loud?
    'L_TX3_LOL':        ('get_bits', 0xA0, 0, 5, 1, 6, 1),
    'L_TX2_LOL':        ('get_bits', 0xA0, 0, 5, 1, 5, 1),
    'L_TX1_LOL':        ('get_bits', 0xA0, 0, 5, 1, 4, 1),
    'L_RX4_LOL':        ('get_bits', 0xA0, 0, 5, 1, 3, 1),
    'L_RX3_LOL':        ('get_bits', 0xA0, 0, 5, 1, 2, 1),
    'L_RX2_LOL':        ('get_bits', 0xA0, 0, 5, 1, 1, 1),
    'L_RX1_LOL':        ('get_bits', 0xA0, 0, 5, 1, 0, 1),

    'L_TEMP_ALARM_WARN':   ('get_bits', 0xA0, 0, 6, 1, 7, 4),  # all 4 temps
    'L_TEMP_HIGH_ALARM':   ('get_bits', 0xA0, 0, 6, 1, 7, 1),
    'L_TEMP_LOW_ALARM':    ('get_bits', 0xA0, 0, 6, 1, 6, 1),
    'L_TEMP_HIGH_WARNING': ('get_bits', 0xA0, 0, 6, 1, 5, 1),
    'L_TEMP_LOW_WARNING':  ('get_bits', 0xA0, 0, 6, 1, 4, 1),
    'INIT_COMPLETE':    ('get_bits', 0xA0, 0, 6, 1, 0, 1),

    'L_VCC_ALARM_WARN': ('get_bits', 0xA0, 0, 7, 1, 7, 4),  # all 4 VCC
    'L_VCC_HIGH_ALARM': ('get_bits', 0xA0, 0, 7, 1, 7, 1),
    'L_VCC_LOW_ALARM':  ('get_bits', 0xA0, 0, 7, 1, 6, 1),
    'L_VCC_HIGH_WARN':  ('get_bits', 0xA0, 0, 7, 1, 5, 1),
    'L_VCC_LOW_WARN':   ('get_bits', 0xA0, 0, 7, 1, 4, 1),
    'VENDOR_SPECIFIC_8':  ('get_bytes', 0xA0, 0, 8, 1),

    'L_RX1_RX2_POWER': ('get_bits', 0xA0, 0, 9, 1, 7, 8),  # all 8 power bits
    'L_RX1_POWER_HIGH_ALARM':  ('get_bits', 0xA0, 0, 9, 1, 7, 1),
    'L_RX1_POWER_LOW_ALARM':   ('get_bits', 0xA0, 0, 9, 1, 6, 1),
    'L_RX1_POWER_HIGH_WARN':   ('get_bits', 0xA0, 0, 9, 1, 5, 1),
    'L_RX1_POWER_LOW_WARN':    ('get_bits', 0xA0, 0, 9, 1, 4, 1),
    'L_RX2_POWER_HIGH_ALARM':  ('get_bits', 0xA0, 0, 9, 1, 3, 1),
    'L_RX2_POWER_LOW_ALARM':   ('get_bits', 0xA0, 0, 9, 1, 2, 1),
    'L_RX2_POWER_HIGH_WARN':   ('get_bits', 0xA0, 0, 9, 1, 1, 1),
    'L_RX2_POWER_LOW_WARN':    ('get_bits', 0xA0, 0, 9, 1, 0, 1),

    'L_RX3_RX4_POWER': ('get_bits', 0xA0, 0, 10, 1, 7, 8),  # all 8 power bits
    'L_RX3_POWER_HIGH_ALARM':  ('get_bits', 0xA0, 0, 10, 1, 7, 1),
    'L_RX3_POWER_LOW_ALARM':   ('get_bits', 0xA0, 0, 10, 1, 6, 1),
    'L_RX3_POWER_HIGH_WARN':   ('get_bits', 0xA0, 0, 10, 1, 5, 1),
    'L_RX3_POWER_LOW_WARN':    ('get_bits', 0xA0, 0, 10, 1, 4, 1),
    'L_RX4_POWER_HIGH_ALARM':  ('get_bits', 0xA0, 0, 10, 1, 3, 1),
    'L_RX4_POWER_LOW_ALARM':   ('get_bits', 0xA0, 0, 10, 1, 2, 1),
    'L_RX4_POWER_HIGH_WARN':   ('get_bits', 0xA0, 0, 10, 1, 1, 1),
    'L_RX4_POWER_LOW_WARN':    ('get_bits', 0xA0, 0, 10, 1, 0, 1),

    'L_TX1_TX2_BIAS': ('get_bits', 0xA0, 0, 11, 1, 7, 8),  # all 8 bias bits
    'L_TX1_BIAS_HIGH_ALARM':  ('get_bits', 0xA0, 0, 11, 1, 7, 1),
    'L_TX1_BIAS_LOW_ALARM':   ('get_bits', 0xA0, 0, 11, 1, 6, 1),
    'L_TX1_BIAS_HIGH_WARN':   ('get_bits', 0xA0, 0, 11, 1, 5, 1),
    'L_TX1_BIAS_LOW_WARN':    ('get_bits', 0xA0, 0, 11, 1, 4, 1),
    'L_TX2_BIAS_HIGH_ALARM':  ('get_bits', 0xA0, 0, 11, 1, 3, 1),
    'L_TX2_BIAS_LOW_ALARM':   ('get_bits', 0xA0, 0, 11, 1, 2, 1),
    'L_TX2_BIAS_HIGH_WARN':   ('get_bits', 0xA0, 0, 11, 1, 1, 1),
    'L_TX2_BIAS_LOW_WARN':    ('get_bits', 0xA0, 0, 11, 1, 0, 1),

    'L_TX3_TX4_BIAS': ('get_bits', 0xA0, 0, 12, 1, 7, 8),  # all 8 bias bits
    'L_TX3_BIAS_HIGH_ALARM':  ('get_bits', 0xA0, 0, 12, 1, 7, 1),
    'L_TX3_BIAS_LOW_ALARM':   ('get_bits', 0xA0, 0, 12, 1, 6, 1),
    'L_TX3_BIAS_HIGH_WARN':   ('get_bits', 0xA0, 0, 12, 1, 5, 1),
    'L_TX3_BIAS_LOW_WARN':    ('get_bits', 0xA0, 0, 12, 1, 4, 1),
    'L_TX4_BIAS_HIGH_ALARM':  ('get_bits', 0xA0, 0, 12, 1, 3, 1),
    'L_TX4_BIAS_LOW_ALARM':   ('get_bits', 0xA0, 0, 12, 1, 2, 1),
    'L_TX4_BIAS_HIGH_WARN':   ('get_bits', 0xA0, 0, 12, 1, 1, 1),
    'L_TX4_BIAS_LOW_WARN':    ('get_bits', 0xA0, 0, 12, 1, 0, 1),

    'L_TX1_TX2_POWER':  ('get_bits', 0xA0, 0, 13, 1, 7, 8),  # all 8 POWER bits
    'L_TX1_POWER_HIGH_ALARM':  ('get_bits', 0xA0, 0, 13, 1, 7, 1),
    'L_TX1_POWER_LOW_ALARM':   ('get_bits', 0xA0, 0, 13, 1, 6, 1),
    'L_TX1_POWER_HIGH_WARN':   ('get_bits', 0xA0, 0, 13, 1, 5, 1),
    'L_TX1_POWER_LOW_WARN':    ('get_bits', 0xA0, 0, 13, 1, 4, 1),
    'L_TX2_POWER_HIGH_ALARM':  ('get_bits', 0xA0, 0, 13, 1, 3, 1),
    'L_TX2_POWER_LOW_ALARM':   ('get_bits', 0xA0, 0, 13, 1, 2, 1),
    'L_TX2_POWER_HIGH_WARN':   ('get_bits', 0xA0, 0, 13, 1, 1, 1),
    'L_TX2_POWER_LOW_WARN':    ('get_bits', 0xA0, 0, 13, 1, 0, 1),

    'L_TX3_TX4_POWER': ('get_bits', 0xA0, 0, 14, 1, 7, 8),  # all 8 POWER bits
    'L_TX3_POWER_HIGH_ALARM':  ('get_bits', 0xA0, 0, 14, 1, 7, 1),
    'L_TX3_POWER_LOW_ALARM':   ('get_bits', 0xA0, 0, 14, 1, 6, 1),
    'L_TX3_POWER_HIGH_WARN':   ('get_bits', 0xA0, 0, 14, 1, 5, 1),
    'L_TX3_POWER_LOW_WARN':    ('get_bits', 0xA0, 0, 14, 1, 4, 1),
    'L_TX4_POWER_HIGH_ALARM':  ('get_bits', 0xA0, 0, 14, 1, 3, 1),
    'L_TX4_POWER_LOW_ALARM':   ('get_bits', 0xA0, 0, 14, 1, 2, 1),
    'L_TX4_POWER_HIGH_WARN':   ('get_bits', 0xA0, 0, 14, 1, 1, 1),
    'L_TX4_POWER_LOW_WARN':    ('get_bits', 0xA0, 0, 14, 1, 0, 1),

    'VENDOR_SPECIFIC_19':     ('get_bytes', 0xA0, 0, 19, 3),

    # Free Side Device Monitors Bytes (22-33)
    'TEMPERATURE':            ('get_temperature', 0xA0, 0, 22, 2),
    'SUPPLY_VOLTAGE':         ('get_voltage', 0xA0, 0, 26, 2),
    'VENDOR_SPECIFIC_30':     ('get_bytes', 0xA0, 0, 30, 4),

    # Channel Monitors Bytes (34-81)
    'RX1_POWER':        ('get_power', 0xA0, 0, 34, 2),
    'RX2_POWER':        ('get_power', 0xA0, 0, 36, 2),
    'RX3_POWER':        ('get_power', 0xA0, 0, 38, 2),
    'RX4_POWER':        ('get_power', 0xA0, 0, 40, 2),
    'TX1_BIAS':         ('get_current', 0xA0, 0, 42, 2),
    'TX2_BIAS':         ('get_current', 0xA0, 0, 44, 2),
    'TX3_BIAS':         ('get_current', 0xA0, 0, 46, 2),
    'TX4_BIAS':         ('get_current', 0xA0, 0, 48, 2),
    'TX1_POWER':        ('get_power', 0xA0, 0, 50, 2),
    'TX2_POWER':        ('get_power', 0xA0, 0, 52, 2),
    'TX3_POWER':        ('get_power', 0xA0, 0, 54, 2),
    'TX4_POWER':        ('get_power', 0xA0, 0, 56, 2),
    'VENDOR_SPECIFIC_74':     ('get_bytes', 0xA0, 0, 74, 8),

    # Control Bytes (86-98)
    'TX_DISABLE':       ('get_bits', 0xA0, 0, 86, 1, 3, 4),  # low nibble
    'TX4_DISABLE':      ('get_bits', 0xA0, 0, 86, 1, 3, 1),
    'TX3_DISABLE':      ('get_bits', 0xA0, 0, 86, 1, 2, 1),
    'TX2_DISABLE':      ('get_bits', 0xA0, 0, 86, 1, 1, 1),
    'TX1_DISABLE':      ('get_bits', 0xA0, 0, 86, 1, 0, 1),

    'RX_RATE_SELECT':   ('get_bytes', 0xA0, 0, 87, 1),  # all 8 Rate Select
    'RX4_RATE_SELECT':  ('get2_bit6', 0xA0, 0, 87, 1),
    'RX3_RATE_SELECT':  ('get2_bit4', 0xA0, 0, 87, 1),
    'RX2_RATE_SELECT':  ('get2_bit2', 0xA0, 0, 87, 1),
    'RX1_RATE_SELECT':  ('get2_bit0', 0xA0, 0, 87, 1),

    'TX_RATE_SELECT':   ('get_bytes', 0xA0, 0, 88, 1),  # all 8 Rate Select
    'TX4_RATE_SELECT':  ('get2_bit6', 0xA0, 0, 88, 1),
    'TX3_RATE_SELECT':  ('get2_bit4', 0xA0, 0, 88, 1),
    'TX2_RATE_SELECT':  ('get2_bit2', 0xA0, 0, 88, 1),
    'TX1_RATE_SELECT':  ('get2_bit0', 0xA0, 0, 88, 1),

    'RX4_APPLICATION_SELECT': ('get_bytes', 0xA0, 0, 89, 1),
    'RX3_APPLICATION_SELECT': ('get_bytes', 0xA0, 0, 90, 1),
    'RX2_APPLICATION_SELECT': ('get_bytes', 0xA0, 0, 91, 1),
    'RX1_APPLICATION_SELECT': ('get_bytes', 0xA0, 0, 92, 1),

    'HIGH_POWER_CLASS_ENABLE': ('get_bits', 0xA0, 0, 93, 1, 2, 1),
    'POWER_SET':        ('get_bits', 0xA0, 0, 93, 1, 1, 1),
    'POWER_OVERRIDE':   ('get_bits', 0xA0, 0, 93, 1, 0, 1),

    'TX4_APPLICATION_SELECT': ('get_bytes', 0xA0, 0, 94, 1),
    'TX3_APPLICATION_SELECT': ('get_bytes', 0xA0, 0, 95, 1),
    'TX2_APPLICATION_SELECT': ('get_bytes', 0xA0, 0, 96, 1),
    'TX1_APPLICATION_SELECT': ('get_bytes', 0xA0, 0, 97, 1),

    'TX_RX_CDR_CONTROL': ('get_bits', 0xA0, 0, 98, 1, 7, 8),  # all 8 CDR bits
    'TX4_CDR_CONTROL': ('get_bits', 0xA0, 0, 98, 1, 7, 1),
    'TX3_CDR_CONTROL': ('get_bits', 0xA0, 0, 98, 1, 6, 1),
    'TX2_CDR_CONTROL': ('get_bits', 0xA0, 0, 98, 1, 5, 1),
    'TX1_CDR_CONTROL': ('get_bits', 0xA0, 0, 98, 1, 4, 1),
    'RX4_CDR_CONTROL': ('get_bits', 0xA0, 0, 98, 1, 3, 1),
    'RX3_CDR_CONTROL': ('get_bits', 0xA0, 0, 98, 1, 2, 1),
    'RX2_CDR_CONTROL': ('get_bits', 0xA0, 0, 98, 1, 1, 1),
    'RX1_CDR_CONTROL': ('get_bits', 0xA0, 0, 98, 1, 0, 1),


    # Free Side Device and Channel Masks (100-104)
    'M_TX_RX_LOS':       ('get_bytes', 0xA0, 0, 100, 1),  # all 8 LOS bits
    'M_TX_ADAPT_EQ_FAULT':  ('get_bits', 0xA0, 0, 101, 1, 7, 4),  # all 4
    'M_TX_FAULT':        ('get_bits', 0xA0, 0, 101, 1, 3, 4),  # all 4 FAULT
    'M_TX_RX_CDR_LOL':   ('get_bytes', 0xA0, 0, 102, 1),  # all 8 LOS bits
    'M_TEMP_ALARM_WARN': ('get_bits', 0xA0, 0, 103, 1, 7, 4),
    'M_VCC_ALARM_WARN':  ('get_bits', 0xA0, 0, 104, 1, 7, 4),
    'VENDOR_SPECIFIC_105': ('get_bytes', 0xA0, 0, 105, 2),

    # Free Side Device Properties
    'PROPAGATION_DELAY': ('get_intX10', 0xA0, 0, 108, 2),
    'ADVANCED_LOW_POWER_MODE': ('get_bits', 0xA0, 0, 110, 1, 7, 4),
    'FAR_SIDE_MANAGED': ('get3_bit2', 0xA0, 0, 110, 1),  # Gary Larson?
    'FAR_END_IMPLEMENT': ('get3_bit6', 0xA0, 0, 113, 1),
    'NEAR_END_IMPLEMENT': ('get_bits', 0xA0, 0, 113, 1, 3, 4),


    # Passwords (note, these are write-only, they can't be read!)
    # These keys are here to enable their write side counterparts
    'PASSWORD_CHANGE':     ('get_int', 0xA0, 0, 119, 4),
    'PASSWORD_ENTRY':      ('get_int', 0xA0, 0, 123, 4),


    # Page 0, Serial ID fields
    # Note, per the spec: Page 00h Byte 0 and Page 00h Byte 128 shall
    # contain the same parameter values.
    #   'IDENTIFIER':   ('get_int', 0xA0, 0, 128, 1), REDUNDANT w A0,0,0,1
    'EXT_IDENTIFIER':   ('get_int', 0xA0, 0, 129, 1),
    'CONNECTOR':        ('get_int', 0xA0, 0, 130, 1),
    'SPEC_COMPLIANCE':  ('get_bytes', 0xA0, 0, 131, 8),       # see table 33
    'ENCODING':         ('get_int', 0xA0, 0, 139, 1),
    'BR_NOMINAL':       ('get_bitrate', 0xA0, 0, 140, 1),  # bytes 12 and 66!
    'EXT_RATE_COMPLY':  ('get_bits', 0xA0, 0, 141, 1, 0, 1),

    'LENGTH_SMF_KM':    ('get_length_km', 0xA0, 0, 142, 1),
    'LENGTH_OM3_50UM':  ('get_length_2m', 0xA0, 0, 143, 1),
    'LENGTH_OM2_50UM':  ('get_int', 0xA0, 0, 144, 1),
    'LENGTH_OM1_62_5UM':  ('get_int', 0xA0, 0, 145, 1),
    'LENGTH_OM4_OR_CU':    ('get_length_omcu2', 0xA0, 0, 146, 2),

    'DEVICE_TECH':      ('get_bytes', 0xA0, 0, 147, 1),
    'VENDOR_NAME':      ('get_string', 0xA0, 0, 148, 16),
    'EXTENDED_MODULE':  ('get_bytes', 0xA0, 0, 164, 1),
    'VENDOR_OUI':       ('get_bytes', 0xA0, 0, 165, 3),
    'VENDOR_PN':        ('get_string', 0xA0, 0, 168, 16),
    'VENDOR_REV':       ('get_string', 0xA0, 0, 184, 2),

    'WAVELENGTH':     ('get_wavelength2', 0xA0, 0, 147, 41),  # 1 field, 3 keys
    'CU_ATTENUATE_2_5': ('get_CU_2_5', 0xA0, 0, 147, 41),     # 1 field, 3 keys
    'CU_ATTENUATE_5_0': ('get_CU_5_0', 0xA0, 0, 147, 41),     # 1 field, 3 keys
    'WAVELEN_TOLERANCE': ('get_wave_tol', 0xA0, 0, 188, 2),
    'MAX_CASE_TEMP':    ('get_int', 0xA0, 0, 190, 1),

    }


FM = {
    'SERIAL_ID': ('IDENTIFIER',
                  'EXT_IDENTIFIER',
                  'CONNECTOR',
                  'SPEC_COMPLIANCE',
                  'ENCODING',
                  'BR_NOMINAL',
                  'EXT_RATE_COMPLY',
                  'LENGTH_SMF_KM',
                  'LENGTH_OM3_50UM',
                  'LENGTH_OM2_50UM',
                  'LENGTH_OM1_62_5UM',
                  'LENGTH_OM4_OR_CU',
                  'DEVICE_TECH',
                  'VENDOR_NAME',
                  'EXTENDED_MODULE',
                  'VENDOR_OUI',
                  'VENDOR_PN',
                  'VENDOR_REV',
                  'WAVELENGTH',
                  'CU_ATTENUATE_2_5',
                  'CU_ATTENUATE_5_0',
                  'WAVELEN_TOLERANCE',
                  'MAX_CASE_TEMP'
                  ),

    'DOM':      ('TEMPERATURE',
                 'SUPPLY_VOLTAGE',
                 'TX1_BIAS',
                 'TX2_BIAS',
                 'TX3_BIAS',
                 'TX4_BIAS',
                 'TX1_POWER',
                 'TX2_POWER',
                 'TX3_POWER',
                 'TX4_POWER',
                 'RX1_POWER',
                 'RX2_POWER',
                 'RX3_POWER',
                 'RX4_POWER',
                 )
    }


WMAP = {
        'TX4_DISABLE': 'set_bits',
        'TX3_DISABLE': 'set_bits',
        'TX2_DISABLE': 'set_bits',
        'TX1_DISABLE': 'set_bits',
        'PASSWORD_CHANGE': 'set_int',
        'PASSWORD_ENTRY': 'set_int',
       }
