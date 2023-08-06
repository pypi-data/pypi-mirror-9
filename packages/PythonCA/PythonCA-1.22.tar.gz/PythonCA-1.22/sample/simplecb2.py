#!/bin/env python
"""
Simple EPICS monitor callback example with using connection handler
"""
import ca
from ca import pend_io,pend_event, ch_state, Get,Put, Monitor, ClearMonitor

class myCh(ca.channel):
    def __init__(self, name):
        ca.channel.__init__(self, name, cb=self.conn_handler)
        
    def conn_handler(self, *args,**env):
        self.update_info()
        cs=self.conn_state
        if cs == ch_state.cs_conn:
            print self.name, "is connected"
            if not self.evid:
                self.monitor(self.cb)
                print "start monitor",self.evid
                self.flush()
        elif cs == ch_state.cs_never_conn:
            print self.name, " never connected"
        elif cs == ch_state.cs_prev_conn:
            print self.name, " disconnected"
        elif cs == ch_state.cs_close:
            print self.name, " closed"
        else:
            print self.name, "unexpected connection state",cs

    def cb(self,valstat):
        self.update_val(valstat)
        print ca.TS2Ascii(valstat[3]), self.name, valstat[:3]

def test():
    ch=myCh("fred")
    ch.flush()
    try:
        ca.pend_event(0)
    except:
        print "channel not connected"

if __name__ =="__main__":
    test()
