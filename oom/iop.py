from oom import *
from decode import hexstr, mod_id
from datetime import datetime
import sys

# get the Aardvark port
portlist = oom_get_portlist()
port = portlist[0]              # assume one port on Aardvark

# build the name of the file to store results to
vendor_name = oom_get_keyvalue(port, 'VENDOR_NAME').replace(" ","_")[0:8]
outfilename = vendor_name + '_'
vendor_sn = oom_get_keyvalue(port, 'VENDOR_SN').replace(" ","_")
outfilename += vendor_sn + '_EEPROMdecode_'
dt = datetime.now()
dateformat = "%Y%m%d%H%M%S"
timestr = dt.strftime(dateformat)
outfilename += timestr + '.txt'

# see if the output should go to the screen or a file
parms = sys.argv
if (len(parms) > 1):
    if parms[1] == '-f':
        sys.stdout = open(outfilename, 'w+')

# identify the module
print
print '%s %s module' % \
        (oom_get_keyvalue(port, 'VENDOR_NAME'),
         mod_id(chr(port.port_type)))
print 'Part Number: %s  Serial Number: %s' % \
         (oom_get_keyvalue(port, 'VENDOR_PN'),
         oom_get_keyvalue(port, 'VENDOR_SN'))
print outfilename

# print out the Serial ID keys
print
keys = port.fmap['SERIAL_ID']
print 'SERIAL_ID Keys:'
for key in sorted(keys):
    val = oom_get_keyvalue(port, key)
    decoder = port.mmap[key][1]
    if ((decoder == 'get_bytes') or (decoder == 'get_cablespec')):
        valstr = hexstr(val)
    else:
        valstr = str(val)
    print '%s: %s' % (key, valstr)

# print out the Vendor Specific data after the Serial ID data
print
if port.port_type == 0x3:   # SFP
    vend_specific = hexstr(oom_get_keyvalue(port, 'VENDOR_SPECIFIC_96'))
if port.port_type == 0xD:   # QSFP
    vend_specific = hexstr(oom_get_keyvalue(port, 'VENDOR_SPECIFIC_224'))
print 'Vendor Specific: ' + vend_specific

# dump the raw data from the two most popular blocks, by type
print
if port.port_type == 0x3:  # SFP
    print 'I2C Address A0h, bytes 0-127, in hex'
    print_block_hex(oom_get_memory_sff(port, 0xA0, 0, 0, 128), 0)
    print
    print 'I2C Address A2h, bytes 0-127, in hex'
    print_block_hex(oom_get_memory_sff(port, 0xA2, 0, 0, 128), 0)

if port.port_type == 0xD:  # QSFP+
    print 'I2C Address A0h, bytes 0-127, in hex'
    print_block_hex(oom_get_memory_sff(port, 0xA0, 0, 0, 128), 0)
    print
    print 'I2C Address A0h, page 0, bytes 128-255, in hex'
    print_block_hex(oom_get_memory_sff(port, 0xA2, 0, 0, 128), 0)
