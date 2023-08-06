#!/usr/local/bin/python
# FILE: ca_test.py
# import EPICS -CA and Tk libraries
#

import ca

from Tkinter import *
import thread
import Queue
import time
import random

import os

if not (os.environ.has_key("DISPLAY") and os.environ["DISPLAY"]):
    os.environ["DISPLAY"]=":0"
    
tkroot=Tk()
tkroot.withdraw()

import os,time

class Simple(Frame):
    import Tkinter   
    __tkroot=Tkinter.Tk()
    __tkroot.withdraw()
    def __init__(self,name,master=None,*cnf):
        Frame.__init__(self,master)
        self.pack(expand=1,fill='both')
        self.ch=random.Random()
        self.ch.get=self.ch.random
        
        s="%f"%self.ch.get()
        self.dirty=1
        self.var=DoubleVar()
        s=Scale(self,orient="horizontal",label=name,resolution=0.1)
        s["from"]=-10.0;s["to"]=10.0;s["length"]=100;
        s.pack(expand=1,fill='x')
        s.configure(variable=self.var)

        l=Label(self,text=s)
        l.pack()
        l.configure(textvariable=self.var)

        self.var.set(self.ch.get())
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
        self.monitor_active=0
        
    def quit(self):
        try:
            print "Shutdown TK"
            self.l.master.tk.quit()
        finally:
            print "Shutdown thread ","%x"%thread.get_ident()
            thread.exit()

    def start_monitor(self):
        if self.monitor_active:
            return 
            #self.ch.clear_monitor()
        self.monitor_active=1
        self.idle()
        
    def idle(self):
        self.l.after(50,self.idle)
        self.update_var()

    def scale_change(self,arg):
        v=self.s.get()
        self.put(v)

    def update_ch(self,val):
        self.dirty=1
        
    def update_var(self,val=None):
        self.var.set(self.ch.get())
        
    def update_scale(self,val=None):
        self.s.set(self.ch.get()*25+50)

sem1=thread.allocate_lock()
sem2=thread.allocate_lock()
sem3=thread.allocate_lock()

def foo():
    random.random()
    try:
        while 1:
            sem1.acquire()
            sem2.acquire()
            print time.ctime(time.time()),"Hello, I'm Foo in %x"%thread.get_ident(), random.random(),sem1.locked(),sem2.locked(),sem3.locked()
            sem2.release()
            sem1.release()
            time.sleep(random.uniform(1.0,10.0))
    except:
        print "exception in foo"

def bah():
    ca.Get("jane")
    try:
        while 1:
            sem2.acquire()
            sem3.acquire()
            print time.ctime(time.time()),"Hi, I'm Bah in %x"%thread.get_ident(), random.random(),sem1.locked(),sem2.locked(),sem3.locked()
            sem3.release()
            sem2.release()
            time.sleep(random.uniform(1.0,10.0))
    except:
        print "exception in bah"

def gee():
    ca.Get("janet")
    try:
        while 1:
            sem1.acquire()
            sem3.acquire()
            print time.ctime(time.time()),"How do you do, I'm Gee in %x"%thread.get_ident(), random.random(),sem1.locked(),sem2.locked(),sem3.locked()
            sem3.release()
            sem1.release()
            time.sleep(random.uniform(1.0,10.0))
    except:
        print "exception in gee"

def main():
    # execute the following lines if loaded as main program.
    d=[]
    s=Simple("fred",master=Toplevel())
    s.pack()
    d.append(s)
    d.append(Simple("freddy",master=Toplevel()))
    d.append(Simple("janet",master=Toplevel()))
    d.append(Simple("jane",master=Toplevel()))

    for i in range(1):
        d.append(Simple("fred",master=Toplevel()))
        d.append(Simple("freddy",master=Toplevel()))
        d.append(Simple("janet",master=Toplevel()))
        d.append(Simple("jane",master=Toplevel()))

    for w in d:
        w.pack()

    #Simple("alan",master=Toplevel()).pack() #wf
    #Simple("albert",master=Toplevel()).pack() #wf
    #Simple("bloaty",master=Toplevel()).pack()

    ca.flush_io()

    s.update()
    
    #thread.start_new_thread(ca_main_loop,())
    time.sleep(0.1)
    ca.flush_io()

    for i in range(100):
        thread.start_new(foo,())
        thread.start_new(bah,())
        thread.start_new(gee,())

    for w in d:
        w.start_monitor()

    try:
        s.mainloop()
    finally:
        thread.exit()

if(__name__ == "__main__"):
    main()
