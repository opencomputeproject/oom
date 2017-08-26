/*
 * sff_8436_eeprom.c - handle most SFF-8436 based QSFP EEPROMs
 *
 * Copyright (C) 2014 Cumulus networks Inc.
 * Copyright (C) 2017 Finisar Corp.
 *
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Freeoftware Foundation; either version 2 of the License, or
 * (at your option) any later version.
 */

/*
 *	Description:
 *	a) SFF 8436 based qsfp read/write transactions are just like the
 *		at24 eeproms
 *	b) The register/memory layout is up to 256 128 byte pages defined by
 *		a "pages valid" register and switched via a "page select"
 *		register as explained in below diagram.
 *	c) 256 bytes are mapped at a time. 'Lower page 00h' is the first 128
 *	        bytes of address space, and always references the same
 *	        location, independent of the page select register.
 *	        All mapped pages are mapped into the upper 128 bytes 
 *	        (offset 128-255) of the i2c address 50 (A0h in the spec).
 *	d) SFF8472 based sfp read/write transactions are also supported.
 *	        These devices work the same as 8436/qsfp EXCEPT that 
 *	        i2c address 50, (A0h in the spec) addresses a fixed
 *	        256 bytes.  i2c address 51 (A2h in the spec) works like
 *	        the QSFP memory map, with a fixed 128 bytes in the lower
 *	        half and up to 256 pages mapped into the upper half 
 *	        (offset 128-255) of the second i2c client (51 or A2h).
 *	e) The address space is presented, by the driver, as a linear 
 *	        address space.  For QSFP, offset 0-127 are in the lower
 *	        half of address 50/A0h/client[0].  Offset 128-255 are in
 *	        page 0, 256-383 are page 1, etc.  More generally, offset
 *	        'n' resides in page (n/128)-1.  ('page -1' is the lower
 *	        half, offset 0-127).
 *	f) For SFP, the address space places offset 0-127 in the lower
 *	        half of 50/A0/client[0], offset 128-255 in the upper 
 *	        half.  Offset 256-383 is in the lower half of 51/A2/client[1].
 *	        Offset 384-511 is in page 0, in the upper half of 51/A2/...
 *	        Offset 512-639 is in page 1, in the upper half of 51/A2/...
 *	        Offset 'n' is in page (n/128)-3 (for n > 383)
 *
 *	                    SFF 8436 based QSFP Memory Map
 *
 *	                    2-Wire Serial Address: 1010000x
 *
 *	                    Lower Page 00h (128 bytes)
 *	                    =====================
 *	                   |                     |
 *	                   |                     |
 *	                   |                     |
 *	                   |                     |
 *	                   |                     |
 *	                   |                     |
 *	                   |                     |
 *	                   |                     |
 *	                   |                     |
 *	                   |                     |
 *	                   |Page Select Byte(127)|
 *	                    =====================
 *	                              |
 *	                              |
 *	                              |
 *	                              |
 *	                              V
 *	     -----------------------------------------------------------------
 *	    |                  |                    |                         |
 *	    |                  |                    |                         |
 *	    |                  |                    |                         |
 *	    |                  |                    |                         |
 *	    |                  |                    |                         |
 *	    |                  |                    |                         |
 *	    |                  |                    |                         |
 *	    |                  |                    |                         |
 *	    |                  |                    |                         |
 *	    V                  V                    V                         V
 *	 -------------   ----------------      -----------------     --------------
 *	|             | |                |    |                 |   |              |
 *	|   Upper     | |     Upper      |    |     Upper       |   |    Upper     |
 *	|  Page 00h   | |    Page 01h    |    |    Page 02h     |   |   Page 03h   |
 *	|             | |   (Optional)   |    |   (Optional)    |   |  (Optional   |
 *	|             | |                |    |                 |   |   for Cable  |
 *	|             | |                |    |                 |   |  Assemblies) |
 *	|    ID       | |     AST        |    |      User       |   |              |
 *	|  Fields     | |    Table       |    |   EEPROM Data   |   |              |
 *	|             | |                |    |                 |   |              |
 *	|             | |                |    |                 |   |              |
 *	|             | |                |    |                 |   |              |
 *	 -------------   ----------------      -----------------     --------------
 *
 *
 **/

#define DEBUG 1

#include <linux/kernel.h>
#include <linux/init.h>
#include <linux/module.h>
#include <linux/slab.h>
#include <linux/delay.h>
#include <linux/mutex.h>
#include <linux/sysfs.h>
#include <linux/jiffies.h>
#include <linux/i2c.h>
#include <linux/i2c/sff-8436.h>
#include <linux/eeprom_class.h>
#include <linux/types.h>

/* fundamental unit of addressing for SFF_8472/SFF_8436 */
#define SFF_8436_PAGE_SIZE 128
/* 
 * The current 8436 (QSFP) spec provides for only 4 supported
 * pages (pages 0-3).  
 * This driver is prepared to support more, but needs a register in the 
 * EEPROM to indicate how many pages are supported before it is safe
 * to implement more pages in the driver.
 */
#define SFF_8436_SPECED_PAGES 4
#define SFF_8436_EEPROM_SIZE ((1 + SFF_8436_SPECED_PAGES) * SFF_8436_PAGE_SIZE)
#define SFF_8436_EEPROM_UNPAGED_SIZE (2 * SFF_8436_PAGE_SIZE)
/* 
 * The current 8472 (SFP) spec provides for only 3 supported 
 * pages (pages 0-2).
 * This driver is prepared to support more, but needs a register in the 
 * EEPROM to indicate how many pages are supported before it is safe
 * to implement more pages in the driver.
 */
/* #define SFF_8472_SPECED_PAGES 3 */
#define SFF_8472_SPECED_PAGES 128
#define SFF_8472_EEPROM_SIZE ((3 + SFF_8472_SPECED_PAGES) * SFF_8436_PAGE_SIZE)
#define SFF_8472_EEPROM_UNPAGED_SIZE (4 * SFF_8436_PAGE_SIZE)

/* a few constants to find our way around the EEPROM */
#define SFF_8436_PAGE_SELECT_REG   0x7F
#define SFF_8436_PAGEABLE_REG 0x02
#define SFF_8436_NOT_PAGEABLE (1<<2)
#define SFF_8472_PAGEABLE_REG 0x40
#define SFF_8472_PAGEABLE (1<<4)

struct sff_8436_data {
	struct sff_8436_platform_data chip;
	struct memory_accessor macc;
	int use_smbus;

	/*
	 * Lock protects against activities from other Linux tasks,
	 * but not from changes by other I2C masters.
	 */
	struct mutex lock;
	struct bin_attribute bin;
	struct attribute_group attr_group;

	u8 *writebuf;
	unsigned write_max;

	unsigned num_addresses;

	struct eeprom_device *eeprom_dev;

	/* sfp_compat: SFF_8472(SFP) = 1, SFF_8436(QSFP) = 0 */
	int sfp_compat;

	struct i2c_client *client[];
};

typedef enum qsfp_opcode {
	QSFP_READ_OP = 0,
	QSFP_WRITE_OP = 1
} qsfp_opcode_e;

/*
 * This parameter is to help this driver avoid blocking other drivers out
 * of I2C for potentially troublesome amounts of time. With a 100 kHz I2C
 * clock, one 256 byte read takes about 1/43 second which is excessive;
 * but the 1/170 second it takes at 400 kHz may be quite reasonable; and
 * at 1 MHz (Fm+) a 1/430 second delay could easily be invisible.
 *
 * This value is forced to be a power of two so that writes align on pages.
 */
static unsigned io_limit = SFF_8436_PAGE_SIZE;

/*
 * specs often allow 5 msec for a page write, sometimes 20 msec;
 * it's important to recover from write timeouts.
 */
static unsigned write_timeout = 25;

/*
 * flags to distinguish 8472 (SFP family) from 8436 (QSFP family)
 * Note that this flag is the same sense as 'sfp_compat' (1 = SFP)
 */
#define SFF_8436_TYPE_8436 0
#define SFF_8436_TYPE_8472 1

static const struct i2c_device_id sff8436_ids[] = {
/*
	{ "sff8436", SFF_8436_DEVICE_MAGIC(2048 / 8, SFF_8436_TYPE_8436) },
	{ "sff8472", SFF_8436_DEVICE_MAGIC(2048 / 8, SFF_8436_TYPE_8472) },
*/
	{ "sff8436", SFF_8436_TYPE_8436 },
	{ "sff8472", SFF_8436_TYPE_8472 },
	{ "24c04", SFF_8436_TYPE_8472 },
	{ /* END OF LIST */ }
};
MODULE_DEVICE_TABLE(i2c, sff8436_ids);

/*-------------------------------------------------------------------------*/
/*
 * This routine computes the addressing information to be used for
 * a given r/w request.
 *
 * Task is to calculate the client (0 = i2c addr 50, 1 = i2c addr 51),
 * the page, and the offset.
 *
 * Handles both SFP and QSFP.  
 *     For SFP, offset 0-255 are on client[0], >255 is on client[1]
 *     Offset 256-383 are on the lower half of client[1]
 *     Pages are accessible on the upper half of client[1].
 *     Offset >383 are in 128 byte pages mapped into the upper half
 *
 *     For QSFP, all offsets are on client[0]
 *     offset 0-127 are on the lower half of client[0] (no paging)
 *     Pages are accessible on the upper half of client[1].
 *     Offset >127 are in 128 byte pages mapped into the upper half
 *
 *     Callers must not read/write beyond the end of a client or a page
 *     without recomputing the client/page.  Hence offset (within page)
 *     plus length must be less than or equal to 128.  (Note that this
 *     routine does not have access to the length of the call, hence 
 *     cannot do the validity check.)
 *
 * Offset within Lower Page 00h and Upper Page 00h are not recomputed
 */

static uint8_t sff_8436_translate_offset(struct sff_8436_data *sff_8436,
		loff_t *offset, struct i2c_client **client)
{
	unsigned page = 0;

	*client = sff_8436->client[0];

	/* if SFP style, offset > 255, shift to i2c addr 0x51 */
	if (sff_8436->sfp_compat) {
		if (*offset > 255) {
			/* like QSFP, but shifted to client[1] */
			*client = sff_8436->client[1];
			*offset -= 256;  
		}
	}

	/*
	 * if offset is in the range 0-128...
	 * page doesn't matter (using lower half), return 0.
	 * offset is already correct (don't add 128 to get to paged area)
	 */
	if (*offset < SFF_8436_PAGE_SIZE)
		return page;

	/* note, page will always be positive since *offset >= 128 */
	page = (*offset >> 7)-1;
	/* 0x80 places the offset in the top half, offset is last 7 bits */
	*offset = SFF_8436_PAGE_SIZE + (*offset & 0x7f);

	return page;  /* note also returning client and offset */
}

static ssize_t sff_8436_eeprom_read(struct sff_8436_data *sff_8436,
		    struct i2c_client *client,
		    char *buf, unsigned offset, size_t count)
{
	struct i2c_msg msg[2];
	u8 msgbuf[2];
	unsigned long timeout, read_time;
	int status, i;

	memset(msg, 0, sizeof(msg));

	switch (sff_8436->use_smbus) {
	case I2C_SMBUS_I2C_BLOCK_DATA:
		/*smaller eeproms can work given some SMBus extension calls */
		if (count > I2C_SMBUS_BLOCK_MAX)
			count = I2C_SMBUS_BLOCK_MAX;
		break;
	case I2C_SMBUS_WORD_DATA:
		/* Check for odd length transaction */
		count = (count == 1) ? 1 : 2;
		break;
	case I2C_SMBUS_BYTE_DATA:
		count = 1;
		break;
	default:
		/*
		 * When we have a better choice than SMBus calls, use a
		 * combined I2C message. Write address; then read up to
		 * io_limit data bytes.  msgbuf is u8 and will cast to our
		 * needs.
		 */
		i = 0;
		msgbuf[i++] = offset;

		msg[0].addr = client->addr;
		msg[0].buf = msgbuf;
		msg[0].len = i;

		msg[1].addr = client->addr;
		msg[1].flags = I2C_M_RD;
		msg[1].buf = buf;
		msg[1].len = count;
	}

	/*
	 * Reads fail if the previous write didn't complete yet. We may
	 * loop a few times until this one succeeds, waiting at least
	 * long enough for one entire page write to work.
	 */
	timeout = jiffies + msecs_to_jiffies(write_timeout);
	do {
		read_time = jiffies;

		switch (sff_8436->use_smbus) {
		case I2C_SMBUS_I2C_BLOCK_DATA:
			status = i2c_smbus_read_i2c_block_data(client, offset,
					count, buf);
			break;
		case I2C_SMBUS_WORD_DATA:
			status = i2c_smbus_read_word_data(client, offset);
			if (status >= 0) {
				buf[0] = status & 0xff;
				if (count == 2)
					buf[1] = status >> 8;
				status = count;
			}
			break;
		case I2C_SMBUS_BYTE_DATA:
			status = i2c_smbus_read_byte_data(client, offset);
			if (status >= 0) {
				buf[0] = status;
				status = count;
			}
			break;
		default:
			status = i2c_transfer(client->adapter, msg, 2);
			if (status == 2)
				status = count;
		}

		dev_dbg(&client->dev, "eeprom read %zu@%d --> %d (%ld)\n",
				count, offset, status, jiffies);

		if (status == count)  /* happy path */
			return count;

		if (status == -ENXIO) /* no module present */
			return status;

		/* REVISIT: at HZ=100, this is sloooow */
		msleep(1);
	} while (time_before(read_time, timeout));

	return -ETIMEDOUT;
}

static ssize_t sff_8436_eeprom_write(struct sff_8436_data *sff_8436,
		    		struct i2c_client *client,
				const char *buf,
				unsigned offset, size_t count)
{
	struct i2c_msg msg;
	ssize_t status;
	unsigned long timeout, write_time;
	unsigned next_page_start;
	int i = 0;

	/* write max is at most a page
	 * (In this driver, write_max is actually one byte!)
	 */
	if (count > sff_8436->write_max)
		count = sff_8436->write_max;

	/* shorten count if necessary to avoid crossing page boundary */
	next_page_start = roundup(offset + 1, SFF_8436_PAGE_SIZE);
	if (offset + count > next_page_start)
		count = next_page_start - offset;

	switch (sff_8436->use_smbus) {
	case I2C_SMBUS_I2C_BLOCK_DATA:
		/*smaller eeproms can work given some SMBus extension calls */
		if (count > I2C_SMBUS_BLOCK_MAX)
			count = I2C_SMBUS_BLOCK_MAX;
		break;
	case I2C_SMBUS_WORD_DATA:
		/* Check for odd length transaction */
		count = (count == 1) ? 1 : 2;
		break;
	case I2C_SMBUS_BYTE_DATA:
		count = 1;
		break;
	default:
		/* If we'll use I2C calls for I/O, set up the message */
		msg.addr = client->addr;
		msg.flags = 0;

		/* msg.buf is u8 and casts will mask the values */
		msg.buf = sff_8436->writebuf;

		msg.buf[i++] = offset;
		memcpy(&msg.buf[i], buf, count);
		msg.len = i + count;
		break;
	}

	/*
	 * Reads fail if the previous write didn't complete yet. We may
	 * loop a few times until this one succeeds, waiting at least
	 * long enough for one entire page write to work.
	 */
	timeout = jiffies + msecs_to_jiffies(write_timeout);
	do {
		write_time = jiffies;

		switch (sff_8436->use_smbus) {
		case I2C_SMBUS_I2C_BLOCK_DATA:
			status = i2c_smbus_write_i2c_block_data(client,
						offset, count, buf);
			if (status == 0)
				status = count;
			break;
		case I2C_SMBUS_WORD_DATA:
			if (count == 2) {
				status = i2c_smbus_write_word_data(client,
					offset, (u16)((buf[0])|(buf[1] << 8)));
			} else {
				/* count = 1 */
				status = i2c_smbus_write_byte_data(client,
					offset, buf[0]);
			}
			if (status == 0)
				status = count;
			break;
		case I2C_SMBUS_BYTE_DATA:
			status = i2c_smbus_write_byte_data(client, offset,
						buf[0]);
			if (status == 0)
				status = count;
			break;
		default:
			status = i2c_transfer(client->adapter, &msg, 1);
			if (status == 1)
				status = count;
			break;
		}

		dev_dbg(&client->dev, "eeprom write %zu@%d --> %ld (%lu)\n",
				count, offset, (long int) status, jiffies);

		if (status == count)
			return count;

		/* REVISIT: at HZ=100, this is sloooow */
		msleep(1);
	} while (time_before(write_time, timeout));

	return -ETIMEDOUT;
}


static ssize_t sff_8436_eeprom_update_client(struct sff_8436_data *sff_8436,
				char *buf, loff_t off, 
				size_t count, qsfp_opcode_e opcode)
{
	struct i2c_client *client;
	ssize_t retval = 0;
	u8 page = 0;
	loff_t phy_offset = off;
	int ret = 0;

	page = sff_8436_translate_offset(sff_8436, &phy_offset, &client);

	dev_dbg(&client->dev,
			"sff_8436_eeprom_update_client off %lld  page:%d phy_offset:%lld, count:%ld, opcode:%d\n",
			off, page, phy_offset, (long int) count, opcode);
	if (page > 0) {
		ret = sff_8436_eeprom_write(sff_8436, client, &page, 
			SFF_8436_PAGE_SELECT_REG, 1);
		if (ret < 0) {
			dev_dbg(&client->dev,
				"Write page register for page %d failed ret:%d!\n",
					page, ret);
			return ret;
		}
	}

	while (count) {
		ssize_t	status;

		if (opcode == QSFP_READ_OP) {
			status =  sff_8436_eeprom_read(sff_8436, client,
				buf, phy_offset, count);
		} else {
			status =  sff_8436_eeprom_write(sff_8436, client,
				buf, phy_offset, count);
		}
		if (status <= 0) {
			if (retval == 0)
				retval = status;
			break;
		}
		buf += status;
		phy_offset += status;
		count -= status;
		retval += status;
	}


	if (page > 0) {
		/* return the page register to page 0 (why?) */
		page = 0;
		ret = sff_8436_eeprom_write(sff_8436, client, &page, 
			SFF_8436_PAGE_SELECT_REG, 1);
		if (ret < 0) {
			dev_err(&client->dev,
				"Restore page register to page %d failed ret:%d!\n",
					page, ret);
			return ret;
		}
	}
	return retval;
}

/*
 * Figure out if this access is within the range of supported pages.
 * Note this is called on every access because we don't know if the
 * module has been replaced since the last call.
 * If/when modules support more pages, this is the routine to update
 * to validate and allow access to additional pages.
 *
 * Returns updated len for this access:
 *     - entire access is legal, original len is returned.
 *     - access begins legal but is too long, len is truncated to fit.
 *     - initial offset exceeds supported pages, return -EINVAL
 */
static ssize_t sff_8436_page_legal(struct sff_8436_data *sff_8436, 
		loff_t off, size_t len)
{
	struct i2c_client *client = sff_8436->client[0];
	u8 regval;
	int status;
	size_t maxlen;

	if (off < 0) return -EINVAL;
	if (sff_8436->sfp_compat == 1) {
		/* SFP case */
		/* if no pages needed, we're good */
		if ((off + len) <= SFF_8472_EEPROM_UNPAGED_SIZE) return len;
		/* if offset exceeds possible pages, we're not good */
		if (off >= SFF_8472_EEPROM_SIZE) return -EINVAL;
		/* in between, are pages supported? */
		status = sff_8436_eeprom_read(sff_8436, client, &regval, 
				SFF_8472_PAGEABLE_REG, 1);
		if (status < 0) return status;  /* error out (no module?) */
		if (regval & SFF_8472_PAGEABLE) {
			/* Pages supported, trim len to the end of pages */
			maxlen = SFF_8472_EEPROM_SIZE - off;
		} else {
			/* pages not supported, trim len to unpaged size */
			if (off >= SFF_8472_EEPROM_UNPAGED_SIZE) return -EINVAL;
			maxlen = SFF_8472_EEPROM_UNPAGED_SIZE - off;
		}
		len = (len > maxlen) ? maxlen : len;
		dev_dbg(&client->dev,
			"page_legal, SFP, off %lld len %ld\n",
			off, (long int) len);
	} else {
		/* QSFP case */
		/* if no pages needed, we're good */
		if ((off + len) <= SFF_8436_EEPROM_UNPAGED_SIZE) return len;
		/* if offset exceeds possible pages, we're not good */
		if (off >= SFF_8436_EEPROM_SIZE) return -EINVAL;
		/* in between, are pages supported? */
		status = sff_8436_eeprom_read(sff_8436, client, &regval, 
				SFF_8436_PAGEABLE_REG, 1);
		if (status < 0) return status;  /* error out (no module?) */
		if (regval & SFF_8436_NOT_PAGEABLE) {
			/* pages not supported, trim len to unpaged size */
			if (off >= SFF_8436_EEPROM_UNPAGED_SIZE) return -EINVAL;
			maxlen = SFF_8436_EEPROM_UNPAGED_SIZE - off;
		} else {
			/* Pages supported, trim len to the end of pages */
			maxlen = SFF_8436_EEPROM_SIZE - off;
		}
		len = (len > maxlen) ? maxlen : len;
		dev_dbg(&client->dev,
			"page_legal, QSFP, off %lld len %ld\n",
			off, (long int) len);
	}
	return len;
}

static ssize_t sff_8436_read_write(struct sff_8436_data *sff_8436,
		char *buf, loff_t off, size_t len, qsfp_opcode_e opcode)
{
	struct i2c_client *client = sff_8436->client[0];
	int chunk;
	int status = 0;
	ssize_t retval;
	size_t pending_len = 0, chunk_len = 0;
	loff_t chunk_offset = 0, chunk_start_offset = 0;

	if (unlikely(!len))
		return len;

	/*
	 * Read data from chip, protecting against concurrent updates
	 * from this host, but not from other I2C masters.
	 */
	mutex_lock(&sff_8436->lock);
	
	/*
	 * Confirm this access fits within the device suppored addr range 
	 */
	len = sff_8436_page_legal(sff_8436, off, len);
	if (len < 0) {
		status = len;
		goto err;
	}

	/*
	 * For each (128 byte) chunk involved in this request, issue a
	 * separate call to sff_eeprom_update_client(), to
	 * ensure that each access recalculates the client/page
	 * and writes the page register as needed.
	 * Note that chunk to page mapping is confusing, is different for 
	 * QSFP and SFP, and never needs to be done.  Don't try!
	 */
	pending_len = len; /* amount remaining to transfer */
	retval = 0;  /* amount transferred */
	for (chunk = off >> 7; chunk <= (off + len - 1) >> 7; chunk++) {

		/*
		 * Compute the offset and number of bytes to be read/write
		 *
		 * 1. start at offset 0 (within the chunk), and read/write
		 *    the entire chunk
		 * 2. start at offset 0 (within the chunk) and read/write less
		 *    than entire chunk
		 * 3. start at an offset not equal to 0 and read/write the rest
		 *    of the chunk
		 * 4. start at an offset not equal to 0 and read/write less than
		 *    (end of chunk - offset)
		 */
		chunk_start_offset = chunk * SFF_8436_PAGE_SIZE;

		if (chunk_start_offset < off) {
			chunk_offset = off;
			if ((off + pending_len) < (chunk_start_offset +
					SFF_8436_PAGE_SIZE))
				chunk_len = pending_len;
			else
				chunk_len = SFF_8436_PAGE_SIZE - off;
		} else {
			chunk_offset = chunk_start_offset;
			if (pending_len > SFF_8436_PAGE_SIZE)
				chunk_len = SFF_8436_PAGE_SIZE;
			else
				chunk_len = pending_len;
		}

		dev_dbg(&client->dev,
			"sff_r/w: off %lld, len %ld, chunk_start_offset %lld, chunk_offset %lld, chunk_len %ld, pending_len %ld\n",
			off, (long int) len, chunk_start_offset, chunk_offset,
			(long int) chunk_len, (long int) pending_len);

		/* 
		 * note: chunk_offset is from the start of the EEPROM, 
		 * not the start of the chunk 
		 */
		status = sff_8436_eeprom_update_client(sff_8436, buf, 
				chunk_offset, chunk_len, opcode);
		if (status != chunk_len) {
			/* This is another 'no device present' path */
			dev_dbg(&client->dev, 
	"sff_8436_update_client for chunk %d chunk_offset %lld chunk_len %ld failed %d!\n",
				chunk, chunk_offset, (long int) chunk_len, status);
			goto err;
		}
		buf += status;
		pending_len -= status;
		retval += status;
	}
	mutex_unlock(&sff_8436->lock);

	return retval;

err:
	mutex_unlock(&sff_8436->lock);

	return status;
}

static ssize_t sff_8436_bin_read(struct file *filp, struct kobject *kobj,
		struct bin_attribute *attr,
		char *buf, loff_t off, size_t count)
{
	struct i2c_client *client = to_i2c_client(container_of(kobj,
				struct device, kobj));
	struct sff_8436_data *sff_8436 = i2c_get_clientdata(client);

	return sff_8436_read_write(sff_8436, buf, off, count, QSFP_READ_OP);
}


static ssize_t sff_8436_bin_write(struct file *filp, struct kobject *kobj,
		struct bin_attribute *attr,
		char *buf, loff_t off, size_t count)
{
	struct i2c_client *client = to_i2c_client(container_of(kobj,
				struct device, kobj));
	struct sff_8436_data *sff_8436 = i2c_get_clientdata(client);

	return sff_8436_read_write(sff_8436, buf, off, count, QSFP_WRITE_OP);
}
/*-------------------------------------------------------------------------*/

/*
 * This lets other kernel code access the eeprom data. For example, it
 * might hold a board's Ethernet address, or board-specific calibration
 * data generated on the manufacturing floor.
 */

static ssize_t sff_8436_macc_read(struct memory_accessor *macc,
		char *buf, off_t offset, size_t count)
{
	struct sff_8436_data *sff_8436 = container_of(macc,
					struct sff_8436_data, macc);

	return sff_8436_read_write(sff_8436, buf, offset, count, QSFP_READ_OP);
}

static ssize_t sff_8436_macc_write(struct memory_accessor *macc,
		const char *buf, off_t offset, size_t count)
{
	struct sff_8436_data *sff_8436 = container_of(macc,
					struct sff_8436_data, macc);

	return sff_8436_read_write(sff_8436, (char *) buf, offset,
						count, QSFP_WRITE_OP);
}

/*-------------------------------------------------------------------------*/

static int sff_8436_remove(struct i2c_client *client)
{
	struct sff_8436_data *sff_8436;
	int i;

	sff_8436 = i2c_get_clientdata(client);
	sysfs_remove_group(&client->dev.kobj, &sff_8436->attr_group);
	sysfs_remove_bin_file(&client->dev.kobj, &sff_8436->bin);

	for (i = 1; i < sff_8436->num_addresses; i++)
		i2c_unregister_device(sff_8436->client[i]);

	eeprom_device_unregister(sff_8436->eeprom_dev);

	kfree(sff_8436->writebuf);
	kfree(sff_8436);
	return 0;
}

static ssize_t show_sfp_compat(struct device *dev,
			struct device_attribute *dattr, char *buf)
{
	struct i2c_client *client = to_i2c_client(dev);
	struct sff_8436_data *sff_8436 = i2c_get_clientdata(client);
	ssize_t count;

	mutex_lock(&sff_8436->lock);
	count = sprintf(buf, "%d\n", sff_8436->sfp_compat);
	mutex_unlock(&sff_8436->lock);

	return count;
}

static ssize_t set_sfp_compat(struct device *dev,
			struct device_attribute *attr,
			const char *buf, size_t count)
{
	struct i2c_client *client = to_i2c_client(dev);
	struct sff_8436_data *sff_8436 = i2c_get_clientdata(client);
	int sfp_compat;

	if (sscanf(buf, "%d", &sfp_compat) != 1 ||
		sfp_compat < 0 || sfp_compat > 1)
		return -EINVAL;

	mutex_lock(&sff_8436->lock);
	sff_8436->sfp_compat = sfp_compat;
	mutex_unlock(&sff_8436->lock);

	return count;
}

static DEVICE_ATTR(sfp_compatible,  S_IRUGO | S_IWUSR,
					show_sfp_compat, set_sfp_compat);

static struct attribute *sff_8436_attrs[] = {
	&dev_attr_sfp_compatible.attr,
	NULL,
};

static struct attribute_group sff_8436_attr_group = {
	.attrs = sff_8436_attrs,
};

static int sff_8436_eeprom_probe(struct i2c_client *client,
			const struct i2c_device_id *id)
{
	int err;
	int use_smbus = 0;
	struct sff_8436_platform_data chip;
	struct sff_8436_data *sff_8436;
	int num_addresses = 0;
	int i = 0;

	if (client->dev.platform_data) {
		chip = *(struct sff_8436_platform_data *)client->dev.platform_data;
		dev_dbg(&client->dev, "probe, chip provided, flags:0x%x; name: %s\n", chip.flags, client->name);
	} else {
		if (!id->driver_data) {
			err = -ENODEV;
			goto exit;
		}
		dev_dbg(&client->dev, "probe, building chip\n");
		chip.flags = 0;
		chip.setup = NULL;
		chip.context = NULL;
		chip.eeprom_data = NULL;
	}

	/* Use I2C operations unless we're stuck with SMBus extensions. */
	if (!i2c_check_functionality(client->adapter, I2C_FUNC_I2C)) {
		if (i2c_check_functionality(client->adapter,
				I2C_FUNC_SMBUS_READ_I2C_BLOCK)) {
			use_smbus = I2C_SMBUS_I2C_BLOCK_DATA;
		} else if (i2c_check_functionality(client->adapter,
				I2C_FUNC_SMBUS_READ_WORD_DATA)) {
			use_smbus = I2C_SMBUS_WORD_DATA;
		} else if (i2c_check_functionality(client->adapter,
				I2C_FUNC_SMBUS_READ_BYTE_DATA)) {
			use_smbus = I2C_SMBUS_BYTE_DATA;
		} else {
			err = -EPFNOSUPPORT;
			goto exit;
		}
	}


	/*
	 * Make room for two i2c clients, QSFP needs 1, SFP needs 2
	 */
	num_addresses = 2;

	sff_8436 = kzalloc(sizeof(struct sff_8436_data) +
			num_addresses * sizeof(struct i2c_client *),
			GFP_KERNEL);

	if (!sff_8436) {
		err = -ENOMEM;
		goto exit;
	}

	mutex_init(&sff_8436->lock);

	/* determine whether this is an SFP or a QSFP type module */
	if ((strcmp(client->name, "24c04")) && 
	    (strcmp(client->name, "sff8472"))) {
		/* QSFP family */
		sff_8436->sfp_compat = 0;
		chip.byte_len = SFF_8436_EEPROM_SIZE;
		num_addresses = 1;   /* QSFP only uses one i2c addr */
	} else {
		/* SFP family */
		sff_8436->sfp_compat = 1;
		chip.byte_len = SFF_8472_EEPROM_SIZE;
	}
	dev_dbg(&client->dev, "sfp_compat: %d\n", sff_8436->sfp_compat);
	sff_8436->use_smbus = use_smbus;
	sff_8436->chip = chip;
	sff_8436->num_addresses = num_addresses;

	/*
	 * Export the EEPROM bytes through sysfs, since that's convenient.
	 * By default, only root should see the data (maybe passwords etc)
	 */
	sysfs_bin_attr_init(&sff_8436->bin);
	sff_8436->bin.attr.name = "eeprom";
	sff_8436->bin.attr.mode = SFF_8436_FLAG_IRUGO;
	sff_8436->bin.read = sff_8436_bin_read;
	sff_8436->bin.size = chip.byte_len;

	sff_8436->macc.read = sff_8436_macc_read;

	if (!use_smbus ||
			(i2c_check_functionality(client->adapter,
				I2C_FUNC_SMBUS_WRITE_I2C_BLOCK)) ||
			i2c_check_functionality(client->adapter,
				I2C_FUNC_SMBUS_WRITE_WORD_DATA) ||
			i2c_check_functionality(client->adapter,
				I2C_FUNC_SMBUS_WRITE_BYTE_DATA)) {
		/*
		 * NOTE: AN-2079
		 * Finisar recommends that the host implement 1 byte writes
		 * only since this module only supports 32 byte page boundaries.
		 * 2 byte writes are acceptable for PE and Vout changes per
		 * Application Note AN-2071.
		 */
		unsigned write_max = 1;

		sff_8436->macc.write = sff_8436_macc_write;

		sff_8436->bin.write = sff_8436_bin_write;
		sff_8436->bin.attr.mode |= S_IWUSR;

		if (write_max > io_limit)
			write_max = io_limit;
		if (use_smbus && write_max > I2C_SMBUS_BLOCK_MAX)
			write_max = I2C_SMBUS_BLOCK_MAX;
		sff_8436->write_max = write_max;

		/* buffer (data + address at the beginning) */
		sff_8436->writebuf = kmalloc(write_max + 2, GFP_KERNEL);
		if (!sff_8436->writebuf) {
			err = -ENOMEM;
			goto exit_kfree;
		}
	} else {
			dev_warn(&client->dev,
				"cannot write due to controller restrictions.");
	}

	sff_8436->client[0] = client;

	/* use dummy devices for multiple-address chips */
	for (i = 1; i < num_addresses; i++) {
		sff_8436->client[i] = i2c_new_dummy(client->adapter,
					client->addr + i);
		if (!sff_8436->client[i]) {
			dev_err(&client->dev, "address 0x%02x unavailable\n",
				client->addr + i);
			err = -EADDRINUSE;
			goto err_struct;
		}
	}

	/* create the sysfs eeprom file */
	err = sysfs_create_bin_file(&client->dev.kobj, &sff_8436->bin);
	if (err)
		goto err_struct;

	sff_8436->attr_group = sff_8436_attr_group;

	err = sysfs_create_group(&client->dev.kobj, &sff_8436->attr_group);
	if (err) {
		dev_err(&client->dev, "failed to create sysfs attribute group.\n");
		goto err_struct;
	}
	sff_8436->eeprom_dev = eeprom_device_register(&client->dev,
							chip.eeprom_data);
	if (IS_ERR(sff_8436->eeprom_dev)) {
		dev_err(&client->dev, "error registering eeprom device.\n");
		err = PTR_ERR(sff_8436->eeprom_dev);
		goto err_sysfs_cleanup;
	}

	i2c_set_clientdata(client, sff_8436);

	dev_info(&client->dev, "%zu byte %s EEPROM, %s\n",
		sff_8436->bin.size, client->name,
		sff_8436->bin.write ? "read/write" : "read-only");

	if (use_smbus == I2C_SMBUS_WORD_DATA ||
	    use_smbus == I2C_SMBUS_BYTE_DATA) {
		dev_notice(&client->dev, "Falling back to %s reads, "
			   "performance will suffer\n", use_smbus ==
			   I2C_SMBUS_WORD_DATA ? "word" : "byte");
	}

	if (chip.setup)
		chip.setup(&sff_8436->macc, chip.context);

	return 0;

err_sysfs_cleanup:
	sysfs_remove_group(&client->dev.kobj, &sff_8436->attr_group);
	sysfs_remove_bin_file(&client->dev.kobj, &sff_8436->bin);

err_struct:
	for (i = 1; i < num_addresses; i++) {
		if (sff_8436->client[i])
			i2c_unregister_device(sff_8436->client[i]);
	}

	kfree(sff_8436->writebuf);
exit_kfree:
	kfree(sff_8436);
exit:
	dev_dbg(&client->dev, "probe error %d\n", err);

	return err;
}

/*-------------------------------------------------------------------------*/

static struct i2c_driver sff_8436_driver = {
	.driver = {
		.name = "sff8436",
		.owner = THIS_MODULE,
	},
	.probe = sff_8436_eeprom_probe,
	.remove = sff_8436_remove,
	.id_table = sff8436_ids,
};

static int __init sff_8436_init(void)
{

	if (!io_limit) {
		pr_err("sff_8436: io_limit must not be 0!\n");
		return -EINVAL;
	}

	io_limit = rounddown_pow_of_two(io_limit);
	return i2c_add_driver(&sff_8436_driver);
}
module_init(sff_8436_init);

static void __exit sff_8436_exit(void)
{
	i2c_del_driver(&sff_8436_driver);
}
module_exit(sff_8436_exit);

MODULE_DESCRIPTION("Driver for SFF-8436 based QSFP EEPROMs");
MODULE_AUTHOR("VIDYA RAVIPATI <vidya@cumulusnetworks.com>");
MODULE_AUTHOR("DON BOLLINGER <don@thebollingers.org>");
MODULE_LICENSE("GPL");
