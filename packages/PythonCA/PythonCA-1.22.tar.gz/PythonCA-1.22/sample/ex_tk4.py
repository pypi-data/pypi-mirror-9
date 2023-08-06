#!/usr/bin/python
# -*- coding: shift_jis -*-

from Tkinter import *
import ca
import time

class CB:
   def __init__(self,ch):
       self.ch=ch
   def __call__(self,*args,**env):
       print time.ctime(time.time()), self.ch, args,env
       #print time.ctime(time.time()), self, self.ch.name,self.id,vals
       pass

class ChLabel(Label):
    def init(self, chname):
        self.dirty=-1        
        self.monitor_active=0
        self.var=DoubleVar()
        self.configure(textvariable=self.var)
        self.chname=chname
        #self.ca_init()

    def ca_init(self, *args,**env):
        self.ch=ca.channel(self.chname)
        try:
            self.ch.wait_conn(200,0.1)
        except:
            print "wait_conn failed"
            self.ch.pend_event(0.2)
            
        self.ch.get_info()
        while not self.ch.isConnected():
            print ".",
            self.ch.pend_event(1.0)
        self.ch.get();self.ch.flush()
        #print self.ch.name, self.ch.val,self.ch.get_info()
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
        self.ch.monitor(self.update_var)
        self.ch.flush()
        self.monitor_active=1

    def update_var(self,val=None):
        self.ch.update_val(val)
        #print "update_var",self.ch.name, val,time.time()
        if self.ch.val:
            self.var.set(self.ch.val)

    def __init__(self, master, chname, width=None):
        Label.__init__(self, master)
        self.configure(width=width)
        self.init(chname)

class App(Frame):
    def init(self):
        self.master.title("CA monitor test")
        f=LabelFrame(self, text = 'ChLabel test', labelanchor = NW)
        f.pack()

        chname="SUM_GET_RFG_NUM"
        chname="fred"
        Label(f, text='"%s" is' % chname).pack(side=LEFT)
        cl1=ChLabel(f, chname, width=3)
        cl1.pack(side=TOP, fill=X, anchor=NW)
        cl1.ca_init()
        # ここで cl1 のモニターをスタートすると、cl2 を生成したところでクラッシュ
        cl1.start_monitor()

        chname="SUM_SET_RFG_NUM"
        chname="freddy"
        Label(f, text='"%s" is' % chname).pack(side=LEFT)
        cl2=ChLabel(f, chname, width=3)
        cl2.pack(side=TOP, fill=X, anchor=NW)
        cl2.ca_init()
        # ここで cl1 のモニターをスタートすると、成功する
        #cl1.start_monitor()

        cl2.start_monitor()

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
