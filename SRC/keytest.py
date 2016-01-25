import oomlib
import decode

port = oomlib.oom_getport(0)
keymap = oomlib.getmm(port.port_type)
for keyx in keymap:
    if len(keymap[keyx]) == 5:
        print keyx + ': ' + str(oomlib.oom_get_keyvalue(port, keyx))

print
print 'byte string keys, in hex:'
print
bytekeys = ('TRANSCEIVER',
            'VENDOR_OUI',
            'CABLE_SPEC',
            'OPTIONS',
            'DIAGNOSTIC_MONITORING_TYPE',
            'ENHANCED_OPTIONS',
            'VENDOR_SPECIFIC_EEPROM',
            'STATUS_CONTROL')
for keyx in bytekeys:
    val = oomlib.oom_get_keyvalue(port, keyx)
    print keyx + ': ' + decode.hexstr(val)

print ' '
print 'functions, with their keys and values:'
print ' '
fnkeys = oomlib.getfm(port.port_type)
for keyx in fnkeys:
    val = oomlib.oom_get_memory(port, keyx)
    print keyx + ': '
    print str(val)
    print
