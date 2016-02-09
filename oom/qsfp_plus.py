# qsfp_plus.py
# qsfp+ memory map
# based on SFF-8436, rev 4.8, Section 7.6, and SFF-8024
# Note that values that range from 0-n are returned as integers (get_int)
# Keys that are encoded as bit fields are returned as raw bytes (get_bytes)


MM = {                  # decoder, addr, page, offset,length
    # ID and status bytes (0-2)
    'IDENTIFIER':       ('get_int', 0xA0, 0, 0, 1),
    'FLAT_MEM':         ('get_bit2', 0xA0, 0, 2, 1),
    'INT_L':            ('get_bit1', 0xA0, 0, 2, 1),

    # Interrupt Flags bytes (3-21)
    'L_TX_RX_LOS':      ('get_bytes', 0xA0, 0, 3, 1),  # All 8 LOS bits
    'L_TX4_LOS':        ('get_bit7', 0xA0, 0, 3, 1),
    'L_TX3_LOS':        ('get_bit6', 0xA0, 0, 3, 1),
    'L_TX2_LOS':        ('get_bit5', 0xA0, 0, 3, 1),
    'L_TX1_LOS':        ('get_bit4', 0xA0, 0, 3, 1),
    'L_RX4_LOS':        ('get_bit3', 0xA0, 0, 3, 1),
    'L_RX3_LOS':        ('get_bit2', 0xA0, 0, 3, 1),
    'L_RX2_LOS':        ('get_bit1', 0xA0, 0, 3, 1),
    'L_RX1_LOS':        ('get_bit0', 0xA0, 0, 3, 1),
    'L_TX_FAULT':       ('get_low_nibl', 0xA0, 0, 4, 1),  # all 4 Fault bits
    'L_TX4_FAULT':      ('get_bit3', 0xA0, 0, 4, 1),
    'L_TX3_FAULT':      ('get_bit2', 0xA0, 0, 4, 1),
    'L_TX2_FAULT':      ('get_bit1', 0xA0, 0, 4, 1),
    'L_TX1_FAULT':      ('get_bit0', 0xA0, 0, 4, 1),

    'L_TEMP_ALARM_WARN':   ('get_high_nibl', 0xA0, 0, 6, 1),  # all 4 temps
    'L_TEMP_HIGH_ALARM':   ('get_bit7', 0xA0, 0, 6, 1),
    'L_TEMP_LOW_ALARM':    ('get_bit6', 0xA0, 0, 6, 1),
    'L_TEMP_HIGH_WARNING': ('get_bit5', 0xA0, 0, 6, 1),
    'L_TEMP_LOW_WARNING':  ('get_bit4', 0xA0, 0, 6, 1),
    'INIT_COMPLETE':    ('get_bit0', 0xA0, 0, 6, 1),

    'L_RX1_RX2_POWER':     ('get_bytes', 0xA0, 0, 9, 1),   # all 8 power bits
    'L_RX1_POWER_HIGH_ALARM':  ('get_bit7', 0xA0, 0, 9, 1),
    'L_RX1_POWER_LOW_ALARM':   ('get_bit6', 0xA0, 0, 9, 1),
    'L_RX1_POWER_HIGH_WARN':   ('get_bit5', 0xA0, 0, 9, 1),
    'L_RX1_POWER_LOW_WARN':    ('get_bit4', 0xA0, 0, 9, 1),
    'L_RX2_POWER_HIGH_ALARM':  ('get_bit3', 0xA0, 0, 9, 1),
    'L_RX2_POWER_LOW_ALARM':   ('get_bit2', 0xA0, 0, 9, 1),
    'L_RX2_POWER_HIGH_WARN':   ('get_bit1', 0xA0, 0, 9, 1),
    'L_RX2_POWER_LOW_WARN':    ('get_bit0', 0xA0, 0, 9, 1),

    'L_RX3_RX4_POWER':     ('get_bytes', 0xA0, 0, 10, 1),   # all 8 power bits
    'L_RX3_POWER_HIGH_ALARM':  ('get_bit7', 0xA0, 0, 10, 1),
    'L_RX3_POWER_LOW_ALARM':   ('get_bit6', 0xA0, 0, 10, 1),
    'L_RX3_POWER_HIGH_WARN':   ('get_bit5', 0xA0, 0, 10, 1),
    'L_RX3_POWER_LOW_WARN':    ('get_bit4', 0xA0, 0, 10, 1),
    'L_RX4_POWER_HIGH_ALARM':  ('get_bit3', 0xA0, 0, 10, 1),
    'L_RX4_POWER_LOW_ALARM':   ('get_bit2', 0xA0, 0, 10, 1),
    'L_RX4_POWER_HIGH_WARN':   ('get_bit1', 0xA0, 0, 10, 1),
    'L_RX4_POWER_LOW_WARN':    ('get_bit0', 0xA0, 0, 10, 1),

    'L_TX1_TX2_BIAS':     ('get_bytes', 0xA0, 0, 11, 1),   # all 8 bias bits
    'L_TX1_BIAS_HIGH_ALARM':  ('get_bit7', 0xA0, 0, 11, 1),
    'L_TX1_BIAS_LOW_ALARM':   ('get_bit6', 0xA0, 0, 11, 1),
    'L_TX1_BIAS_HIGH_WARN':   ('get_bit5', 0xA0, 0, 11, 1),
    'L_TX1_BIAS_LOW_WARN':    ('get_bit4', 0xA0, 0, 11, 1),
    'L_TX2_BIAS_HIGH_ALARM':  ('get_bit3', 0xA0, 0, 11, 1),
    'L_TX2_BIAS_LOW_ALARM':   ('get_bit2', 0xA0, 0, 11, 1),
    'L_TX2_BIAS_HIGH_WARN':   ('get_bit1', 0xA0, 0, 11, 1),
    'L_TX2_BIAS_LOW_WARN':    ('get_bit0', 0xA0, 0, 11, 1),

    'L_TX3_TX4_BIAS':     ('get_bytes', 0xA0, 0, 12, 1),   # all 8 bias bits
    'L_TX3_BIAS_HIGH_ALARM':  ('get_bit7', 0xA0, 0, 12, 1),
    'L_TX3_BIAS_LOW_ALARM':   ('get_bit6', 0xA0, 0, 12, 1),
    'L_TX3_BIAS_HIGH_WARN':   ('get_bit5', 0xA0, 0, 12, 1),
    'L_TX3_BIAS_LOW_WARN':    ('get_bit4', 0xA0, 0, 12, 1),
    'L_TX4_BIAS_HIGH_ALARM':  ('get_bit3', 0xA0, 0, 12, 1),
    'L_TX4_BIAS_LOW_ALARM':   ('get_bit2', 0xA0, 0, 12, 1),
    'L_TX4_BIAS_HIGH_WARN':   ('get_bit1', 0xA0, 0, 12, 1),
    'L_TX4_BIAS_LOW_WARN':    ('get_bit0', 0xA0, 0, 12, 1),

    'VENDOR_SPECIFIC_19':     ('get_bytes', 0xA0, 0, 19, 3),

    # Module Monitors Bytes (22-33)
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
    'VENDOR_SPECIFIC_66':     ('get_bytes', 0xA0, 0, 66, 16),

    # Control Bytes (86-97)
    'TX_DISABLE':       ('get_low_nibl', 0xA0, 0, 86, 1),
    'TX4_DISABLE':      ('get_bit3', 0xA0, 0, 86, 1),
    'TX3_DISABLE':      ('get_bit2', 0xA0, 0, 86, 1),
    'TX2_DISABLE':      ('get_bit1', 0xA0, 0, 86, 1),
    'TX1_DISABLE':      ('get_bit0', 0xA0, 0, 86, 1),

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

    'POWER_SET':        ('get_bit1', 0xA0, 0, 93, 1),
    'POWER_OVERRIDE':   ('get_bit0', 0xA0, 0, 93, 1),

    'TX4_APPLICATION_SELECT': ('get_bytes', 0xA0, 0, 94, 1),
    'TX3_APPLICATION_SELECT': ('get_bytes', 0xA0, 0, 95, 1),
    'TX2_APPLICATION_SELECT': ('get_bytes', 0xA0, 0, 96, 1),
    'TX1_APPLICATION_SELECT': ('get_bytes', 0xA0, 0, 97, 1),

    # Free Side Device and Channel Mask (98-106)
    'M_TX_RX_LOS':      ('get_bytes', 0xA0, 0, 100, 1),  # all 8 LOS bits
    'M_TX_FAULT':       ('get_low_nibl', 0xA0, 0, 101, 1),  # all 4 FAULT
    'M_TEMP_ALARM_WARN': ('get_high_nibl', 0xA0, 0, 103, 1),
    'M_INITIALIZE_COMP': ('get_bit0', 0xA0, 0, 103, 1),
    'M_VCC_ALARM_WARN':  ('get_high_nibl', 0xA0, 0, 104, 1),
    'VENDOR_SPECIFIC_105': ('get_bytes', 0xA0, 0, 105, 2),

    # Password Change Entry Area (119-122)
    # password Entry Area (123-126)
    # note: "Password entry bytes are write only"

    # Page 0, Serial ID fields
    #   'IDENTIFIER':       ('get_int', 0xA0, 0, 128, 1), REDUNDANT w A0,0,0,1
    'EXT_IDENTIFIER':   ('get_int', 0xA0, 0, 129, 1),
    'CONNECTOR':        ('get_int', 0xA0, 0, 130, 1),
    'SPEC_COMPLIANCE':  ('get_bytes', 0xA0, 0, 131, 8),       # see table 33
    'ENCODING':         ('get_int', 0xA0, 0, 139, 1),
    'BR_NOMINAL':       ('get_bitrate', 0xA0, 0, 140, 1),  # bytes 12 and 66!
    'EXT_RATE_COMPLY':  ('get_bit0', 0xA0, 0, 141, 1),

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
    }
