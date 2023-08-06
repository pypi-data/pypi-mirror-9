#!/usr/local/bin/pythonw
# FILE: ca_test.py
# import EPICS -CA and Tk libraries
#
import ca
from Tkinter import *
import thread
import Queue

import os

if not (os.environ.has_key("DISPLAY") and os.environ["DISPLAY"]):
    os.environ["DISPLAY"]=":0"
    
tkroot=Tk()
tkroot.withdraw()

import os,time,thread

def ca_main_loop():
    print "ca_main:",
    time.sleep(10.0)
    while 1:
        ca.pend_event(0.01)
        time.sleep(1.0)

import Tkinter   
tkroot=Tkinter.Tk()
tkroot.withdraw()
fdset=[]

TkQ=Queue.Queue()

def fd_register(arg, fd, cond):
    global tkroot,fdset
    #print "fd_register",fd, cond, arg
    def ca_poll(fd, arg,tmo=arg,**args):
        global fdset
        #print "ca_pend", fd, arg, tmo, args,
        if fdset.count(fd):
            ca.poll()
        #print "fisnished"
    if cond:
        fdset.append(fd)
        tkroot.createfilehandler(fd, READABLE | EXCEPTION , ca_poll)
    else:
        tkroot.deletefilehandler(fd)
        fdset.remove(fd)

class Simple(Frame):
    def __init__(self,name,master=None,*cnf):
        Frame.__init__(self,master)
        self.pack(expand=1,fill='both')
        self.ch=ca.channel(name);
        self.ch.wait_conn()
        self.ch.get();self.ch.pend_event(1)
        if self.ch.val:
            s="%f"%self.ch.val
            self.dirty=1
        else:
            s="CA readback"
            self.dirty=0
        print self.ch.val
        self.var=DoubleVar()
        l=Label(self,text=s)
        l.pack()
        s=Scale(self,orient="horizontal",label=name)
        s.pack(expand=1,fill='x')
        l.configure(textvariable=self.var)
        s.configure(variable=self.var)
        if self.ch.val:
            self.var.set(self.ch.val)
        b=Button(self,command=self.quit,text='Quit')
        b.pack()
        sb=Button(self,command=self.start_monitor,text='Start')
        sb.pack()
        self.s=s
        self.b=b
        self.sb=sb
        self.l=l
        #self.s.config(command=self.scale_change)
        self.ch.pend_event()
        self.monitor_active=0
        
    def quit(self):
        print "shutdown ca", 
        ca.shutdown()
        print "Now TK"
        self.l.quit()
        
    def start_monitor(self):
        if self.monitor_active:
            print self.ch.name," is already monitored"
            return 
            #self.ch.clear_monitor()
        self.ch.monitor(self.update_ch)
        self.ch.flush()
        self.monitor_active=1
        print "activate monitor for ",self.ch.name
        #self.after_idle(fmgr.do_one_event)
        self.idle()
        
    def idle(self):
        global TkQ
        self.l.after(200,self.idle)
        try:
            while not TkQ.empty():
                e=TkQ.get_nowait()
                e()
        except Queue.Full:
            pass
        except Queue.Empty:
            pass

    def scale_change(self,arg):
        v=self.s.get()
        if( v <> self.ch.val):
            self.put(v)
            self.ch.poll(0.0005)

    def update_ch(self,val):
        global TkQ
        self.ch.update_val(val)
        TkQ.put(self.update_var)
        
    def update_var(self,val=None):
        ca.poll()
        if self.ch.val:
            self.var.set(self.ch.val)

    def update_scale(self,val=None):
        print "update_scale,",
        time.sleep(0.001)
        if self.ch.val:
            self.s.set(self.ch.val*25+50)


if(__name__ == "__main__"):
    # execute the following lines if loaded as main program.
    #from fd_reg_test import *
    #ca.add_fd_registration(fd_register,0.01)
    ca.add_fd_registration(fd_register,0.1)
    #    Simple("fred",master=Tk()).mainloop()
    #    Simple("FFTB:WS2",master=Tk())
    #    Simple("FFTB:WS1",master=Toplevel()).mainloop()
    s=Simple("fred",master=Toplevel())
    s.pack()
    #Simple("fred",master=Toplevel()).pack()
    Simple("freddy",master=Toplevel()).pack()
    Simple("janet",master=Toplevel()).pack()
    Simple("jane",master=Toplevel()).pack()
    #Simple("jane",master=Toplevel()).pack()
    #Simple("jane",master=Toplevel()).pack()
    #s.after_idle(fmgr.do_one_event)
    ca.flush_io()
    #thread.start_new_thread(ca_main_loop,())
    ca.flush_io()
    s.mainloop()
