# qsfp.py
# qsfp memory map

MM = {#                addr, page, offset,length
    'MOD_ID':           (0xA0, 0, 0, 1),
    'STATUS':           (0xA0, 0, 1, 2),
    'INTERRUPT_FLAGS':  (0xA0, 0, 3, 19),
    'FAWS_TX_LOS':      (0xA0, 0, 3, 1),
    'FAWS_RX_LOS':      (0xA0, 0, 3, 1),
    'FAWS_TX_FAULT':    (0xA0, 0, 4, 1),
    'FAWS_TX_LOL':      (0xA0, 0, 5, 1),
    'FAWS_RX_LOL':      (0xA0, 0, 5, 1),
    
    'DOM_TEMPERATURE':  (0xA0, 0, 22, 2),
    'DOM_VCC':          (0xA0, 0, 26, 2),
    'DOM_TX_BIAS':      (0xA0, 0, 42, 2),
    'DOM_TX_POWER':     (0xA0, 0, 50, 2),
    'DOM_RX_POWER':     (0xA0, 0, 34, 2),
   
    'TX_DIS':           (0xA0, 0, 86, 1),
    'RX_RATE_SELECT':   (0xA0, 0, 87, 1),   
    'TX_RATE_SELECT':   (0xA0, 0, 88, 1),     
    'LOW_POWER_MODE':   (0xA0, 0, 93, 1),

        
    'FAWS_TX_LOL_MASK'		: 0xF0,
    'FAWS_RX_LOL_MASK'		: 0x0F,
    'FAWS_RX_LOS_MASK'		: 0x0F,
    'FAWS_TX_FAULT_MASK'	: 0xFF,


    'EXT_ID':           (0xA0, 0, 129, 1),
    'CONNECTOR':        (0xA0, 0, 130, 1),
    'ENCODING':         (0xA0, 0, 139, 1),
    'BR':               (0xA0, 0, 140, 1),
    'RATE_IDENTIFIER':  (0xA0, 0, 141, 1),
    'LENGTH':           (0xA0, 0, 142, 5),

    'VENDOR_PN':        (0xA0, 0, 168, 16),
    'VENDOR_REV':       (0xA0, 0, 184, 2),
    'VENDOR_SN':        (0xA0, 0, 196, 16),
    }