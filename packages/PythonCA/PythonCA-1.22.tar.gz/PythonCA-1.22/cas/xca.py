#
# monitor status
#                                      self.mon_state  self._evid
#    init                           -->      0           None
#    start_monitor                  -->      1           None
#    connected --> ca monitor       -->      1           evid
#    1st callback                   -->      2           evid
#    stop_monitor                   -->      0           evid
#    connected --> ca clear_monitor -->      0           None
#
# calltype and cb in addcb / cb in addccb
#    0 : when val,conn_state changed, cb()
#    1 : when val changed,            cb(valstat)
#    2 : when val,conn_state changed, cb(ch)      : default
#   addccb : when conn_state changed, cb(ch)
#

import time
import ca # note that cas.py and xca.py assume _ca_kek.py in ca.py

class xcaError(ca.caError) :
    "Exceptions in xca"
class XCA_GETTIMEOUT(xcaError) :
    "Timeout on waiting get completion"
class XCA_NOTCONN(xcaError) :
    "Disconnected channel"

caTIMEOUT   = 10.0
caPOLLINT   = 0.02
EPICS_TS_EPOCH = ca.TS2UTC(0)
pend_io     = ca.pend_io
pend_event  = ca.pend_event
flush_io    = ca.flush_io
_xca_dict = {}

def _xca_int(x) :
    if type(x)==type('') : return int(float(x))
    return int(x)

# DBF type --> STRING, INT,   FLOAT,  ENUM,    CHAR,    LONG,  DOUBLE
_xca_typeconv = [str,_xca_int,float,_xca_int,_xca_int,_xca_int,float]

def wait_get(chlist=None,timeout=None,report=0) :
    if chlist is None : chlist = _xca_dict.values()
    if timeout is None : timeout = caTIMEOUT
    notyet = []
    for ch in chlist :
        timeout = ch.wait_get(timeout=timeout,report=1)
        if timeout is None :
            notyet.append(ch)
            timeout = 0.0
    if notyet :
        if report : return notyet  #<-- wait timeout
        else      : raise XCA_GETTIMEOUT(notyet[0].name)
    return timeout                 #<-- wait OK

def open(name) :
    ch = _xca_dict.get(name)
    if ch is None :
        _xca_dict[name] = ch = channel(name)
    return ch

class channel(ca.channel) :
    def __init__(self,name,cb=None) :
        ca.channel.__init__(self,name,cb=self._conn_cb)
        self._init_cb = cb
        self.mon_state = 0      ###(0:off, 1:on, 2:on & 1st cb done)
        self.mon_valstat = None ###(valstat or None(not connected))
        self._evid = None
        self._cblist = []
        self._ccblist = []
        self.cbtype = None      ###('conn' or 'mon'; valid only in cb)
        self.value = None       ###(val or None(not connected) for mon,get)
        self.get_state = 0      ###(0:done, 1:wait conn, 2:wait cb)
        self.get_valstat = None ###(valstat or None(not yet done))
        self._connlist = []     ### to do list when channel is connected
    def _conn_cb(self) :
        if self._init_cb : self._init_cb()
        self.update_info()
        if self.conn_state==2 :
            if self.mon_state!=0 :
                if self._evid is None :
                    self.monitor(self._mon_cb)
                    self._evid = self.evid[-1]
            else :
                if self._evid :
                    self.clear_monitor(self._evid)
                    self._evid = None
            if self.get_state==1 :
                self.get_state = 2
                self.get(self._get_cb)
            if self._connlist :
                t = time.time()
                for f,a,k,e in self._connlist :
                    if t<e : apply(f,a,k)
                self._connlist[:] = []
        else :
            self.mon_valstat = None
            self.value = None
        for cb in self._ccblist : cb(self)
        if self.mon_state :
            self.cbtype = 'conn'
            for cb,calltype in self._cblist :
                if   calltype==0 : cb()
                elif calltype==1 : pass
                else             : cb(self)
    def addccb(self,cb) :
        self._ccblist.append(cb)
        self.cbtype = 'conn'
        cb(self)
    def delccb(self,cb) :
        self._ccblist.remove(cb)
    def start_monitor(self) :
        if self.mon_state!=0 : return
        self.mon_state = 1
        if self.conn_state==2 and not self._evid :
            self.monitor(self._mon_cb)
            self._evid = self.evid[-1]
    def stop_monitor(self) :
        if self.mon_state==0 : return
        self.mon_state = 0
        if self.conn_state==2 and self._evid :
            self.clear_monitor(self._evid)
            self._evid = None
    def _mon_cb(self,valstat) :
        self.mon_valstat = valstat
        self.update_val(valstat)
        self.value = self.val
        if self.mon_state==1 : self.mon_state = 2
        self.cbtype = 'mon'
        for cb,calltype in self._cblist :
            if   calltype==0 : cb()
            elif calltype==1 : cb(self.mon_valstat)
            else             : cb(self)
    def addcb(self,cb,start=0,calltype=2) :
        self._cblist.append((cb,calltype))
        if start : self.start_monitor()
        if   calltype==0 : self.cbtype = 'conn'; cb()
        elif calltype==1 : pass
        else             : self.cbtype = 'conn'; cb(self)
        if self.conn_state==2 and self.mon_state==2 :
            self.cbtype = 'mon'
            if   calltype==0 : cb()
            elif calltype==1 : cb(self.mon_valstat)
            else             : cb(self)
    def delcb(self,cb,stop=0) :
        i = 0
        for c,ct in self._cblist :
            if c==cb :
                del self._cblist[i]
                break
            i = i+1
        if stop and len(self._cblist)==0 : self.stop_monitor()
    def _get_cb(self,valstat) :
        self.get_valstat = valstat
        self.update_val(valstat)
        self.value = self.val
        self.get_state = 0
    def get_nowait(self,report=0) :
        if self.get_state : return self
        self.get_valstat = None
        if self.conn_state<=0 :
            self.get_state = 1
        elif self.conn_state==2 :
            self.get_state = 2
            self.get(self._get_cb)
        else :
            if report : return None
            else      : raise XCA_NOTCONN(self.name)
        return self
    def wait_get(self,timeout=None,report=0) :
        if timeout is None : timeout = caTIMEOUT
        while self.get_state!=0 :
            if timeout<=0.0 :
                if report : return None  #<-- wait timeout
                else      : raise XCA_GETTIMEOUT(self.name)
            pend_event(caPOLLINT)
            timeout = timeout-caPOLLINT
        return timeout                   #<-- wait OK
    def get_wait(self,timeout=None,report=0) :
        rc = self.get_nowait(report=report)
        if rc is None : return None
        self.wait_get(timeout=timeout,report=report)
        if self.get_valstat : return self.get_valstat[0]
        else                : return None
    def _xput(self,*args,**kw) :
        apply(self.put, tuple(map(self.typeconv,args)), kw)
    def xput(self,*args,**kw) : #<-- kw : cb=None,timeout=None
        if len(args)==1 and type(args[0]) in (type(()),type([])) :
            args = tuple(args[0])
        kw = kw.copy()
        timeout = kw.get('timeout')
        if kw.has_key('timeout') : del kw['timeout']
        self.update_info()
        if   self.conn_state==2 :
            apply(self._xput,args,kw)
        elif self.conn_state==0 :
            if timeout is None : timeout = caTIMEOUT
            self._connlist.append((self._xput,args,kw,time.time()+timeout))
        else :
            raise XCA_NOTCONN(self.name)
    def __getattr__(self,attr) :
        if attr=='uts' :
            if self.ts is None : return None
            return ca.TS2UTC(self.ts)
        elif attr=='typeconv' :
            if self.field_type is None : return None
            return _xca_typeconv[self.field_type]
        raise AttributeError(attr)

### obsolete definition ###

create_channel = open
