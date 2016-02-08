# qsfp_plus.py
# qsfp+ memory map
# based on SFF-8436, rev 4.8, Section 7.6, and SFF-8024
# Note that values that range from 0-n are returned as integers (get_int)
# Keys that are encoded as bit fields are returned as raw bytes (get_bytes)


MM = {#                addr, page, offset,length
    'IDENTIFIER':       ('get_int', 0xA0, 0, 0, 1),
    'FLAT_MEM':         ('get_bit2', 0xA0, 0, 2, 1),
    'INT_L':            ('get_bit1', 0xA0, 0, 2, 1),

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

    'L_RX1_RX2_POWER':     ('get_bytes', 0xA0, 0, 9,1),   # all 8 power bits
    'L_RX1_POWER_HIGH_ALARM':  ('get_bit7', 0xA0, 0, 9,1),
    'L_RX1_POWER_LOW_ALARM':   ('get_bit6', 0xA0, 0, 9,1),
    'L_RX1_POWER_HIGH_WARN':   ('get_bit5', 0xA0, 0, 9,1),
    'L_RX1_POWER_LOW_WARN':    ('get_bit4', 0xA0, 0, 9,1),
    'L_RX2_POWER_HIGH_ALARM':  ('get_bit3', 0xA0, 0, 9,1),
    'L_RX2_POWER_LOW_ALARM':   ('get_bit2', 0xA0, 0, 9,1),
    'L_RX2_POWER_HIGH_WARN':   ('get_bit1', 0xA0, 0, 9,1),
    'L_RX2_POWER_LOW_WARN':    ('get_bit0', 0xA0, 0, 9,1),

    'L_RX3_RX4_POWER':     ('get_bytes', 0xA0, 0, 10,1),   # all 8 power bits
    'L_RX3_POWER_HIGH_ALARM':  ('get_bit7', 0xA0, 0, 10,1),
    'L_RX3_POWER_LOW_ALARM':   ('get_bit6', 0xA0, 0, 10,1),
    'L_RX3_POWER_HIGH_WARN':   ('get_bit5', 0xA0, 0, 10,1),
    'L_RX3_POWER_LOW_WARN':    ('get_bit4', 0xA0, 0, 10,1),
    'L_RX4_POWER_HIGH_ALARM':  ('get_bit3', 0xA0, 0, 10,1),
    'L_RX4_POWER_LOW_ALARM':   ('get_bit2', 0xA0, 0, 10,1),
    'L_RX4_POWER_HIGH_WARN':   ('get_bit1', 0xA0, 0, 10,1),
    'L_RX4_POWER_LOW_WARN':    ('get_bit0', 0xA0, 0, 10,1),

    'L_TX1_TX2_BIAS':     ('get_bytes', 0xA0, 0, 11,1),   # all 8 bias bits
    'L_TX1_BIAS_HIGH_ALARM':  ('get_bit7', 0xA0, 0, 11,1),
    'L_TX1_BIAS_LOW_ALARM':   ('get_bit6', 0xA0, 0, 11,1),
    'L_TX1_BIAS_HIGH_WARN':   ('get_bit5', 0xA0, 0, 11,1),
    'L_TX1_BIAS_LOW_WARN':    ('get_bit4', 0xA0, 0, 11,1),
    'L_TX2_BIAS_HIGH_ALARM':  ('get_bit3', 0xA0, 0, 11,1),
    'L_TX2_BIAS_LOW_ALARM':   ('get_bit2', 0xA0, 0, 11,1),
    'L_TX2_BIAS_HIGH_WARN':   ('get_bit1', 0xA0, 0, 11,1),
    'L_TX2_BIAS_LOW_WARN':    ('get_bit0', 0xA0, 0, 11,1),

    'L_TX3_TX4_BIAS':     ('get_bytes', 0xA0, 0, 12,1),   # all 8 bias bits
    'L_TX3_BIAS_HIGH_ALARM':  ('get_bit7', 0xA0, 0, 12,1),
    'L_TX3_BIAS_LOW_ALARM':   ('get_bit6', 0xA0, 0, 12,1),
    'L_TX3_BIAS_HIGH_WARN':   ('get_bit5', 0xA0, 0, 12,1),
    'L_TX3_BIAS_LOW_WARN':    ('get_bit4', 0xA0, 0, 12,1),
    'L_TX4_BIAS_HIGH_ALARM':  ('get_bit3', 0xA0, 0, 12,1),
    'L_TX4_BIAS_LOW_ALARM':   ('get_bit2', 0xA0, 0, 12,1),
    'L_TX4_BIAS_HIGH_WARN':   ('get_bit1', 0xA0, 0, 12,1),
    'L_TX4_BIAS_LOW_WARN':    ('get_bit0', 0xA0, 0, 12,1),

    'VENDOR_SPECIFIC_19':     ('get_bytes', 0xA0, 0, 19, 3),
    'TEMPERATURE':            ('get_temperature', 0xA0, 0, 22, 2),
    'SUPPLY_VOLTAGE':         ('get_voltage', 0xA0, 0, 26, 2),
    'VENDOR_SPECIFIC_30':     ('get_bytes', 0xA0, 0, 30, 4),

    'RX1_POWER':        ('get_power', 0xA0, 0, 34, 2),
    'RX2_POWER':        ('get_power', 0xA0, 0, 36, 2),
    'RX3_POWER':        ('get_power', 0xA0, 0, 38, 2),
    'RX4_POWER':        ('get_power', 0xA0, 0, 40, 2),
    'TX1_BIAS':         ('get_current', 0xA0, 0, 42, 2),
    'TX2_BIAS':         ('get_current', 0xA0, 0, 44, 2),
    'TX3_BIAS':         ('get_current', 0xA0, 0, 46, 2),
    'TX4_BIAS':         ('get_current', 0xA0, 0, 48, 2),
    'VENDOR_SPECIFIC_66':     ('get_bytes', 0xA0, 0, 66, 16),

    'TX_DISABLE':       ('get_low_nibl', 0xA0, 0, 86, 1),
    'TX4_DISABLE':      ('get_bit3', 0xA0, 0, 86, 1),
    'TX3_DISABLE':      ('get_bit2', 0xA0, 0, 86, 1),
    'TX2_DISABLE':      ('get_bit1', 0xA0, 0, 86, 1),
    'TX1_DISABLE':      ('get_bit0', 0xA0, 0, 86, 1),

    'RX_RATE_SELECT':   ('get_bytes', 0xA0, 0, 87, 1),
    'RX4_RATE_SELECT':  ('get2_bit6', 0xA0, 0, 87, 1),
    'RX3_RATE_SELECT':  ('get2_bit4', 0xA0, 0, 87, 1),
    'RX2_RATE_SELECT':  ('get2_bit2', 0xA0, 0, 87, 1),
    'RX1_RATE_SELECT':  ('get2_bit0', 0xA0, 0, 87, 1),

    'TX_RATE_SELECT':   ('get_bytes', 0xA0, 0, 88, 1),
    'TX4_RATE_SELECT':  ('get2_bit6', 0xA0, 0, 88, 1),
    'TX3_RATE_SELECT':  ('get2_bit4', 0xA0, 0, 88, 1),
    'TX2_RATE_SELECT':  ('get2_bit2', 0xA0, 0, 88, 1),
    'TX1_RATE_SELECT':  ('get2_bit0', 0xA0, 0, 88, 1),


    }
