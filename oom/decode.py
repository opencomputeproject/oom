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


def get_voltage(x):  # return in V
    if len(x) != 2:
        print "wrong voltage format"
        return
    temp = ord(x[0])*256 + ord(x[1])
    result = float(temp*0.1/1000)
    return result


def get_temperature(x):  # return in 'C
    if len(x) != 2:
        print "wrong temperature format"
        return
    temp = ord(x[0])*256 + ord(x[1])
    if temp > 0x7FFF:   # if the sign bit is set
        temp -= 65536   # take two's complement
    result = float(temp/256.0)
    return result


# note:  get_voltage and get_power are actually identical
# implemented twice so as not to confuse the maintainer :-)
def get_power(x):   # return in mW
    if len(x) != 2:
        print "wrong power format"
        return
    temp = ord(x[0])*256 + ord(x[1])
    result = float(temp*0.1/1000)
    return result


def get_current(x):  # return in mA
    if len(x) != 2:
        print "wrong bias format"
        return

    temp = ord(x[0])*256 + ord(x[1])
    result = float(temp/500.0)
    return result


def get_signed_current(x):  # return in mA
    if len(x) != 2:
        print "wrong bias format"
        return

    temp = ord(x[0])*256 + ord(x[1])
    if temp > 0x7FFF:   # if the sign bit is set
        temp -= 65536   # take two's complement
    result = float(temp/10.0)
    return result


def get_string(x):  # copy the cbuffer into a string
    result = ''
    for i in range(0, len(x)):
        result += x[i]
    return result


def mod_id(x):  # return Module ID
    if len(x) != 1:
        print "wrong identifier format"
        return
    return mod_id_dict.get(ord(x[0]), 'Reserved')


def get_bytes(x):
    retval = b''
    for i in x:
        retval += i
    return retval


def get_int(x):
    result = 0
    if len(x) > 4:
        print "too many bytes to decode into 32 bit int"
        return
    for i in x:
        result = (result * 256) + ord(i)
    return result


def get_intX10(x):
    return get_int(x)*10


def get_high_nibl(x):
    temp = ord(x[0])
    temp &= 0xF0
    return(temp)


def get_low_nibl(x):
    temp = ord(x[0])
    temp &= 0x0F
    return(temp)


# return 2 bits

def get2_bits(x, n):
    temp = ord(x[0])
    temp = temp >> n
    temp %= 4
    return(temp)


def get2_bit6(x):
    return(get2_bits(x, 6))


def get2_bit4(x):
    return(get2_bits(x, 4))


def get2_bit2(x):
    return(get2_bits(x, 2))


def get2_bit0(x):
    return(get2_bits(x, 0))


def get3_bit6(x):  # get bits 6, 5, 4
    temp = ord(x[0])
    temp = temp >> 4
    temp %= 8
    return(temp)


def get3_bit2(x):  # get bits 2, 1, 0
    temp = ord(x[0])
    temp %= 8
    return(temp)


# return true if bit 'n' of 'x' is set
def get_bit(x, n):
    temp = ord(x[0])
    temp = temp >> n
    temp %= 2
    return(temp)


def get_bit7(x):
    return(get_bit(x, 7))


def get_bit6(x):
    return(get_bit(x, 6))


def get_bit5(x):
    return(get_bit(x, 5))


def get_bit4(x):
    return(get_bit(x, 4))


def get_bit3(x):
    return(get_bit(x, 3))


def get_bit2(x):
    return(get_bit(x, 2))


def get_bit1(x):
    return(get_bit(x, 1))


def get_bit0(x):
    return(get_bit(x, 0))


def get_bitrate(x):         # returns nominal bit rate IN MB/s
    rate = ord(x[0])
    # take care here...
    # SFP has a special case for rate 0xFF, encoded here
    # QSFP+ does not have the special case, so only 1 byte is sent
    if ((rate == 255) and (len(x) > 1)):
        if (len(x) < 55):
            print "can't decode bit rate"
            return
        rate = ord(x[54]) * 250  # byte 66 is at 54 (starting at 12)
    else:
        rate = rate * 100
    return rate


def get_brmax(x):         # returns max bit rate IN MB/s
    if (len(x) < 56):
        print "can't decode max bit rate"
        return
    rate = ord(x[0])

    # this is tricky...  If byte 12 is 0xFF, then the bit rate is in
    # byte 66 (in units of 250 MBd), and the limit range of bit rates is
    # byte 67, 'in units of +/- 1%'
    if rate == 255:          # special case, need to use byte 66, 67!
        rate = ord(x[54])    # byte 66 is rate in this case
        rate_max = rate * (250 + (2.5 * (ord(x[55]))))

    # if byte 12 is not 0xFF, then the upper bit rate is in byte 66,
    # 'specified in units of 1% above the nominal bit rate'
    # remember the rate here is byte 12, raw, it must be multiplied
    # by 100.  Be careful changing this formula!
    else:
        rate_max = rate * (100 + ord(x[54]))

    return rate_max


def get_brmin(x):         # returns minimum bit rate IN MB/s
    if (len(x) < 56):
        print "can't decode min bit rate"
        return
    rate = ord(x[0])

    # this is tricky...  If byte 12 is 0xFF, then the bit rate is in
    # byte 66 (in units of 250 MBd), and the limit range of bit rates is
    # byte 67, 'in units of +/- 1%'
    if rate == 255:          # special case, need to use byte 66, 67!
        rate = ord(x[54])    # byte 66 is rate in this case
        rate_min = rate * (250 - (2.5 * (ord(x[55]))))

    # if byte 12 is not 0xFF, then the upper bit rate is in byte 66,
    # 'specified in units of 1% above the nominal bit rate'
    # remember the rate here is byte 12, raw, it must be multiplied
    # by 100.  Be careful changing this formula!
    else:
        rate_min = rate * (100 - ord(x[55]))

    return rate_min


def get_length_km(x):   # returns supported link length in meters
    return ord(x[0]) * 1000


def get_length_100m(x):   # returns supported link length in meters
    return ord(x[0]) * 100


def get_length_10m(x):   # returns supported link length in meters
    return ord(x[0]) * 10


def get_length_2m(x):   # returns supported link length in meters
    return ord(x[0]) * 2


def get_length_omcu(x):   # SFP: length in meters, optical OR COPPER
    if (len(x) < 11):
        print "can't decode OM4/CU max cable length"
        return
    valid = ord(x[0])    # get byte 8
    valid %= 16          # strip bits above 3
    valid /= 4           # lose bits below 2
    if valid == 0:       # if bits 2 and 3 are 0, then optical
        return ord(x[10]) * 10  # Optical, stored value is in 10s of meters
    return ord(x[1])    # Copper, stored value is in meters


def get_length_omcu2(x):   # QSFP+: length in meters, optical OR COPPER
    if (len(x) < 2):
        print "can't decode OM4/CU max cable length"
        return
    txtech = ord(x[1])/16     # Transmitter Technology, byte 147, bits 7-4
    if txtech == 0:      # 850 nm VCSEL
        return ord(x[0]) * 2  # OM4, stored value is in units of 2 meters
    return ord(x[0])    # Copper, stored value is in meters


def get_wavelength(x):   # SFP: requires byte 8 and byte 60, 61
    if (len(x) < 54):
        print "can't decode wavelength"
        return
    valid = ord(x[0])    # get byte 8
    valid %= 16          # strip bits above 3
    valid /= 4           # lose bits below 2
    wavelen = 0
    if valid == 0:       # if bits 2 and 3 are 0, then calculate wavelength
        wavelen = ord(x[52])*256 + ord(x[53])
    return wavelen


def get_cablespec(x):    # requires byte 8 and byte 60, 61
    if (len(x) < 54):
        print "can't decode cable spec"
        return
    valid = ord(x[0])    # get byte 8
    valid %= 16          # strip bits above 3
    valid /= 4           # lose bits below 2
    result = x[52:54]
    if valid == 0:       # optical, cable spec doesn't apply
        result = b'\x00\x00'
    return result


def get_wavelength2(x):   # QSFP: requires byte 147, 186, 187
    if (len(x) < 41):
        print "can't decode wavelength"
        return
    txtech = ord(x[1])/16     # Transmitter Technology, byte 147, bits 7-4
    if txtech >= 10:    # copper technology
        return(0)
    wavelen = ord(x[39])*256 + ord(x[40])
    wavelen = wavelen * 0.05  # value is 20ths of a nanometer!
    return wavelen


def get_wave_tol(x):   # 2 bytes, in 200ths of a nm, return value in nm
    if (len(x) < 2):
        print "can't decode wavelength tolerance"
        return
    wave_tol = ord(x[0])*256 + ord(x[1])
    wave_tol = wave_tol * 0.005  # value is 200ths of a nm
    return wave_tol


def get_CU_2_5(x):    # requires byte 147, 186
    if (len(x) < 40):
        print "can't decode copper attenuation"
        return
    txtech = ord(x[1])/16     # Transmitter Technology, byte 147, bits 7-4
    if txtech >= 10:    # copper technology
        return(ord(x[39]))
    return 0


def get_CU_5_0(x):    # requires byte 147, 187
    if (len(x) < 41):
        print "can't decode copper attenuation"
        return
    txtech = ord(x[1])/16     # Transmitter Technology, byte 147, bits 7-4
    if txtech >= 10:    # copper technology
        return(ord(x[40]))
    return 0


def hexstr(x):
    result = ''
    for i in x:
        result += hex(ord(i))
        result += ' '
    return result
