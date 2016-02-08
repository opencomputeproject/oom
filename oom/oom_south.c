/* 
 * Southbound API mock for OOM
 * Uses Finisar "eep" files to provide data
 * Place an eep file in the "./module_data/<n>" to
 * provide simulation data for port <n>
 * Currently limited to 4 ports (implementation hack for simplicity)
 * */

#include <stdio.h>
#include <errno.h>
#include <stdlib.h>
#include <string.h>
#include "oom_south.h"

#define MAXPORTS 6

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


/*
 * get one port.  Allocate all the ports if necessary, 
 * then get the requested port, return it in the pointer to port
 */
int oom_get_port(int n, oom_port_t* port)
{
	oom_port_t* portlist;
	if (initialized == 0) {  /* build global port_array */
		portlist = malloc(sizeof(port_array));
		oom_get_portlist(portlist);
		free(portlist);
	}
	port->port_num = port_array[n].port_num;
	port->port_type = port_array[n].port_type;
	port->seq_num = port_array[n].seq_num;
	port->port_flags = port_array[n].port_flags;
	return(n);
}

/* oom_get_portlist - build 4 ports:
 * 0 - SFP
 * 1 - QSFP+
 * 2 - empty
 * 3 - CFP
 * Port 0, 1, 3 have sequence numbers
 */
int oom_get_portlist(oom_port_t portlist[]) 
{

	char fname[18]; 
	oom_port_t* pptr;
	uint8_t* A0_data;
	int port, stopit, dummy;
	FILE* fp;
	size_t retcount;

	if (initialized == 0) {
		dummy = oom_maxports();  /* allocate memory for all ports */
	}

	/* go ahead and reread the data files even if already initialized */
	for (port = 0; port< MAXPORTS; port++) {
		stopit = 0;
		pptr = &portlist[port];
		pptr->port_num = port;
		pptr->seq_num = 0;
		pptr->port_flags = port*4;  /* different for each port */

		/* Open, read, interpret the A0 data file */
		sprintf(fname, "./module_data/%d.A0", port);
		fp = fopen(fname, "r");
		if (fp == NULL) {
			pptr->port_type = OOM_PORT_TYPE_NOT_PRESENT;
			printf("module %d is not present (%s)\n", port, fname);
			/* perror("errno:"); */
			stopit = 1;
		} 
		if (!stopit) {
		    A0_data = port_i2c_data[port] + 0xA0*256;
		    retcount = fread(A0_data, sizeof(uint8_t), 1, fp);
		    if (retcount != 1) {
		        printf("%s is not a module data file\n", fname);
		        pptr->port_type=OOM_PORT_TYPE_INVALID;
		        stopit = 1;
		    }
		}
		if (!stopit) {
	            if (*A0_data == 3) {  /* first byte is type, 3 == SFP */
		        pptr->port_type = *A0_data;  
			A0_data++;
		        retcount = fread(A0_data, sizeof(uint8_t), 127, fp);
			stopit = SFP_read_A2h(port, pptr);
	             } else if (*A0_data == 'E') {
			 stopit = QSFP_plus_read(port, pptr, fp);
			 if (*A0_data == 0x0D) {
				 pptr->port_type = *A0_data;
			 } else {
				 stopit = 1;
			 }
	             }
		}
		/* copy this port into the global (permanent) port_array */
		port_array[port] = portlist[port];
	}
	/* TODO - undo this kludge */
	/* fake port 3 as a CFP port until file read ability shows up */
	pptr = &portlist[3];
	pptr->port_type=OOM_PORT_TYPE_CFP;
}
int QSFP_plus_read(int port, oom_port_t* pptr, FILE *fp)
{
	/* read QSFP Port data */
	/* Using the already open A0 file pointer, should be pointing
	 * at the second byte of the file, should be 7 lines of 
	 * human text, followed by ASCII hex data for A0 and 4 pages
	 */
	int stopit;
	int j;
	char fname[18]; 
	char* retval;
	char inbuf[80];
	uint8_t* A0_data;

	/* get the REST of the first line, the 1st char has been read */
	retval = fgets(inbuf, 80, fp);
	if ((retval == NULL) ||
	     (strncmp(inbuf, "EPROM Setup", 10) != 0)) {
	  	 printf("%d.A0 is not a module data file\n", port);
		 pptr->port_type=OOM_PORT_TYPE_INVALID;
		 stopit = 1;
	}

	if (!stopit) {
		/* skip the next 6 lines */
		for (j = 0; j < 6; j++) {
			retval = fgets(inbuf, 80, fp);
		}

		/* first block is A0 (lower) data */
		QSFP_readpage(fp, port_i2c_data[port] + 0xA0*256);

		/* next 32 blocks are pages 0-31 */
		/* for QSFP+, read 4 pages */

		for (j = 0; j < 4; j++) {
			stopit = QSFP_readpage(fp, port_page_data[port] + j*128);
		}
	}
	if (stopit == -1) {  /* problem somewhere in readpage() */
		printf("%s is not a module data file\n", fname);
		pptr->port_type=OOM_PORT_TYPE_INVALID;
	}
}

int SFP_read_A2h(int port, oom_port_t* pptr)
{
	int stopit;
	int j;
	char fname[18]; 
	FILE* fp;
	char* retval;
	char inbuf[80];

	/* Open, read, interpret the A2/pages data file */
	sprintf(fname, "./module_data/%d.pages", port);
	fp = fopen(fname, "r");
	if (fp == NULL) {
		pptr->port_type = OOM_PORT_TYPE_NOT_PRESENT;
		/* 
		printf("module %d is not present\n", i);
		perror("errno:");
		*/
		stopit = 1;
	} 
	if (!stopit) {
		retval = fgets(inbuf, 80, fp);
		if ((retval == NULL) ||
	    	    (strncmp(inbuf, ";FCC SETUP", 10) != 0)) {
			printf("%s is not a module data file\n", fname);
			pptr->port_type=OOM_PORT_TYPE_INVALID;
			stopit = 1;
		}
	}

	if (!stopit) {
		/* skip the next 9 lines */
		for (j = 0; j < 9; j++) {
			retval = fgets(inbuf, 80, fp);
		}

		/* first block is A2 (lower) data */
		readpage(fp, port_i2c_data[port] + 0xA2*256);

		/* next 32 blocks are pages 0-31 */
		/* for now, just read page 0 */

		for (j = 0; j < 1; j++) {
			stopit = readpage(fp, port_page_data[port] + j*128);
		}
	}
	if (stopit == -1) {  /* problem somewhere in readpage() */
		printf("%s is not a module data file\n", fname);
		pptr->port_type=OOM_PORT_TYPE_INVALID;
	}
}

/* 
 * QSFP_readpage() reads 128 byte blocks out of the <n>.A0 file
 * decodes the hex, and puts the result into buf, leaving
 * the file pointer ready to read the next block
 */

int QSFP_readpage(FILE* fp, char* buf)
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
0030: 00 01 02 03 04 05 06 07 08 09 0A 0B 0C 0D 0E 0F
          1         2         3         4         5
01234567890123456789012345678901234567890123456789012
		 *  4 char offset, 2 useless bytes
		 *  then 16 bytes, as 2 hex chars, blank separating
		 */
		for (j = 6; j < 52; j += 3) {
			chin = inbuf[j];
			chout = (chin >= 'A') ? (10 + chin - 'A') : chin - '0';
			chout *= 16;
			chin = inbuf[j+1];
			chout += (chin >= 'A') ? (10 + chin - 'A') : chin - '0';
			*bufptr = chout;
			chout_int = chout;
			bufptr++;
		}
	
	}
	/* read 5 more lines of data, the spacers line between data blocks */
	for (i = 0; i < 5; i++) {
		retval = fgets(inbuf, 80, fp);
	}
	return(0);
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
		 
0030: 00000000 0000FF01 23456748 29041100
0123456789012345678901234567890123456789012345

		 *  4 char offset, 2 useless bytes
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

int oom_set_function(oom_port_t* port, oom_functions_t function, int value) 
{
	/* for this mock function, and it's "get" equivalent, store the function in the flags field */
	
	if (value != 0) value = 1;  /* either enabled or disabled */
	port->port_flags = (value << function); /* set the bit to the supplied value */
	return 0;
}

int oom_get_function(oom_port_t* port, oom_functions_t function, int* rv) 
{
	
	*rv = port->port_flags >> function;
	*rv &= 1;
}

int oom_set_memoryraw(oom_port_t* port, int address, int page, int offset, int len, uint8_t* data)
{
	int i, i2clen;
	int pageoffset, pagelen;
	uint8_t* i2cptr;
	uint8_t* pageptr;
	
	/*
	printf("SET: Port: %d, address: 0x%2X, page: %d, offset: %d, len: %d\n", port->port_num, 
		address, page, offset, len);
	*/
	
	i2cptr = port_i2c_data[port->port_num];  /* get the data for this port */
	i2cptr += address*256;  /* select the data at the right i2c address */
	pageptr = port_page_data[port->port_num];  /* point to page data for this port */
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


int oom_get_memoryraw(oom_port_t* port, int address, int page, int offset, int len, uint8_t* data)
{
	int i;
	uint8_t* i2cptr;

	/* comment here to quiet the tracking of this call *
	printf("GET: Port: %d, address: 0x%2X, page: %d, offset: %d, len: %d\n", port->port_num, 
		address, page, offset, len); 
	 * catcher for comment above */
	
	i2cptr = port_i2c_data[port->port_num];  /* get the data for this port */
	i2cptr += address*256;  /* select the data at the right i2c address */
	pmemcpy(&i2cptr[128], &port_page_data[port->port_num][page*128], 128); /* copy page into i2c */

	pmemcpy(data, &i2cptr[offset], len);  /* copy the requested data */
	return(len);
}

int oom_set_memoryraw16(oom_port_t* port, int address, int len, uint16_t* data)
{

	printf("SET16: Port: %d, address: 0x%2X, len: %d\n", port->port_num, address, len);
	if (port->port_type != OOM_PORT_TYPE_CFP) {
		printf("Not a CFP port, not writing to memory\n");
		return(-1);
	}
	
	if ((address < 0x8000) || (address >0xFFFF)) {
		printf("Not a legal CFP address, not writing to memory\n");
		return(-1);
	}

	pmemcpy(&port_CFP_data[port->port_num][address], data, len*2);

	return(len);
}

int oom_get_memoryraw16(oom_port_t* port, int address, int len, uint16_t* data)
{

	printf("GET16: Port: %d, address: 0x%2X, len: %d\n", port->port_num, address, len);
	if (port->port_type != OOM_PORT_TYPE_CFP) {
		printf("Not a CFP port, not writing to memory\n");
		return(-1);
	}
	
	if ((address < 0x8000) || ((address + len - 1) >0xFFFF)) {
		printf("Not a legal CFP address, not writing to memory\n");
		return(-1);
	}

	pmemcpy(data, &port_CFP_data[port->port_num][address], len*2);	

	return(len);
}
