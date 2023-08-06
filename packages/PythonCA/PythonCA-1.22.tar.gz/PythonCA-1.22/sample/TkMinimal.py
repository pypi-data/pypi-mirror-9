#!/bin/env python
import ca
from caAlarmSeverity import *

from Tkinter import *
import types,time

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
        self.init_ca(ch)
        LabelFrame.__init__(self, parent, text=self.ch.name, *args,**env);
        self.var=StringVar()
        
        self.varEntry=LabeledEntry(self,   "Value:",textvariable=self.var)
        self.varEntry.pack(side=TOP,fill=X)

    def __del__(self):
        self.clear_monitor()
        LabelFrame.__del__(self)

    def Update(self):
        if self.ch.val:
            self.var.set(self.ch.val)

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
