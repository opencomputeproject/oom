# oom
Open Optical Monitoring - http://www.opencompute.org/wiki/Networking/SpecsAndDesigns#Common_Module_Interface

This is a project to make the contents of optical module EEPROM
accessible to python programmers.  This allows a python programmer
to query the value of dozens of keys (serial Number, module type,
temperature, transmit power, ...), for the optical module in each 
port of a switch.  In addition to key/value read access, the OOM
project also supports key/value write to a limited number of EEPROM
locations, and raw read/write access directly to EEPROM.

NEWS: July 13, 2016

   Updated the version of OOM to 0.4, LOTS of improvements have gone in
   since the last version update.  The most recent change, which triggered
   the version roll, is a reorganization to the code, and a code cleanup
   which allows OOM to be installed as a site-specific python package.

   As of Version 0.4, there is a test directory, for scripts which test
   the OOM code.  There is an apps directory for scripts which provide 
   useful user output from OOM or otherwise call on OOM but are not
   part of the package API.  The data files which drive the simulator 
   SHIM have been moved to the module_data directory.  The remaining files
   in the oom directory are the core OOM library modules, plus the SHIMs 
   and make files to assemble OOM.  (The SHIMs may be factored out as well
   in a future version.)

   OOM can now be installed as a package.  In the top level oom directory
   there is a setup.py script.  AFTER building oom with the desired SHIM,
   oom can be installed with 'python setup.py install'.  Building the 
   appropriate SHIM (simulator(file), aardvark, or the one that matches
   the NOS on which it is installed), must be done first, so that the SHIM
   will be installed with the package.  Note that only the OOM API is
   installed as a package.  The test and apps directories contain scripts
   that can be run from anywhere, but are not installed as part of the
   package.  

   There are many ways to acquire and install OOM, but this recipe is
   known to work in the Cygwin environment, to install the simulator SHIM:
   
	cd <where you want to stage oom>
	mkdir myoom
	cd myoom
	git clone https://github.com/ocpnetworking-wip/oom.git
	cd oom/oom
	make SHIM=file all
	cd ..
	python setup.py install   # installation is complete
	cd apps
	python inventory.py   # shows simulated switch:  SFP, QSFP+, QSFP28

   OOM can also be built for use in a native Windows environment.  The 
   recipe depends on use of the x86_64-w64-mingw32-gcc compiler, and has
   only been used in a Cygwin environment.  This recipe builds with the 
   Aardvark SHIM, for testing devices with an Aardvark USB/i2c adapter.
   If you are using this environment, contact Don (don@thebollingers.org)
   for additional support and documentation. The recipe:
    
	cd <where you want to stage oom>
	mkdir myoom
	cd myoom
	git clone https://github.com/ocpnetworking-wip/oom.git
	cd oom/oom
	make -f makewindows
	<build a ZIP file containing everything in myoom/oom>
	<move the ZIP file to the target Windows system>
	<unpack the ZIP file into the desired Windows folder>
	python setup.py install  # installation is complete
	cd apps
	python inventory.py  # shows Aardvark accessible device(s)


Old News:  February 16, 2016

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

   The new Southbound API is now committed to the master branch, 
   and should be considered accepted for development going forward.

   The 'dev' branch will contain latest updates going forward, and
   is also based on the new Southbound API

   BETA, demo_code and newsouth branches have been removed.  Master
   is stable and complete, previous branches are out of date.


More mundane stuff...

There is a mock Southbound Shim, oom_south.c, among the python modules.
This make file builds the mock shim, installs it, and also installs
some data files with static but real data for some modules.

The user accessible functions are all in oom.py, which constitutes the
"Northbound Interface".  The use of all of these functions is shown
in oomdemo.py <now in the apps directory>.  oomdemo.py is very short, 
demonstrating not only the functionality, but the simplicity of the
interface.

<Now in the test directory...>
keytest.py extracts and displays every key available for SFP modules,
as well as the key collections (functions) available.  

qtest.py extracts and displays every key available for QSFP+ modules,
as well as the key collections (functions) available.  

The build process assumes your C compiler builds libraries that your 
Python interpereter can run!

Note in the makefile the process to populate the module_data directory 
with data with the correct names.  Substitute different source files, 
or give these different numbers in the first character to populate 
different ports with different data.

Questions?  Please contact don@thebollingers.org
