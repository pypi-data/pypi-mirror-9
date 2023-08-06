#!/usr/bin/env python
## @package ca: EPICS-CA interface module for Python.
"""$Source: /opt/epics/R314/modules/soft/kekb/python/PythonCA-1.20.1beta2/RCS/ca.py,v $
CA modlue : EPICS-CA interface module for Python.
This module provide a  version of EPICS-CA and Python interface.
It users C module _ca. _ca module basically maps C-API in EPICS ca library into python. Interface between ca.py and _ca module is  subject for change. You should not depend on it. API in ca.py will be preserved in future releases as much as possible.
Author: Noboru Yamamoto, KEK, JAPAN. -2007.
Contoributors:
$Revision: 1.19 $
"""
#__version__ = "$Revision: 1.22d7 $"

import time,gc,sys,atexit
import threading
import sys
from sys import version_info

if (version_info.major == 3):
    def printfn(x):
        print(x)
else:
    from printfn import printfn

try:
    from exceptions import ValueError
except:
    pass

try:
    import signal
except:
    printfn("signal module is not avaialble")

# force thread module to call PyEval_InitThread in it.
import threading
threading.Thread().start()
#import thread
#thread.start_new_thread(thread.exit_thread,()) 

import _ca
# version from _ca314.cpp
version=_ca.version
__version__ = "$Revision: %s $"%version
revision=_ca.revision
release=_ca.release
hg_release=_ca.hg_release
ca_version=_ca.ca_version

# some constants for EPICS channel Access library
from cadefs import *
from caError import *

# for FNAL version you need to provide _ca_fnal.py and import every thin from them
from _ca_kek import *
#
#from _ca_fnal import *
