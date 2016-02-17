# oom
Open Optical Monitoring - http://www.opencompute.org/wiki/Networking/SpecsAndDesigns#Common_Module_Interface

This is a project to make the contents of optical module EEPROM
accessible to python programmers.  This allows a python programmer
to query the value of dozens of keys (serial Number, module type,
temperature, transmit power, ...), for the optical module in each 
port of a switch.  In addition to key/value read access, the OOM
project also supports key/value write to a limited number of EEPROM
locations, and raw read/write access directly to EEPROM.

NEWS:  February 16, 2016

   The Master branch has been updated with the latest work:
     - Added table drive oom_set_keyvalue()
     - Added write keys to sfp.py, qsfp_plus.py
     - Added memory map, function map and write map (mmap, fmap, wmap)
       to each (python) port at initialization (oom_get_portlist())
     - Cleaned up mapping of module type to 'sfp.py', 'qsfp_plus.py'.
       New decode types can just be added as new files to the package
       without modifying code.
     - Fixed linux build issues (thanks Dustin)
     - Removed all the pesky DOS <cr> at the end of each line of
       many files (thanks Dustin)
     - I will continue to use the 'dev' branch for upcoming changes
     - Old news and mundane stuff below is still accurate

Old News: Feb 11

   Gravitational waves detected at LIGO. A big day for physics!

   The new Southbound API is now committed to the master branch, 
   and should be considered accepted for development going forward.

   The 'dev' branch will contain latest updates going forward, and
   is also based on the new Southbound API

   BETA, demo_code and newsouth branches have been removed.  Master
   is stable and complete, previous branches are out of date.


More mundane stuff...

Installation has not yet been worked on seriously.  However, this
project should work if all of the \*.py modules are installed in a
location accessible to your python interpreter, AND an appropriate
"Southbound Shim" is also provided in the same location the python
modules are installed.  The Southbound Shim should be a C library
which uses suitable APIs for the host switch/NOS to provide the
necessary (discovery, read, write) functions to the OOM library.

Note to shim implementers:  The Southbound API is defined in
oom_south.h

After fetching the code to a clean directory on your machine, you 
can try 'py setup.py', it has been known to work in a simulated
environment.

There is a mock Southbound Shim, oom_south.c, among the python modules.
There is also a make file, which works in the simulated environment,
but probably does not work unchanged in a real linux environment.
This make file builds the mock shim, installs it, and also installs
some data files with static but real data for some modules.

The user accessible functions are all in oom.py, which constitutes the
"Northbound Interface".  The use of all of these functions is shown
in oomdemo.py.  oomdemo.py is very short, demonstrating not only the
functionality, but the simplicity of the interface.

keytest.py extracts and displays every key available for SFP modules,
as well as the key collections (functions) available.  

qtest.py extracts and displays every key available for QSFP+ modules,
as well as the key collections (functions) available.  

In a Cygwin environment on a Windows PC, you can:

Checkout these files into a clean directory
run 'make'

py oomdemo.py   # runs the demo
py keytest.py   # demonstrates the SFP keys available
py qtest.py     # demonstrates the QSFP+ keys available
oomsouth_driver.exe     # runs C code to exercise the Southbound shim

The build process assumes your C compiler builds libraries that your 
Python interpereter can run!

Note in the makefile the process to create the module_data directory and
populate it with data with the correct names.  Substitute different 
source files, or give these different numbers in the first character
to populate different ports with different data.  Note that port 3 is 
hardwired for now to CFP, with limited support.

Questions?  Please contact don@thebollingers.or
