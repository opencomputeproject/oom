# /////////////////////////////////////////////////////////////////////
#
#  oomsysfsshim.py : An OOM Southbound SHIM, in Python, that
#  reads optical EEPROM data directly from the /sys file system
#  and presents it to the OOM decode layer.  This shim eliminates
#  the compilation phase required for most other OOM shims.
#
#  Copyright 2017  Finisar Inc.
#
#  Author: Don Bollinger don@thebollingers.org
#
# ////////////////////////////////////////////////////////////////////

# import base64
from oomtypes import c_port_t
from oomtypes import port_class_e
from ctypes import create_string_buffer
import errno
import os


#
# where to find eeprom data:  '<root>/<device_name>/<eeprom>'
#
class paths_class:
    def __init__(self):
        # styles define where to find the eeprom data
        # Fields are the directory path, the name of the file containing
        # the name of the port, and the path to the EEPROM file
        #
        # The first style here matches Cumulus, the second is ONL
        self.styles = [
            ['/sys/class/eeprom_dev/', '/label', '/device/eeprom'],
            ['/sys/bus/i2c/devices/', '/sfp_port_number', '/sfp_eeprom'],
                 ]
        # (kludge) code below depends on Cumulus as style 0, ONL as style 1
        self.style = -1

    def nextstyle(self):
        self.style += 1
        if self.style >= len(self.styles):
            raise Exception("Can't find EEPROM files in /sys")
        self.root, self.name, self.eeprom = self.styles[self.style]

paths = paths_class()

MAXPORTS = 512


# build a class that holds the portlist info, state of the shim
class ports:
    def __init__(self):
        # state values:
        #   0 - not initialized (port_array has not been filled)
        #   1 - initialized, port_array is filled, but not copied to user
        #   2 - oom_get_portlist(list, len) has returned the portlist to user
        self.shimstate = 0
        self.portcount = 0
        self.retval = 0
        cport_array = c_port_t * MAXPORTS
        self.portlist = cport_array()
        self.portdir_list = []

    def initports(self):
        # fill an array of ports
        self.portcount = 0

        # figure out the style of /sys files.  Will break out on success.
        while (1):
            paths.nextstyle()   # will throw an exception when out of styles
            try:
                filenames = os.listdir(paths.root)
                # for Cumulus style, confirm sfp_eeprom devices exist
                if paths.style == 0:
                    foundit = 0
                    for name in filenames:
                        eeprom = paths.root + name + paths.eeprom
                        try:
                            fp = open(eeprom, 'r')
                            foundit = 1
                            break  # confirmed Cumulus, get out of for()
                        except:
                            continue
                    if foundit == 1:
                        break   # confirmed Cumulus, get out of while(1)
                    continue
                break

            except:  # if anything fails in this style, move to the next
                continue
            break  # successfully opened the directory, use this style

        #
        # note, we now have our style set, saved in paths class
        # next, check each name to see if it is the dir path for
        # an optical EEPROM device.  Skip any that aren't EEPROM dirs.
        #
        for portdir in filenames:
            if portdir[0] == '.':
                continue

            labelpath = paths.root + portdir + paths.name
            if paths.style == 0:    # Cumulus style
                try:
                    fp = open(labelpath, 'r')
                    portname = fp.readline()
                except:
                    continue
                if len(portname) < 5:    # looking for 'port<num>'
                    continue
                if portname[0:4] != 'port':
                    continue
                # this is the eeprom device we are looking for

            elif paths.style == 1:   # ONL style
                # device names look like '<num>-00<addr>',
                # eg 54-0050.  addr is the i2c address of the
                # EEPROM.  We want only devices with addr '50'
                if portdir[-2:] != '50':
                    continue

                # Get the port number for this eeprom
                try:
                    fp = open(labelpath, 'r')
                    slabel = fp.readline()
                except:
                    continue
                for i in range(len(slabel)):
                    if slabel[i] == 0xA:
                        slabel[i] = '\0'
                label = int(slabel)
                if label == 0:  # note, non-numeric labels return 0 also
                    continue
                portname = "port" + slabel
                # This is the eeprom device we are looking for

            newport = self.portlist[self.portcount]
            newport.handle = self.portcount
            newport.oom_class = port_class_e['SFF']

            # build the name, put it into the c_port_t
            # note the type of newport.cport.name is c_ubyte_Array_32
            # so I can't just assign the string to newport.cport.name
            for i in range(0, 32):
                if i < (len(portname)-1):
                    newport.name[i] = ord(portname[i])
                else:
                    newport.name[i] = 0
            self.portdir_list.append(portdir)
            self.portcount += 1
        self.shimstate = 1
        self.retval = self.portcount
        return self.retval

    def filllist(self, c_port_list, listsize):
        # shimstate 1 means we populated the portlist, but just
        # returned the number of ports.  Don't rebuild the portlist,
        # just copy the one we have.  For any other value, build the list
        # before copying it to c_port_list
        # (0 hasn't been initialized, initialized)
        # (2 has already been returned, caller must want a refresh)
        if self.shimstate != 1:
            if self.initports() < 0:
                return

        # if not enough room, return error
        if listsize < self.portcount:
            self.retval = -errno.ENOMEM
            return

        # if portlist has changed, need to return new portcount, else 0
        self.retval = 0
        if listsize > self.portcount:
            self.retval = self.portcount
        for i in range(0, self.portcount):
            if c_port_list[i] != self.portlist[i]:
                c_port_list[i] = self.portlist[i]
                self.retval = self.portcount
        shimstate = 2
        return


# initialize the ports class (in not initialized state!)
allports = ports()


def oom_get_portlist(cport_list, numports):
    if (cport_list == 0) and (numports == 0):   # how many ports?
        return allports.initports()
    else:   # return a list of ports
        allports.filllist(cport_list, numports)
        return allports.retval


def setparms(parms):
    return


# cport.handle is a c_void_p, but not really :-(
# turn it into an integer by handling '0 is None'
def gethandle(cport):
    handle = cport.handle
    if handle is None:
        handle = 0
    return handle


#
# common code between oom_{get, set}_memory_sff
#
def open_and_seek(cport, address, page, offset):
    # sanity check
    if (address < 0xA0) or (address == 0xA1) or (address > 0xA2):
        return -errno.EINVAL

    # open the the EEPROM file
    handle = gethandle(cport)
    portdir = allports.portdir_list[handle]
    eeprompath = paths.root + portdir + paths.eeprom
    try:
        fp = open(eeprompath, 'rb+', 0)
    except IOError, err:
        return -err.errno

    # calculate the place to start reading/writing data
    if offset < 128:
        # offset less than 128 is the same for all pages
        seekto = offset
    else:
        seekto = page * 128 + offset

    # If 0xA2 is being addressed, it is SFP, and starts at offset 256
    if address == 0xA2:
        seekto += 256

    try:
        fp.seek(seekto)
    except IOError, err:
        return -err.errno

    return fp


#
# note, we are in oomsouth, so 'cport' is actually a c_port_t
#
def oom_get_memory_sff(cport, address, page, offset, length, data):

    if length != len(data):
        return -errno.EINVAL
    fd = open_and_seek(cport, address, page, offset)
    if (fd < 0):
        return fd

    # and read it!
    try:
        buf = fd.read(length)
    except IOError, err:
        return -err.errno

    # copy the buffer into the data array
    ptr = 0
    for c in buf:
        data[ptr] = c
        ptr += 1
    return len(data)


#
# oom_set_memory_sff
#
def oom_set_memory_sff(cport, address, page, offset, length, data):

    if length > len(data):
        return -errno.EINVAL
    fd = open_and_seek(cport, address, page, offset)
    if (fd < 0):
        return fd

    # and write it!
    try:
        fd.write(data[0:length])
    except IOError, err:
        return -err.errno

    # success
    return length
