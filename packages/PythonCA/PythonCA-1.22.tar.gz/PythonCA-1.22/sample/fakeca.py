
import random,thread,time

class channel:
    def __init__(self,name):
        self.name=name
        self.ts=time.time()
        self.sevr=0
        self.status=0
        self.val=random.random()
        self.active=False
        self.cb=None

    def get(self):
        self.val=random.random()
        self.ts=time.time()

    def put(self,val):
        pass

    def flush(self):
        pass
    def wait_conn(self):
        pass

    def monitor(self,callback):
        self.cb=callback
        self.active=True
        thread.start_new(self.mainloop,())

    def mainloop(self):
        import time,random
        #print "main loop"
        while self.active:
            try:
                self.cb((random.random(),time.time()))
            except:
                self.active=False
                print "exit thread"
                thread.exit()
            time.sleep(0.01)
        thread.exit_thread()

    def clear_monitor(self):
        self.active=False

    def update_val(self, vals):
        try:
            self.val=vals[0]
            self.ts =vals[1]
        except:
            pass

import time

def TS2Ascii(ts):
    return time.ctime(ts)

def TS2time(ts):
    return time.localtime(ts)

def TS2UTC(ts):
    return ts

