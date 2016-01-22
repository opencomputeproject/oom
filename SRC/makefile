# make the C southbound library, organize the pieces

SRC = oom_south.h oom_south.c oomsouth_driver.c makefile sfp.py qsfp.py \
      oomdemo.py decode.py oomlib.py \
      MUP0WB0_EEPROM_20160108_192637.txt \
      MUP0WB0_FCCABY_20160108_192637.txt \
      MUQ1BZB_EEPROM_20160108_192514.txt \
      MUQ1BZB_FCCABY_20160108_192514.txt

OBJ = ./lib/oom_south.so oomsouth_driver.exe

all: $(SRC) $(OBJ)
	mkdir module_data
	cp MUP0WB0_EEPROM_20160108_192637.txt module_data/0.A0
	cp MUP0WB0_FCCABY_20160108_192637.txt module_data/0.pages
	cp MUQ1BZB_EEPROM_20160108_192514.txt module_data/2.A0
	cp MUQ1BZB_FCCABY_20160108_192514.txt module_data/2.pages
	

oomsouth_driver.exe: oomsouth_driver.c ./lib/oom_south.so makefile
	gcc -c oomsouth_driver.c
	gcc oomsouth_driver.o oom_south.o -o oomsouth_driver.exe

./lib/oom_south.so: oom_south.c oom_south.h makefile
	mkdir -p ./lib
	gcc -c oom_south.c
	gcc -shared oom_south.o -o ./lib/oom_south.so

clean:
	rm -rf oom_south.o ./lib/oom_south.so oomsouth_driver.exe module_data/*
