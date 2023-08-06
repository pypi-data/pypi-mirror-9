#!/usr/bin/python
# -*- coding: shift_jis -*-

from Tkinter import *
import ca,thread
import time

class ChLabel(LabelFrame):
    def __init__(self, master, chname, width=None):
        LabelFrame.__init__(self, master,text=chname)
        
        self.label=Label(self)
        self.label.pack()
        self.var=DoubleVar()
        self.label.configure(textvariable=self.var)
        self.configure(width=width)
        self.init(chname)

    def init(self, chname):
        self.dirty=-1        
        self.monitor_active=0
        self.chname=chname
        #self.ca_init()

    def ca_init(self, *args,**env):
        self.ch=ca.channel(self.chname)
        self.ca_update_lock=thread.allocate()
        self.ch.wait_conn()
            
        self.ch.get_info()
        while not self.ch.isConnected():
            print ".",
            self.ch.pend_event(1.0)
        if self.ch.val:
            s="%f"%self.ch.val
            self.dirty=1
        else:
            s="CA readback"
            self.dirty=0
        self.monitor_active=0
#        self.start_monitor()

    def start_monitor(self):
        if self.monitor_active:
            print self.ch.name," is already monitored"
            return 
            #self.ch.clear_monitor()
        self.monitor_active=1
        thread.start_new_thread(self.callback_tk,())
        self.ch.monitor(self.callback_ca)
        self.ch.flush()

    def callback_ca(self,val=None):
        self.ch.update_val(val)
        self.ca_update_lock.release()

    def callback_tk(self):
        while self.monitor_active:
            self.ca_update_lock.acquire()
            #self.update_var()
            if self.ch.val:
                self.var.set(self.ch.val)
        thread.exit_thread()

    def update_var(self,val=None):
        if self.ch.val:
            self.var.set(self.ch.val)

class App(Frame):
    def init(self):
        self.master.title("CA monitor test")
        f=LabelFrame(self, text = 'ChLabel test', labelanchor = NW)
        f.pack()

        chname="SUM_GET_RFG_NUM"
        chname="jane"
        cl1=ChLabel(f, chname, width=400)
        cl1.pack(side=TOP, fill=X, anchor=NW)
        cl1.ca_init()
        cl1.start_monitor()

        chname="SUM_SET_RFG_NUM"
        chname="janet"
        cl2=ChLabel(f, chname, width=400)
        cl2.pack(side=TOP, fill=X, anchor=NW)
        cl2.ca_init()
        cl2.start_monitor()

        chname="SUM_SET_RFG_NUM"
        chname="fred"
        cl3=ChLabel(f, chname, width=400)
        cl3.pack(side=TOP, fill=X, anchor=NW)
        cl3.ca_init()
        cl3.start_monitor()

        chname="SUM_SET_RFG_NUM"
        chname="freddy"
        cl4=ChLabel(f, chname, width=400)
        cl4.pack(side=TOP, fill=X, anchor=NW)
        cl4.ca_init()
        cl4.start_monitor()
        
    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.init()
        self.pack()

def main():
    app = App()
    app.mainloop()

if __name__ == "__main__":
    main()

# end.
