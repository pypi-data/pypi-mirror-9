#!/bin/env python
from caAlarmSeverity import *
import ca
#import niseca as ca

from Tkinter import *
import types,time
from math import modf
import random,thread,time

class channel:
    def __init__(self,name):
        self.name=name
        self.ts=0
        self.sevr=0
        self.status=0
        self.val=random.random()
        self.active=False
        self.cb=None

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
        while self.active:
            r=random.random()
            t=time.time()
            try:
                self.cb((r,t))
            except:
                self.active=False
                thread.exit()
            time.sleep(0.1)
        thread.exit_thread()

    def clear_monitor(self):
        self.active=False
        thread.wait(self.thread)

    def update_val(self,vals):
        self.val=vals[0]
        self.ts=vals[1]

class LabeledEntry(Entry):
    def __init__(self, parent, text, *args, **env):
        self.label=LabelFrame(text=text)
        self.label.pack(side=LEFT,fill=X)
        Entry.__init__(self, self.label, *args,**env)
        Entry.pack(self, side=LEFT,fill=X)

    def pack(self, *args,**env):
        self.frame.pack(*args,**env)

class CaInfoWidget(LabelFrame):
    def init_ca(self, ch):
        if( type(ch) in types.StringTypes):
            self.ch=channel(ch)
            self.ch.wait_conn()
        elif isinstance(ch, channel):
            self.ch=ch
        else:
            raise "No Channel object  nor Channel name"
            
    def __init__(self, parent, ch, *args,**env):
        LabelFrame.__init__(self, parent, text=ch, *args,**env);

        self.init_ca(ch)

        self.var=StringVar()
        self.tsvar=StringVar()
#        self.nsecvar=IntVar()
        self.statusvar=StringVar()
        self.countvar=IntVar()
        self.counter=0

        self.varEntry=LabeledEntry(self,   "Value:",
                                   textvariable=self.var,
                                   width=30)
        self.tsEntry=LabeledEntry(self,    "   TS:",
                                  textvariable=self.tsvar,
                                  width=30)
#         self.nsecEntry=LabeledEntry(self,  "  nsec:",
#                                     textvariable=self.nsecvar)
        self.statusEntry=LabeledEntry(self,"Status:",
                                      textvariable=self.statusvar,
                                      width=30)
        self.statusEntry.configure(background="lightpink")

        self.counterEntry=LabeledEntry(self,"Counter:",
                                       textvariable=self.countvar,
                                       width=30)

        self.varEntry.pack(side=TOP,fill=X)
        self.tsEntry.pack(side=TOP,fill=X)
#        self.nsecEntry.pack(side=TOP,fill=X)
        self.statusEntry.pack(side=TOP,fill=X)
        self.counterEntry.pack(side=TOP,fill=X)

    def Update(self):
        if not self.ch.val:
            return
        self.var.set(self.ch.val)
        self.tsvar.set(time.ctime(self.ch.ts))
        self.statusEntry.configure(
            foreground=AlarmSeverity.Colors[self.ch.sevr])
        self.statusvar.set("%s / %s"%(
            AlarmSeverity.Strings[self.ch.sevr],
            AlarmStatus.Strings[self.ch.status]))
        self.counter +=1
        self.countvar.set(self.counter)
        
    def start_monitor(self):
        self.ch.monitor(callback=self.ca_callback)
        self.ch.flush()

    def clear_monitor(self):
        self.ch.clear_monitor()
        self.ch.flush()
            
    def ca_callback(self,vals):
        #print "callback",self.ch.name
        self.ch.update_val(vals)
        self.Update()

def test():
    tk=Tk()
    ci=CaInfoWidget(tk, "jane")
    ci.pack()
    ci.start_monitor()
    
    ci.mainloop()

if __name__ =="__main__":
    test()
