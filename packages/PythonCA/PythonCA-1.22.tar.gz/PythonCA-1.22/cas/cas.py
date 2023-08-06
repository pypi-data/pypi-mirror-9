import ca
import xca

capollint = 0.02
capollmax = 500

class casError(ca.caError) :
    "Exceptions in cas"
class CAS_CONNTIMEOUT(casError) :
    "Timeout on waiting caopen completion"
class CAS_GETTIMEOUT(casError) :
    "Timeout on waiting caget completion"

def _Error(err,msg,erropt) :
    if   erropt=='pass'  : return
    elif erropt=='print' : print (str(err)+': '+msg)
    else                 : raise err(msg)

def _pair2lists(pl) :
    a,b = [],[]
    for x,y in pl :
        a.append(x)
        b.append(y)
    return a,b

def _capoll(n) :
    "EPICS CA; pend_event short period"
    if n[0]==0 : return 1
    ca.pend_event(capollint)
    n[0] = n[0]-1
    return 0

##### caopen #####

def _connwait(chl,erropt,maxpoll) :
    if chl is None : return
    if isinstance(chl,ca.channel) :
        while(chl.conn_state!=2) :
            if (_capoll(maxpoll)) :
                _Error(CAS_CONNTIMEOUT,chl.name,erropt)
                chl.NC = 1
                return
        if hasattr(chl,'NC') : del chl.NC
    else :
        for ch in chl :
            _connwait(ch,erropt,maxpoll)

def caopen(arg,sync=1,erropt='raise'):
    "EPICS CA; open"
    if arg is None : return None
    if isinstance(arg,ca.channel) :
        result = arg
    elif type(arg)==type('') :
        result = xca.open(arg)
    else :
        result = []
        for x in arg :
            ch = caopen(x,0,erropt)
            result.append(ch)
    ca.flush_io()
    if sync :
        maxpoll = [capollmax]
        _connwait(result,erropt,maxpoll)
    return result

##### caget #####

def _caget_async(chl):
    "EPICS CA; async get"
    if chl is None : return
    if isinstance(chl,ca.channel) :
        if hasattr(chl,'NC') : return
        chl.status = None
        chl.get()
    else :
        for x in chl :
            _caget_async(x)

def _caval(chl,erropt,maxpoll=None):
    "EPICS CA; wait caget completion and make value list"
    if maxpoll is None : maxpoll = [capollmax]
    if chl is None : return None
    if isinstance(chl,ca.channel) :
        if hasattr(chl,'NC') : return None
        while(chl.status==None) :
            if (_capoll(maxpoll)) :
                _Error(CAS_GETTIMEOUT,chl.name,erropt)
                return None
        return chl.val
    else :
        vlist = []
        for x in chl :
            vlist.append(_caval(x,erropt,maxpoll))
        return vlist

def _cawait(chl,erropt,maxpoll=None):
    "EPICS CA; wait caget completion"
    if maxpoll is None : maxpoll = [capollmax]
    if chl is None : return
    if isinstance(chl,ca.channel) :
        if hasattr(chl,'NC') : return
        while(chl.status==None) :
            if (_capoll(maxpoll)) :
                _Error(CAS_GETTIMEOUT,chl.name,erropt)
    else :
        for x in chl :
            _cawait(x,erropt,maxpoll)

def caget(arg,sync=2,erropt='raise') :
    "EPICS CA; get (sync=0(nowait),1(wait),2(wait and return value))"
    chl = caopen(arg,erropt=erropt)
    _caget_async(chl)
    ca.flush_io()
    if   sync==0 : return chl
    elif sync==1 : _cawait(chl,erropt); return chl
    else         : return _caval(chl,erropt)

##### caput #####

def _caput_const(chl,v):
    "EPICS CA; async put a constant value"
    if chl is None : return
    if isinstance(chl,ca.channel) :
        if hasattr(chl,'NC') : return
        chl.put(v)
    else :
        for x in chl :
            _caput_const(x,v)

def _caput_list(chl,vl):
    "EPICS CA; async put with value list"
    if chl is None : return
    if isinstance(chl,ca.channel) :
        if hasattr(chl,'NC') : return
        if type(vl) in (type([]),type(())) :  ## 2001.12.13 bug fixed
            apply(chl.put,vl)                 ## 2001.12.7  waveform data
        else :                                ## 2001.12.13
            chl.put(vl)
    else :
        map(_caput_list,chl,vl)

def _Tcaput(arg,val=(),flush=1,erropt='raise') :
    "EPICS CA; put"
    islist = type(val) in (type([]),type(()))
    if islist and len(val)==0 : arg,val = _pair2lists(arg)
    chl = caopen(arg,erropt=erropt)
    if islist : _caput_list(chl,val)
    else      : _caput_const(chl,val)
    if flush : ca.pend_event(capollint)

caput = _Tcaput

def _Dcaput(arg,val=(),flush=1,erropt='raise') :
    "Dummy caput for test"
    islist = type(val) in (type([]),type(()))
    if islist and len(val)==0 : arg,val = _pair2lists(arg)
    if arg is None :
        print ("--caput None")
    elif isinstance(arg,ca.channel) :
        print ("--caput <ca>",val)
    elif type(arg)==type('') :
        print ("--caput",arg,val)
    else :
        if islist :
            i=0
            for item in arg : _Dcaput(item,val[i],0); i=i+1
        else :
            for item in arg : _Dcaput(item,val,0)
    if flush : print ("-----pend_event")

##### camonitor #####

class _callbackobj :
    def __init__(self,ch,func,functype) :
        self.ch = ch
        self.func = func
        self.functype = functype
    def callback(self,valstat) :
        if self.functype==1 : self.func(self.ch,valstat)

def _camon(ch,func,functype=0) :
    if hasattr(ch,'NC') : return None
    if type(func)==type('') : func = getattr(ch,func)
    if functype :
        try                   : cblist = ch.CBLIST
        except AttributeError : cblist = ch.CBLIST = []
        cb = _callbackobj(ch,func,functype)
        cblist.append(cb)
        ch.monitor(cb.callback)
        cb.evid = ch.evid[-1]
    else :
        ch.monitor(func)
    return ch.evid[-1]

def _camon_const(chl,func,functype) :
    if chl is None : return None
    if isinstance(chl,ca.channel) :
        return _camon(chl,func,functype)
    else :
        result=[]
        for ch in chl :
            result.append(_camon_const(ch,func,functype))
        return result

def _camon_list(chl,funcl,functype) :
    if chl is None : return None
    if isinstance(chl,ca.channel) :
        return _camon(chl,funcl,functype)
    else :
        return map(_camon_list,chl,funcl,(functype,)*len(chl))

def camonitor(arg,func=(),functype=0,flush=1,erropt='raise') :
    islist = type(func) in (type([]),type(()))
    if islist and len(func)==0 : arg,func = _pair2lists(arg)
    chl = caopen(arg,erropt=erropt)
    if islist : result = _camon_list(chl,func,functype)
    else      : result = _camon_const(chl,func,functype)
    if flush : ca.pend_event(capollint)
    return result

##### caclear_monitor #####

def caclear_monitor(ch,evid,flush=1) :
    if type(ch)==type('') : ch = xca.open(ch)
    ch.clear_monitor(evid)
    if flush : ca.flush_io()

##### sleep #####

def sleep(delay) : ca.pend_event(delay)
