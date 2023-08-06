# Setup EPICS installation information
import os

EPICSROOT=os.path.join("/jk/epics/R314-Current")
EPICSBASE=os.path.join(EPICSROOT,"base")
EPICSEXT=os.path.join(EPICSROOT,"extensions")

HOSTARCH="linux-x86"
#WITH_TK=False
WITH_TK=True
if WITH_TK:
    TKINC="/jk/local/include"
    TKLIB="/jk/local/lib"
    TCLINC=TKINC
    TCLLIB=TKLIB
    libraries=["ca","asHost","Com","tk8.4","tcl8.4",]
else:
    libraries=["ca","asHost","Com"]

