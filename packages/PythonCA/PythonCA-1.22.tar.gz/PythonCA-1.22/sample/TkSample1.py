#!/bin/env python
# -*- coding:utf-8 -*-
import ca
#import fakeca as ca
from caAlarmSeverity import *

from Tkinter import *
import types,time,thread
from math import modf

class LabeledEntry(Entry):
    def __init__(self, parent, text, *args, **env):
        self.frame=Frame(parent)
        self.label=Label(self.frame,text=text)
        self.label.pack(side=LEFT,fill=X)
        Entry.__init__(self, self.frame, *args,**env)
        Entry.pack(self, side=LEFT,fill=X)

    def pack(self, *args,**env):
        self.frame.pack(*args,**env)

class CaInfoWidget(LabelFrame):
    def init_ca(self, ch):
        if( type(ch) in types.StringTypes):
            self.ch=ca.channel(ch)
            self.ch.wait_conn()
        elif isinstance(ch, ca.channel):
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
        self.countvar=StringVar()
        self.counter=0
        self.ucounter=0

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
        
        self.counterEntry=LabeledEntry(self,"Counter:",
                                       textvariable=self.countvar,
                                       width=30)

        self.varEntry.pack(side=TOP,fill=X)
        self.tsEntry.pack(side=TOP,fill=X)
        self.nsecEntry.pack(side=TOP,fill=X)
        self.statusEntry.pack(side=TOP,fill=X)
        self.counterEntry.pack(side=TOP,fill=X)

    def Update(self):
        if not self.ch.val:
            return
        self.var.set(self.ch.val)
        self.tsvar.set(ca.TS2Ascii(self.ch.ts))
        self.statusEntry.configure(
            foreground=AlarmSeverity.Colors[self.ch.sevr])
        self.statusvar.set("%s / %s"%(
                AlarmSeverity.Strings[self.ch.sevr],
                AlarmStatus.Strings[self.ch.status]))
        self.countvar.set("%d/%d/%d"%(
                self.counter,self.ucounter,self.counter-self.ucounter))
        self.update()

    def start_monitor(self):
        self.ca_update_lock=thread.allocate()
        self.ch.monitor(callback=self.ca_callback)
        self.ca_update_lock.acquire(False)
        self.after(3, self.tk_callback )
        self.ch.flush()

    def clear_monitor(self):
        self.ch.clear_monitor()
        self.ch.flush()
        try:
            self.ca_update_lock.release()
        finally:
            del self.ca_update_lock
            
    def ca_callback(self,vals):
        self.ch.update_val(vals)
        self.counter +=1
        try:
            self.ca_update_lock.release()
        except thread.error:
            pass

    def tk_callback(self):
        self.ucounter +=1
        if self.ca_update_lock.acquire(True):
            self.Update()
            self.after_idle(self.tk_callback)

    def __del__(self):
        self.clear_monitor()
        del self.ch
        LabelFrame.__del__(self)

def test():
    tk=Tk()
    ci=CaInfoWidget(tk, "jane")
    ci.pack()
    ci.start_monitor()
    ci.mainloop()

if __name__ =="__main__":
    test()
