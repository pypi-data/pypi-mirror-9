#!/bin/env python
"""
Simple EPICS monitor callback example
"""
import ca

class myCh(ca.channel):
    def __init__(self,name):
        ca.channel.__init__(self,name)
        self.jane=ca.channel("jane")
        
    def cb(self,valstat):
        self.update_val(valstat)
        self.jane.get()
        self.jane.flush() # you shoud not call pend_io/pend_event in callback.
        print ca.TS2Ascii(valstat[3]), self.name, valstat[:3]," jane:",(self.jane.val,self.jane.sevr,self.jane.status)

def test():
    ch=myCh("fred")
    try:
        ch.wait_conn()
        ch.jane.wait_conn()
        ch.jane.get()
        ch.jane.flush()
        try:
            ch.monitor(ch.cb)
            ca.pend_event(0)
        except:
            raise
    except:
        print "channel not connected"

if __name__ =="__main__":
    test()
    
