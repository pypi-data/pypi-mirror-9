# Setup EPICS installation information
import os,platform

EPICSROOT=os.path.join("/opt/epics/R314")
EPICSBASE=os.path.join(EPICSROOT,"base")
EPICSEXT=os.path.join(EPICSROOT,"extensions")

HOSTARCH="darwin-intel"
#WITH_TK=False
WITH_TK=True
if WITH_TK:
    TKINC="/Library/Frameworks/Tk.framework/Versions/Current/Headers"
    TKLIB="/Library/Frameworks/Tk.framework/Versions/Current"
    TCLINC="/Library/Frameworks/Tcl.framework/Versions/Current/Headers"
    TCLLIB="/Library/Frameworks/Tcl.framework/Versions/Current"

    TKINC="/System/Library/Frameworks/Tk.framework/Versions/Current/Headers"
    TKLIB="/System/Library/Frameworks/Tk.framework/Versions/Current"
    TCLINC="/System/Library/Frameworks/Tcl.framework/Versions/Current/Headers"
    TCLLIB="/System/Library/Frameworks/Tcl.framework/Versions/Current"

    if (int(os.uname()[2].split(".")[0]) >= 10):
        libraries=["ca","asHost","Com","tkstub8.5","tclstub8.5",]
    else:
        libraries=["ca","asHost","Com","tkstub8.4","tclstub8.4",]
else:
    libraries=["ca","asHost","Com",]
