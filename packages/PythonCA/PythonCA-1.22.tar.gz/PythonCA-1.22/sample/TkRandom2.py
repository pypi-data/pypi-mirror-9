#!/bin/env python
from caAlarmSeverity import *
#import ca
import fakeca as ca

from Tkinter import *
import types,time
from math import modf
import random,thread,time

class LabeledEntry(Entry):
    def __init__(self, parent, text, *args, **env):
        self.label=LabelFrame(text=text)
        self.label.pack(side=LEFT,fill=X)
        Entry.__init__(self, self.label, *args,**env)
        Entry.pack(self, side=LEFT,fill=X)

    def pack(self, *args,**env):
        self.label.pack(*args,**env)

class CaInfoWidget(LabelFrame):
    def init_ca(self, ch):
        if( type(ch) in types.StringTypes):
            self.ch=ca.channel(ch)
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
        self.nsecvar=IntVar()
        self.statusvar=StringVar()
        self.varEntry=LabeledEntry(self,   "Value:",
                                   textvariable=self.var,
                                   width=30)
        self.tsEntry=LabeledEntry(self,    "   TS:",
                                  textvariable=self.tsvar,
                                  width=30)
        self.nsecEntry=LabeledEntry(self,  "  nsec:",
                                     textvariable=self.nsecvar)
        self.statusEntry=LabeledEntry(self,"Status:",
                                      textvariable=self.statusvar,
                                      width=30)
        self.statusEntry.configure(background="lightpink")

        self.countvar=IntVar()
        self.counter=0
        self.counterEntry=LabeledEntry(self,"Counter:",
                                       textvariable=self.countvar,
                                       width=30)
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
        self.countvar.set(self.counter)

        
    def start_monitor(self):
        self.ch.monitor(callback=self.ca_callback)
        self.ch.flush()

    def clear_monitor(self):
        self.ch.clear_monitor()
        self.ch.flush()
            
    def ca_callback(self,vals):
        self.ch.update_val(vals)
        self.counter +=1

    def bg(self):
        self.Update()
        self.after_idle(self.bg)

def test():
    tk=Tk()
    ci=CaInfoWidget(tk, "jane")
    ci.pack()
    ci.start_monitor()
    ci.after(1000,ci.bg)
    ci.mainloop()

if __name__ =="__main__":
    test()
