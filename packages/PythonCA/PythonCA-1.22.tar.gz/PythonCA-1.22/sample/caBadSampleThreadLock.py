import time
from caBadSampleChannels import mgpslist 
import ca,sys,thread

class newchannel:
    def __init__(self, name) :
        self.ch=ca.channel(name,self.conn_cb, noflush=True)
        self.lock=thread.allocate_lock()
        self.lock.acquire()
        #thread.start_new_thread(self.wait_lock,()) # you cannot start hread here.

    def wait_lock(self):
        while 1:
            self.lock.acquire()
            self.ch.update_info()
            print ".",
            sys.stdout.flush()

    def conn_cb(self,):
        try:
            self.lock.release()
        except thread.error:
            pass

    def mon_cb(self,vals):
        self.ch.update_val(vals)
        self.conn_cb()

    def start_monitor(self):
        self.ch.monitor(self.mon_cb)
        self.ch.flush()

def test():

    chlist = []
    proplist=('ALARM','SHREG','STATE','REQSTAT','IRB','IMON')
    cnt=0

    print 'Step 1'
    for chname in ("%s:%s"%(fullname, prop) for prop in proplist 
                   for fullname in mgpslist ):
        cnt +=1
        ch = newchannel(chname)
        chlist.append(ch)
    for chname in ("fred","jane","freddy","janet"):
        cnt +=1
        ch = newchannel(chname)
        chlist.append(ch)
    ca.flush()
    print "waiting for connection "
    chlist[-1].ch.wait_conn()
    print "connected"
    for ch in chlist:
        thread.start_new_thread(ch.wait_lock,())
        print "start new thread for",ch.ch.name, ch.ch.get_info()
    for ch in chlist:
        ch.start_monitor()
    print 'Step 2'
    ca.pend_event(10)
    print 'wait key input'
    raw_input()
    print 'End'

def genRec(chname):
    print "record(ai, \"%s\"){}"%chname

def genDB():
    chlist = []

    for fullname in mgpslist :
        for prop in ('ALARM','SHREG','STATE','REQSTAT','IRB','IMON') :
            chname = fullname+':'+prop
            ch = genRec(chname)
            #chlist.append(ch)

if __name__ == "__main__":
    test()
