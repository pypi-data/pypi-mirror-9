import time
from caBadSampleChannels import mgpslist 
import ca,sys,thread,random

class newchannel:
    def __init__(self, name) :
        self.ch=ca.channel(name,self.conn_cb, noflush=True)
        self.cnt=0

    def count(self):
        self.cnt +=1

    def conn_cb(self,):
        self.ch.update_info() # can crash the process.
        self.count() # it is OK to call function with no access to IO(?)
        print ".", # cause  crash on python2.6

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
    print "waiting for connection "
    chlist[-1].ch.wait_conn()

    for ch in chlist:
        print ch.ch.name, ch.ch.get_info()
        ch.ch.put(random.random())
    print 'Step 2'
    ca.pend_event(3)


    print 'Step 3'
    for ch in chlist:
        ch.ch.get()
    ca.pend_event(3)
    for ch in chlist:
        print ch.ch.name, ch.ch.val
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
