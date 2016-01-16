# /////////////////////////////////////////////////////////////////////
#
# decode.py : decode DOM/FAWS/SerialID... to readable physical units
#
#
#
#
#
#
#
# ////////////////////////////////////////////////////////////////////

import binascii


__author__ = "Yuan Yu"
__version__ = "0.0.1"
__email__ = "yuan.yu@finisar.com"


# module ID dictionary, expressed in hex to match the spec
mod_id_dict = {0x00: 'Unknown',
               0x01: 'GBIC',
               0x02: 'Module soldered to MB',
               0x03: 'SFP/SFP+/SFP28',
               0x04: '300_Pin_XBI',
               0x05: 'XENPAK',
               0x06: 'XFP',
               0x07: 'XFF',
               0x08: 'XFP-E',
               0x09: 'XPAK',
               0x0A: 'X2',
               0x0B: 'DWDM-SFP/SFP+',
               0x0C: 'QSFP',
               0x0D: 'QSFP+',
               0x0E: 'CXP',
               0x0F: 'Sheilded Mini Multilane HD 4x',
               0x10: 'Sheilded Mini Multilane HD 8x',
               0x11: 'QSFP28',
               0x12: 'CXP2',
               0x13: 'CDFP',
               0x14: 'Sheilded Mini Multilane HD 4x Fanout Calbe',
               0x15: 'Sheilded Mini Multilane HD 8x Fanout Calbe',
               0x16: 'CDFP',
               0x17: 'microQSFP'}


def voltage(x):  # return in V
    if len(x) != 2:
        print "wrong voltage format"
        return
    temp = ord(x[0])*256 + ord(x[1])
    result = float(temp*0.1/1000)
    return result


def temperature(x):  # return in 'C
    if len(x) != 2:
        print "wrong temperature format"
        return
    temp = ord(x[0])*256 + ord(x[1])
    if temp > 0x7FFF:   # if the sign bit is set
        temp -= 0x8000  # remove the sign bit
        temp = -temp    # and make the result a negative number
    result = float(temp/256)
    return result


def power(x):   # return in mW
    if len(x) != 2:
        print "wrong power format"
        return

    temp = ord(x[0])*256 + ord(x[1])
    result = float(temp*0.1/1000)
    return result


def txbias(x):  # return in mA
    if len(x) != 2:
        print "wrong bias format"
        return

    temp = ord(x[0])*256 + ord(x[1])
    result = float(temp/500)
    return result


def serial_num(x):  # copy 16 bytes into a string
    result = ''
    for i in range(0, 15):
        result += x[i]
    return result


def mod_id(x):  # return Module ID
    if len(x) != 1:
        print "wrong identifier format"
        return
    return mod_id_dict.get(ord(x[0]), 'Reserved')
