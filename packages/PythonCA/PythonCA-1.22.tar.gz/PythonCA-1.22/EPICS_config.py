# Setup EPICS installation information
"""
Configuration file for EPICS installation.
"""
import os,platform
try:
    UNAME=platform.uname()[0]
except:
    UNAME="Unknowon"

if (UNAME == "Darwin"):
    from EPICS_config_Darwin import *
elif(UNAME =="Linux"):
    from EPICS_config_Linux import *
elif(UNAME =="Windows"):
    from EPICS_config_Win32 import *
else:
     #EPICSROOT=os.path.join("/Users/Shared/SRC/EPICS/R314")
     #EPICSBASE=os.path.join(EPICSROOT,"base")
     #EPICSEXT=os.path.join(EPICSROOT,"ext3148")
     #HOSTARCH=os.popen(os.path.join(EPICSBASE,"startup/EpicsHostArch.pl")).read()
     pass
