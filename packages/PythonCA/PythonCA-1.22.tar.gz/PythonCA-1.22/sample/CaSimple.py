#!/usr/local/bin/python
# FILE: ca_test.py
# import EPICS -CA and Tk libraries
#

import ca

from Tkinter import *
import thread,threading,gc,signal
import Queue
import time
import random
import traceback

import os

if not (os.environ.has_key("DISPLAY") and os.environ["DISPLAY"]):
    os.environ["DISPLAY"]=":0"
    
import os,time,gc
class CB:
   def __init__(self,ch,id,lk):
       lk.acquire()
       self.ch=ch
       self.id=id
       lk.release()
       
   def __call__(self,vals,*args,**env):
       lk.acquire()
       print time.ctime(time.time()), self, self.ch.name,self.id,vals
       lk.release()
       pass

class Simple(Frame):
    import Tkinter   
    __tkroot=Tkinter.Tk()
    __tkroot.withdraw()

    def __init__(self,name,master=None,*cnf):
        Frame.__init__(self,master)
        self.pack(expand=1,fill='both')
        self.ch=ca.channel(name);
        self.ch.wait_conn(dt=0.1,wait=10)
        self.ch.get();self.ch.pend_event(1)
        if self.ch.val:
            s="%f"%self.ch.val
            self.dirty=1
        else:
            s="CA readback"
            self.dirty=0
        print name, self.ch.val
        self.var=DoubleVar()
        s=Scale(self,orient="horizontal",label=name,resolution=0.1)
        s["from"]=-10.0;s["to"]=10.0;s["length"]=100;
        s.pack(expand=1,fill='x')
        s.configure(variable=self.var)

        l=Label(self,text=s)
        l.pack()
        l.configure(textvariable=self.var)

        if self.ch.val:
            self.var.set(self.ch.val)
        sb=Button(self,command=self.start_monitor,text='Start')
        cb=Button(self,command=self.master.destroy,text="Close")
        qb=Button(self,command=self.quit,text="Quit")
        sb.pack(side="left")
        cb.pack(side="left")
        qb.pack(side="left")
        self.s=s
        self.sb=sb
        self.l=l
        #self.s.config(command=self.scale_change)
        self.ch.flush()
        self.monitor_active=0

    def quit(self):
        try:
            print "Shutdown TK"
            self.l.tk.quit()
        finally:
            print "Shutdown thread ","%x"%thread.get_ident()
            thread.exit()

    def start_monitor(self):
        if self.monitor_active:
            print self.ch.name," is already monitored"
            return 
            #self.ch.clear_monitor()
        self.ch.monitor(self.update_var)
        self.ch.flush()
        self.monitor_active=1
        
    def idle(self):
        self.l.after(200,self.idle)
        self.update_var()

    def scale_change(self,arg):
        v=self.s.get()
        if( v <> self.ch.val):
            self.put(v)
            self.ch.poll()

    def update_var(self,val=None):
        self.ch.update_val(val)
        if self.ch.val:
            self.var.set(self.ch.val)
        
    def update_scale(self,val=None):
        if self.ch.val:
            self.s.set(self.ch.val*25+50)

sem1=threading.BoundedSemaphore(1,0)
sem2=threading.BoundedSemaphore(1,0)
sem3=threading.BoundedSemaphore(1,0)
sem1.acquire()
sem2.acquire()
sem3.acquire()

janetlk=threading.Lock()
janelk=threading.Lock()
fredlk=threading.Lock()
freddylk=threading.Lock()

def bah(i=0,ch=None,lk=None ):
    global janetlk, janelk, fredlk, freddylk
    global gt2s,sem1,sem2,sem3,janet
    v=-i
    cb=CB(ch,thread.get_ident(),lk)
    while 1:
        t2s=random.uniform(gt2s,2*gt2s)
        sem2.acquire()
        time.sleep(t2s)
        sem3.acquire()
        #v=-janet.val
        v=1
        try:
            try:
                if ch:
                    lk.acquire()
                    ch.put(v,cb=cb)
                    ch.flush()
                    lk.release()
            except ca.caError,msg:
                print "CaError",msg
                traceback.print_exc()        
                raise
            except:
                print "exception in bah", "%x"%thread.get_ident()
                traceback.print_exc()        
                thread.exit_thread()
        finally:
            sem2.release()
            time.sleep(t2s)
            sem3.release()
            time.sleep(t2s)
            
def gee(i=0,ch=None,lk=None):
    global gt2s,sem1,sem2,sem3,janet
    v=i
    cb=CB(ch,thread.get_ident(),lk)
    while 1:
        t2s=random.uniform(gt2s,2*gt2s)
        sem1.acquire()
        time.sleep(t2s)
        sem3.acquire()
        time.sleep(t2s)
        try:
            try:
                v=1
                if ch:
                    lk.acquire()
                    ch.put(v,cb=cb)
                    ch.flush()
                    lk.release()
            except ca.caError,msg:
                print "CaError",msg
                traceback.print_exc()        
                raise
            except:
                print "exception in gee", "%x"%thread.get_ident()
                traceback.print_exc()
                thread.exit_thread()
        finally:
            sem1.release()
            time.sleep(t2s)
            sem3.release()
            time.sleep(t2s)
            
def foo(i=0,ch=None,lk=None):
    global gt2s,sem1,sem2,sem3,janet
    v=i
    cb=CB(ch,thread.get_ident(),lk)
    while 1:
        t2s=random.uniform(gt2s,2*gt2s)
        time.sleep(t2s)
        sem1.acquire()
        time.sleep(t2s)
        sem2.acquire()
        try:
            try:
                v=1
                if ch:
                    lk.acquire()
                    ch.put(v,cb=cb)
                    ch.flush()
                    lk.release()
            except ca.caError,msg:
                print "CaError",msg
                traceback.print_exc()
                raise
            except:
                print "exception in foo", "%x"%thread.get_ident()
                traceback.print_exc()
                thread.exit_thread()
        finally:
            sem1.release()
            time.sleep(t2s)
            sem2.release()
            time.sleep(t2s)
        
def monitor():
    s=[]

    top=Toplevel()
    s.append(Simple("freddy",master=top))
    s[-1].pack()

    top=Toplevel()
    s.append(Simple("fred",master=top))
    s[-1].pack()
    
    top=Toplevel()
    s.append(Simple("jane",master=top))
    s[-1].pack()

    top=Toplevel()
    s.append(Simple("janet",master=top))
    s[-1].pack()
    
    [w.pack() for w in s]
    [w.start_monitor() for w in s]

    top.mainloop()
    
gc.set_debug(gc.DEBUG_STATS)

def main():
    global janetlk, janelk, fredlk, freddylk
    global gt2s,sem1,sem2,sem3,janet
    # execute the following lines if loaded as main program.

#    ca.Put("freddy.SCAN",0)
#    ca.Put("fred.SCAN",0)
#    ca.Put("jane.SCAN",0)
    ca.flush_io()

    jane=ca.channel("jane.PROC")
    jane.wait_conn()

    freddy=ca.channel("freddy.PROC")
    freddy.wait_conn()

    fred=ca.channel("fred.PROC")
    fred.wait_conn()

    janet=ca.channel("janet")
    janet.wait_conn()
    janet.autoUpdate()
    
    gt2s=0.01
    task=[]
    n=200

    gt2s=0.00001
    n=200

    task.append(thread.start_new(bah,(0,jane,janelk)))
    time.sleep(0.01)

    for i in range(1,n+1):
        print "creating %d-th threds"%i
        task.append(thread.start_new(foo,(10.*i/n,freddy,freddylk)))
        time.sleep(0.01)
        task.append(thread.start_new(gee,(i*10./n,fred,fredlk)))
        time.sleep(0.01)
    ca.flush_io(1)

    sem1.release()
    sem2.release()
    sem3.release()

    try:
        while 1:
            sem1.acquire()
            sem2.acquire()
            sem3.acquire()
            try:
                print time.ctime(time.time())
                gc.collect()
            finally:
                sem1.release()
                sem2.release()
                sem3.release()
                time.sleep(3)
    finally:
        ca.Put("freddy.SCAN",5)
        ca.Put("fred.SCAN",5)
        ca.Put("jane.SCAN",7)
        thread.exit()

if(__name__ == "__main__"):
    import gc
    gc.disable()
    main()
    gc.enable()
