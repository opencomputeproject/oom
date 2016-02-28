# make the C southbound library, organize the pieces

# Select a shim
SHIM=file
# SHIM=ethtool
# SHIM=aardvark

SRC = oom_south.h oom_$(SHIM).c oomsouth_driver.c makefile sfp.py qsfp_plus.py \
      oomdemo.py decode.py oomlib.py \
      MUP0WB0_EEPROM_20160108_192637.txt \
      MUP0WB0_FCCABY_20160108_192637.txt \
      MUQ1BZB_EEPROM_20160108_192514.txt \
      MUQ1BZB_FCCABY_20160108_192514.txt \
      qsfpdatafile.txt

OBJ = ./lib/oom_south.so oomsouth_driver.exe

all: $(SRC) $(OBJ)
	mkdir -p module_data
	cp MUP0WB0_EEPROM_20160108_192637.txt module_data/0.A0
	cp MUP0WB0_FCCABY_20160108_192637.txt module_data/0.pages
	cp MUQ1BZB_EEPROM_20160108_192514.txt module_data/2.A0
	cp MUQ1BZB_FCCABY_20160108_192514.txt module_data/2.pages
	cp qsfpdatafile.txt module_data/5.A0

oomsouth_driver.exe: oomsouth_driver.c oom_internal.o oom_$(SHIM).o \
	             ./lib/oom_south.so makefile
	gcc -Wall -c oomsouth_driver.c
	mkdir -p ./lib
ifeq ($(SHIM), aardvark)
	gcc oomsouth_driver.o oom_internal.o oom_$(SHIM).o \
		aardvark.o -o oomsouth_driver.exe
else
	gcc oomsouth_driver.o oom_internal.o oom_$(SHIM).o \
		-o oomsouth_driver.exe
endif

oom_internal.o: oom_internal.c oom_internal.h
	gcc -Wall -fPIC -c oom_internal.c

./lib/oom_south.so: oom_$(SHIM).c oom_internal.o oom_south.h \
	            makefile
	gcc -Wall -fPIC -c oom_$(SHIM).c
	mkdir -p ./lib
ifeq ($(SHIM), aardvark)
		cp -f aardvark.dll ./lib
		gcc -Wall -c aardvark.c
		gcc -shared oom_internal.o aardvark.o oom_$(SHIM).o \
				-o ./lib/oom_south.so
else
		gcc -shared oom_internal.o oom_$(SHIM).o -o ./lib/oom_south.so
endif

clean:
	rm -f oom_*.o ./lib/oom_south.so oomsouth_driver.exe module_data/* \
		aardvark.o ./lib/aardvark.dll
