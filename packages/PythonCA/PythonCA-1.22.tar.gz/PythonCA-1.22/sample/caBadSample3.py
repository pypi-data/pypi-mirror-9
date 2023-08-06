import ca
import time,thread


def cb(self, valstat) :
    print "%08x"%thread.get_ident(), time.time(),self.name, valstat


jane = ca.channel('jane')
janet = ca.channel('janet')
fred =ca.channel("fred")
freddy =ca.channel("freddy")

ca.channel.myCB=cb

janet.wait_conn()

jane.monitor(jane.myCB)
janet.monitor(janet.myCB)
fred.monitor(fred.myCB)
freddy.monitor(freddy.myCB)

ca.flush_io()

import time
def foo():
    global lck
    while 1:
        lck.acquire()
        print "%08x"%thread.get_ident(),time.time()
        time.sleep(100e-6)
        lck.release()

lck=thread.allocate_lock()
lck.acquire()

thread.start_new_thread(foo,())

lck.release()
while 1:
    if(lck.acquire()):
        time.sleep(100e-6)
        lck.release()
