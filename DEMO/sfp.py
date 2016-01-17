# sfp.py
# sfp memory map


MM = {
     'IDENTIFIER':       ('mod_id', 0xA0, 0, 0, 1),
     'MOD_ID':           (0xA0, 0, 0, 1),
     'EXT_ID':           (0xA0, 0, 1, 1),
     'CONNECTOR':        (0xA0, 0, 2, 1),

     'TRANSCEIVER':      (0xA0, 0, 3, 1),
     'ENCODING':         (0xA0, 0, 11, 1),
     'BR':               (0xA0, 0, 12, 1),
     'RATE_IDENTIFIER':  (0xA0, 0, 13, 1),
     'LENGTH':           (0xA0, 0, 14, 1),

     'SERIAL_NUMBER':    ('serial_num', 0xA0, 0, 68, 16),
     'VENDOR_SN':        ('serial_num', 0xA0, 0, 68, 16),
     'VENDOR_PN':        (0xA0, 0, 168, 16),
     'VENDOR_REV':       (0xA0, 0, 184, 2),

     'TEMPERATURE':      ('temperature', 0xA2, 0, 96, 2),
     'VCC':              ('voltage', 0xA2, 0, 98, 2),
     'TX_BIAS':          ('txbias', 0xA2, 0, 100, 2),
     'TX_POWER':         ('power', 0xA2, 0, 102, 2),
     'RX_POWER':         ('power', 0xA2, 0, 104, 2),
     'LASER_TEMP_WAVELENGTH':   (0xA2, 0, 106, 2),
     'TEC_CURRENT':     (0xA2, 0, 108, 2),

     'DOM_TEMPERATURE':  (0xA2, 0, 96, 2),
     'DOM_VCC':          (0xA2, 0, 98, 2),
     'DOM_TX_BIAS':      (0xA2, 0, 100, 2),
     'DOM_TX_POWER':     (0xA2, 0, 102, 2),
     'DOM_RX_POWER':     (0xA2, 0, 104, 2),
     'DOM_LASER_TEMP':   (0xA2, 0, 106, 2),
     'DOM_TEC_CURR':     (0xA2, 0, 108, 2),

     'FAWS_TX_LOL':      (0xA2, 0, 111, 1),
     'FAWS_RX_LOL':      (0xA2, 0, 111, 1),
     'FAWS_RX_LOS':      (0xA2, 0, 110, 1),
     'FAWS_TX_FAULT':    (0xA2, 0, 110, 1),


     'FAWS_TX_LOL_MASK'		: 0x00,
     'FAWS_RX_LOL_MASK'		: 0x00,
     'FAWS_RX_LOS_MASK'		: 0x02,
     'FAWS_TX_FAULT_MASK'	: 0x04,
    }

FM = {
    'DOM': ('TEMPERATURE', 'VCC', 'TX_BIAS', 'TX_POWER',
            'RX_POWER'),
    'X_POWER': ('TX_POWER', 'RX_POWER')
    }
