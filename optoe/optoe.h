
#ifndef _LINUX_OPTOE_H
#define _LINUX_OPTOE_H

#include <linux/types.h>
#include <linux/memory.h>

#ifdef EEPROM_CLASS
#include <linux/eeprom_class.h>
#endif

/*
 * The optoe driver is for read/write access to the EEPROM on standard
 * I2C based optical transceivers (SFP, QSFP, etc)
 *
 * While based on the at24 driver, it eliminates code that supports other
 * types of I2C EEPROMs, and adds support for pages accessed through the
 * page-select register at offset 127.
 */

struct optoe_platform_data {
	u32		byte_len;		/* size (sum of all addr) */
	u16		page_size;		/* for writes */
	u8		flags;

	void		(*setup)(struct memory_accessor *, void *context);
	void		*context;
#ifdef EEPROM_CLASS
	struct eeprom_platform_data *eeprom_data; /* extra data for the eeprom_class */
#endif
};

#endif /* _LINUX_OPTOE_H */
