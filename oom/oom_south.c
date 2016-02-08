/* 
 * Southbound API mock for OOM
 * Uses Finisar "eep" files to provide data
 * Place an eep file in the "./module_data/<n>" to
 * provide simulation data for port <n>
 * Currently limited to 4 ports (implementation hack for simplicity)
 */

#include <stdio.h>
#include <errno.h>
#include <stdlib.h>
#include <string.h>
#include "oom_south.h"

#define MAXPORTS 4

/* pointers to the data, per port */
/* memory will be allocated as needed for actual data */
uint8_t* port_i2c_data[MAXPORTS];
uint8_t* port_page_data[MAXPORTS];
uint16_t* port_CFP_data[MAXPORTS];

int initialized = 0;
oom_port_t port_array[MAXPORTS];

/* MOCKS */

/* oom_maxports - returns 4 ports (always), like a 4 port switch */
int oom_maxports(void) {
    int i;

    if (initialized == 0) {   /* don't reallocate memory! */
        /* allocate memory for every page of every port */
        for (i = 0; i < MAXPORTS; i++) {
            port_i2c_data[i] = malloc(256*256); /* 256 bytes per ic2c address */
            port_page_data[i] = malloc(128*256); /* 128 bytes for 256 pages */
            port_CFP_data[i] = malloc(65536*2); /* full 64K word memory map */
        }
	initialized = 1;
    }
    return(MAXPORTS);
}


/* oom_get_portlist - build 4 ports:
 * 0 - SFP
 * 1 - QSFP+
 * 2 - empty
 * 3 - CFP
 * Port 0, 1, 3 have sequence numbers
 */
int oom_get_portlist(oom_port_t portlist[], int listsize) 
{

	char fname[18]; 
	oom_port_t* pptr;
	uint8_t* A0_data;
	long i, j, k, stopit;
	FILE* fp;
	char inbuf[80];
	char* retval;
	size_t retcount;

	if (initialized == 0) {
		i = oom_maxports();  /* allocate memory for all ports */
	}
	if ((portlist == NULL) && (listsize == 0)) {  /* asking # of ports */
		return(MAXPORTS);
	}
	if (listsize < MAXPORTS) {   /* not enough room */
		return(-ENOMEM);
	}
		

	/* go ahead and reread the data files even if already initialized */
	for (i = 0; i< MAXPORTS; i++) {
		stopit = 0;
		pptr = &portlist[i];
		pptr->handle = (void *) i;
		pptr->oom_class = OOM_PORT_CLASS_SFF;
		sprintf(pptr->name, "port%d\0", i);

		/* Open, read, interpret the A0 data file */
		sprintf(fname, "./module_data/%d.A0", i);
		fp = fopen(fname, "r");
		if (fp == NULL) {
			pptr->oom_class = OOM_PORT_CLASS_UNKNOWN;
			/* printf("module %d is not present (%s)\n", i, fname); */
			/* perror("errno:"); */
			stopit = 1;
		} 
		if (!stopit) {
			A0_data = port_i2c_data[i] + 0xA0*256;
			retcount = fread(A0_data, sizeof(uint8_t), 128, fp);
			if (retcount != 128) {
				printf("%s is not a module data file\n", fname);
				pptr->oom_class = OOM_PORT_CLASS_UNKNOWN;
				stopit = 1;
			} else {
				/*
				printf("Port %d class: %d\n", i, pptr->oom_class); 
				*/
			}

		}

		/* Open, read, interpret the A2/pages data file */
		if (!stopit) {
			sprintf(fname, "./module_data/%d.pages", i);
			fp = fopen(fname, "r");
			if (fp == NULL) {
				pptr->oom_class = OOM_PORT_CLASS_UNKNOWN;
				/* 
				printf("module %d is not present\n", i);
				perror("errno:");
				*/
				stopit = 1;
			} 
		}
		if (!stopit) {
			retval = fgets(inbuf, 80, fp);
			if ((retval == NULL) ||
		    	    (strncmp(inbuf, ";FCC SETUP", 10) != 0)) {
				printf("%s is not a module data file\n", fname);
				pptr->oom_class = OOM_PORT_CLASS_UNKNOWN;
				stopit = 1;
			}
		}

		if (!stopit) {
			/* skip the next 9 lines */
			for (j = 0; j < 9; j++) {
				retval = fgets(inbuf, 80, fp);
			}

			/* first block is A2 (lower) data */
			readpage(fp, port_i2c_data[i] + 0xA2*256);

			/* next 32 blocks are pages 0-31 */
			/* for now, just read page 0 */

			for (j = 0; j < 1; j++) {
				stopit = readpage(fp, port_page_data[i] + j*128);
			}
		}
		if (stopit == -1) {  /* problem somewhere in readpage() */
			printf("%s is not a module data file\n", fname);
			pptr->oom_class = OOM_PORT_CLASS_UNKNOWN;
		}
	}
	/* TODO - undo this kludge */
	/* fake port 3 as a CFP port until file read ability shows up */
	pptr->oom_class = OOM_PORT_CLASS_CFP;

	/* copy the port_list into the global port_array */
	for (i = 0; i < MAXPORTS; i++) {
		port_array[i] = portlist[i];
	}
	return(0);   /* '0' indicates success filling portlist[] */
}

/* 
 * readpage() reads 128 byte blocks out of the .eep file
 * decodes the hex, and puts the result into buf, leaving
 * the file pointer ready to read the next block
 */

int readpage(FILE* fp, char* buf)
{
	char inbuf[80];
	char* retval;
	int i, j, k;
	char chin;
	uint8_t chout;
	int chout_int;
	char *bufptr;

	bufptr = buf;
	for (i = 0; i< 8; i++) {   /* read 8 lines of data */
		retval = fgets(inbuf, 80, fp);
		if (retval != inbuf) {
			printf("badly formatted module data file\n");
			return(-1);
		}

		/* data looks like this:
		 
.....0030: 00000000 0000FF01 23456748 29041100
0123456789012345678901234567890123456789012345

		 *  5 blanks (dots here for readability), 4 char offset, 2 useless
		 *  then 4 bytes, as 8 hex chars, a blank, and repeating
		 */
		for (j = 6; j < 35; j += 9) {
			for (k = j; k < j+8; k += 2) {
				chin = inbuf[k];
				chout = (chin >= 'A') ? (10 + chin - 'A') : chin - '0';
				chout *= 16;
				chin = inbuf[k+1];
				chout += (chin >= 'A') ? (10 + chin - 'A') : chin - '0';
				*bufptr = chout;
				chout_int = chout;
				bufptr++;
			}
		}
	
	}
	/* read 4 more lines of data, the spacers line between data blocks */
	for (i = 0; i < 4; i++) {
		retval = fgets(inbuf, 80, fp);
	}
	return(0);
}

print_block_hex(uint8_t* buf)
{
	int j, k;
	uint8_t* bufptr8;
	uint32_t tempintchar;

	bufptr8 = buf;
	for (j = 0; j < 8; j++) {
		printf("       " );
		for (k = 0; k < 19; k++) {
			if ((k % 5) == 4) {
				printf(" ");
			} else {
				tempintchar = *bufptr8;
				printf("%.2X", tempintchar);
				bufptr8++;
			}
		}
		printf("\n");
	}
}

/* intercept memcpy, print out parameters (uncomment the printf) */
void *pmemcpy(void *dest, const void *src, size_t n)
{
/*	printf("pmemcpy - dest: %d, src: %d, size: %d\n", dest, src, n); */
	memcpy(dest, src, n);
}


int oom_set_memory_sff(oom_port_t* port, int address, int page, int offset, int len, uint8_t* data)
{
	int i, i2clen;
	int pageoffset, pagelen;
	uint8_t* i2cptr;
	uint8_t* pageptr;
	
	long port_num = (long) port->handle;
	/*
	printf("SET: Port: %d, address: 0x%2X, page: %d, offset: %d, len: %d\n", port_num, 
		address, page, offset, len);
	*/
	
	i2cptr = port_i2c_data[port_num];  /* get the data for this port */
	i2cptr += address*256;  /* select the data at the right i2c address */
	pageptr = port_page_data[port_num];  /* point to page data for this port */
	pageptr += page*128; /* select the right page */
	
	i2clen = 0; /* assume skipping over i2c lower range */
	pageoffset = offset - 128; /* assume skipping over i2c lower range */
	pagelen = len;  /* assume skipping over ic2 lower range */

	if (offset <128) {  /* write just to the end of i2c lower */
		if ((offset + len) > 128) {
			i2clen = 128 - offset;
		} else {
			i2clen = len;
		}
	
		pmemcpy(&i2cptr[offset], data, i2clen); /* write the i2c space */

		/* adjust page pointers to account for writing some to i2c space */
		pageoffset = 0; /* start writing page at beginning */
		pagelen = len - i2clen;
	}
	if (pagelen > 0) { /* some data to be copied to the page */
		pmemcpy(&pageptr[pageoffset], &data[i2clen], pagelen);
	}
	
	return(len);
}


int oom_get_memory_sff(oom_port_t* port, int address, int page, int offset, int len, uint8_t* data)
{
	int i;
	uint8_t* i2cptr;

	long port_num = (long) port->handle;
	/* comment here to quiet the tracking of this call *
	printf("GET: Port: %d, address: 0x%2X, page: %d, offset: %d, len: %d\n", port_num, 
		address, page, offset, len); 
	 * catcher for comment above */
	
	i2cptr = port_i2c_data[port_num];  /* get the data for this port */
	i2cptr += address*256;  /* select the data at the right i2c address */
	pmemcpy(&i2cptr[128], &port_page_data[port_num][page*128], 128); /* copy page into i2c */

	pmemcpy(data, &i2cptr[offset], len);  /* copy the requested data */
	return(len);
}

int oom_set_memory_cfp(oom_port_t* port, int address, int len, uint16_t* data)
{

	long port_num = (long) port->handle;
	printf("SET16: Port: %d, address: 0x%2X, len: %d\n", port_num, address, len);
	if (port->oom_class != OOM_PORT_CLASS_CFP) {
		printf("Not a CFP port, not writing to memory\n");
		return(-1);
	}
	
	if ((address < 0x8000) || (address >0xFFFF)) {
		printf("Not a legal CFP address, not writing to memory\n");
		return(-1);
	}

	pmemcpy(&port_CFP_data[port_num][address], data, len*2);

	return(len);
}

int oom_get_memory_cfp(oom_port_t* port, int address, int len, uint16_t* data)
{

	long port_num = (long) port->handle;
	printf("GET16: Port: %d, address: 0x%2X, len: %d\n", port_num, address, len);
	if (port->oom_class != OOM_PORT_CLASS_CFP) {
		printf("Not a CFP port, not writing to memory\n");
		return(-1);
	}
	
	if ((address < 0x8000) || ((address + len - 1) >0xFFFF)) {
		printf("Not a legal CFP address, not writing to memory\n");
		return(-1);
	}

	pmemcpy(data, &port_CFP_data[port_num][address], len*2);	

	return(len);
}
