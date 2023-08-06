#!/usr/bin/env python
"""
Setup file for Ca-Python using distutils package.
Python2.4 or later should be used.

Version Info:
  $Id: setup.py,v 1.22 2010/08/18 06:46:32 noboru Exp noboru $
  $Revision: 1.22 $
  $Author: noboru $
  $Log: setup.py,v $

  Revision 1.22  2010/08/18 06:46:32  noboru
  support python3

  Revision 1.6  2007/03/20 11:48:56  noboru
  Add RCS keywords to setup.py
"""

import os,platform
try:
    UNAME=platform.uname()[0]
except:
    UNAME="Unknowon"

# use Environmet Variable first and then try config files.
try:
    EPICSROOT=os.environ["EPICS_ROOT"]
    EPICSBASE=os.path.join(EPICSROOT,"base")
    EPICSEXT=os.path.join(EPICSROOT,"extensions")
except KeyError:
    EPICSROOT=None

try:
    EPICSBASE=os.environ["EPICS_BASE"]
    if not EPICSROOT:
        EPICSROOT=os.path.dirname(EPICSBASE)
        EPICSEXT=os.path.join(EPICSROOT,"extensions")
except KeyError:
    EPICSBASE=None

try:
    EPICSEXT=os.environ["EPICS_EXTENSIONS"]
    if not EPICSROOT:
        EPICSROOT=os.path.dirname(EPICSEXT)
    if not EPICSBASE:
        EPICSBASE=os.path.join(EPICSROOT,"base")
except KeyError:
    EPICSEXT=None

try:
    TKINC=os.environ["TK_INC"]
except KeyError:
    TKINC="/usr/local/include"

## Tk include/library path
try:
    TKLIB=os.environ["TK_LIB"]
except KeyError:
    TKLIB="/usr/local"
# read config file if any
libraries=None
WITH_TK=False
try:
    if (UNAME == "Darwin"):
        from EPICS_config_Darwin import *
    elif(UNAME =="Linux"):
        from EPICS_config_Linux import *
    elif(UNAME =="Windows"):
        from EPICS_config_Win32 import *
        #UNAME="WIN32"
    else:
        from EPICS_config import *
except ImportError:
    print("No config file. Retain Environment variable setting.")

assert(EPICSROOT)
assert(EPICSBASE)
assert(EPICSEXT)

if (HOSTARCH==None):
    HOSTARCH=os.popen(os.path.join(EPICSBASE,"startup/EpicsHostArch.pl")).read()

assert(HOSTARCH)

if WITH_TK:
    assert(TKINC)
    assert(TKLIB)

# choose _ca source
#CA_SOURCE="_ca.c"  # for NON-threaded version
CA_SOURCE="_ca314.cpp" # for threaded version.

## start normal setup.
from distutils.core import setup,Extension
rev="$Revision: 1.22d8$"
rev="$Revision: 1.22$"
release = os.popen("hg log -r tip --template '{latesttag}.{latesttagdistance}-{node|short}'").read()

if (libraries==None):
    if UNAME.lower() == "alpha":
        libraries=["ca","As","Com"]
    else:
        WITH_TK=True
        libraries=["ca","asHost","Com","tk","tcl",]
if WITH_TK:
    tk_include_dir=[os.path.join(TKINC, "include"), 
                    os.path.join(TKINC),
                    os.path.join(TCLINC, "include"), 
                    os.path.join(TCLINC),]
else:
    tk_include_dir=[]
#
setup(name="PythonCA",
      version=rev[11:-1],
      author="Noboru Yamamoto, KEK, JAPAN",
      author_email = "Noboru.YAMAMOTO_at_kek.jp",
      description="EPICS CA library interface module",
      long_description="""
      EPICS CA library interface module (KEK, Japan)
      """,
      url="http://www-acc.kek.jp/EPICS_Gr/products.html",
      download_url="http://www-acc.kek.jp/EPICS_Gr/products.html",
      classifiers=['Programming Language :: C++',
                   'Programming Language :: Python :: 2.7',
                   'Topic :: Scientific/Engineering :: Interface Engine/Protocol Translator',
                   #'Topic :: EPICS CA',
                   #'Topic :: Controls'
                   ],
      py_modules=["ca", "caError", "cadefs","_ca_kek","_ca_fnal","CaChannel","printfn"],
      ext_modules=[Extension("_ca",[CA_SOURCE],
                             depends=["setup.py"],
                             include_dirs=tk_include_dir+[
                                           os.path.join(EPICSBASE,"include"),
                                           os.path.join(EPICSBASE,"include/os",UNAME),
                                           os.path.join(EPICSBASE,"include/os"),
					   os.path.join("/usr/X11R6","include")],
                             define_macros=[("PYCA_VERSION","\"%s\""%rev[11:-1]),
                                            ("PYCA_HG_RELEASE","\"%s\""%release),
                                            ("WITH_THREAD", None),
                                            ("WITH_TK", WITH_TK),
                                            ("UNIX", None),
                                            (UNAME, None)],
                             undef_macros="",
                             libraries=libraries,
                             library_dirs=[os.path.join(EPICSBASE,"lib",HOSTARCH),
                                           os.path.join(TKLIB,""),
                                           os.path.join(TCLLIB,""),
                                           ],
                             extra_compile_args=["-O"], # Can we set it to -O1 ?
                             runtime_library_dirs=[os.path.join(EPICSBASE,"lib",HOSTARCH),],
                             ),
                   ],
      )


setup(name="cas",
      version=rev[11:-1],
      author="Tatsuro Nakamur, KEK, JAPAN",
      author_email = "Tatsuro.nakamura@kek.jp",
      description="EPICS CA library interface module",
      long_description="""
      Simple EPICS CA library interface module (KEK,Japan)
      """,
      url="http://www-acc.kek.jp/EPICS_Gr/products.html",
      download_url="http://www-acc.kek.jp/EPICS_Gr/products.html",
      classifiers=['Programming Language :: Python :: 2.7',
                   'Topic :: Scientific/Engineering :: Interface Engine/Protocol Translator',
                   #'Topic :: EPICS CA',
                   #'Topic :: Controls'
                   ],
      package_dir={"":"cas"},
      py_modules=["cas","xca"],
      )
