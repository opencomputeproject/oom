
#/////////////////////////////////////////////////////////////////////
#
# decode.py : decode DOM/FAWS/SerialID... to readable physical units
#
#
#
#
#
#
#
#////////////////////////////////////////////////////////////////////

__author__	= "Yuan Yu"
__version__ = "0.0.1"
__email__	= "yuan.yu@finisar.com"


import binascii

# module ID dictionary
mod_id_dict = { '00':'Unknown',
		'01':'GBIC',
		'02':'Module soldered to MB', 
		'03':'SFP/SFP+/SFP28',
		'04':'300_Pin_XBI',
		'05':'XENPAK',
		'06':'XFP',
		'07':'XFF',
		'08':'XFP-E',
		'09':'XPAK',
		'0A':'X2',
		'0B':'DWDM-SFP/SFP+',
		'0C':'QSFP',
		'0D':'QSFP+',
		'0E':'CXP',
		'0F':'Sheilded Mini Multilane HD 4x',
		'10':'Sheilded Mini Multilane HD 8x',
		'11':'QSFP28',
		'12':'CXP2',
		'13':'CDFP',
		'14':'Sheilded Mini Multilane HD 4x Fanout Calbe',
		'15':'Sheilded Mini Multilane HD 8x Fanout Calbe',
		'16':'CDFP',
		'17':'microQSFP',}


def voltage(x):	#return in V
	if len(x) != 4:
		print "wrong voltage format"
		return

	temp = int("0x"+x, 16)
	result = float(temp*0.1/1000)
	return result


def temperature(x): #return in 'C
    if len(x) != 4:
        print "wrong temperature format"
        return
    temp = int("0x"+x, 16)
    if temp > 0x7FFF:
        temp -= 0x1000
    result = float(temp/256)
    return result


def power(x):	#return in mW
	if len(x) != 4:
		print "wrong power format"
		return

	temp = int("0x"+x, 16)
	result = float(temp*0.1/1000)
	return result

def txbias(x):	#return in mA
	if len(x) != 4:
		print "wrong bias format"
		return

	temp = int("0x"+x, 16)
	result = float(temp/500);
	return result

def serial_num(x): # return 16 bytes string
	if len(x) != 16*2:
		print "wrong serial number format"
		return
	result = x.decode('hex')
	return result

def mod_id(x):	# return Module ID
	if len(x) != 2:
		print "wrong module id format"
		return

	return mod_id_dict.get(x,'Reserved')
		

