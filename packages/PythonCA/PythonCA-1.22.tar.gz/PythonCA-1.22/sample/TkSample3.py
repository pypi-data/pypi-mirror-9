#!/bin/env python
import thread
import ca
#import fakeca as ca
from caAlarmSeverity import *
import gc

from Tkinter import *
import types,time,thread

class LabeledEntry(Label):
    def __init__(self, parent, text, *args, **env):
        self.frame=Frame(parent)
        self.label=Label(self.frame,text=text)
        self.label.pack(side=LEFT,fill=X)
        Label.__init__(self, self.frame, *args,**env)
        Label.configure(self, relief=SUNKEN)
        Label.pack(self, side=LEFT,fill=X,expand=True)

    def pack(self, *args,**env):
        self.frame.pack(*args,**env)

    def replace(self,str):
        self.delete(0,len(self.get()))
        self.insert(0,str)

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
        self.tsvar=StringVar()
        self.nsecvar=StringVar()
        self.statusvar=StringVar()
        
        self.varEntry=LabeledEntry(self,   "Value:")#,textvariable=self.var)
        self.tsEntry=LabeledEntry(self,    "   TS:")#,textvariable=self.tsvar)
        self.nsecEntry=LabeledEntry(self,  " nsec:") #,textvariable=self.nsecvar)
        self.statusEntry=LabeledEntry(self,"status:")#,textvariable=self.statusvar)
        self.statusEntry.configure(background="lightpink")
        self.varEntry.pack(side=TOP,fill=X)
        self.tsEntry.pack(side=TOP,fill=X)
        self.nsecEntry.pack(side=TOP,fill=X)
        self.statusEntry.pack(side=TOP,fill=X)

    def Update(self):
        if not self.ch.val:
            return
        self.varEntry.configure(text="%20.7f"%self.ch.val)
        sec,subsec=divmod(self.ch.ts,1.0)
        tm=ca.TS2time(sec)
        self.tsEntry.configure(text="%s\n"%time.asctime(tm))
            #self.nsecvar.set("%06d"%(1e9*subsec))
        gc.collect()
            #print gc.get_count(),len(gc.get_objects())
            #self.nsecEntry.configure(text="%s,%s"%(gc.get_count(),len(gc.get_objects())))
        self.nsecEntry.configure(text="%02d.%09d"%(tm.tm_sec,int(1e9*subsec)))
        self.statusEntry.configure(text="%s/%s"%(AlarmSeverity.Strings[self.ch.sevr],AlarmStatus.Strings[self.ch.status]))
            ##self.statusvar.set("%s"%AlarmStatus.Strings[self.ch.status])
        self.statusEntry.configure(foreground=AlarmSeverity.Colors[self.ch.sevr])
        return

    def start_monitor(self):
        self.active=True
        self.ch.monitor(callback=self.ca_callback)
        self.after(100,self.tk_callback)
        self.ch.flush()

    def clear_monitor(self):
        self.active=False
        self.ch.clear_monitor()
        self.ch.flush()
            
    def ca_callback(self,vals):
        self.ch.update_val(vals)
        
    def tk_callback(self):
        if self.active:
            self.Update()
            self.after_idle(self.tk_callback)

def test():
    tk=Tk()
    ci=CaInfoWidget(tk, "jane")
    ci.pack()
    ci.start_monitor()
    root=Toplevel()
    ci=CaInfoWidget(root, "janet")
    ci.pack()
    ci.start_monitor()
    ci.mainloop()

if __name__ =="__main__":
    test()
