#!/usr/bin/python
# -*- coding: shift_jis -*-

from Tkinter import *
import ca,thread

class ChLabel(Label):
    def CB(self,*args):
        print "con callback in",self.ch.name
        self.ch.get();self.ch.pend_event(1)
        if self.ch.val:
            s="%f"%self.ch.val
            self.dirty=1
        else:
            s="CA readback"
            self.dirty=0
        print self.ch.name, self.ch.val
        self.monitor_active=0
        #self.start_monitor()

    def init(self, chname):
        self.ch=ca.channel(chname,cb=self.CB)
        self.ca_update_lock=thread.allocate()
        self.ch.wait_conn()
        
    def start_monitor(self):
        if self.monitor_active:
            print self.ch.name," is already monitored"
            return
        self.monitor_active=1
        self.ch.monitor(self.callback_ca)
        thread.start_new_thread(self.callback_tk,())
        self.ch.flush()
        
    def callback_ca(self,val=None):
        self.ch.update_val(val)
        self.ca_update_lock.release()

    def callback_tk(self):
        while self.monitor_active:
            self.ca_update_lock.acquire()
            self.update_var()
        thread.exit_thread()

    def update_var(self):
        if self.ch.val:
            self.var.set(self.ch.val)
            
    def __init__(self, master, chname):
        lf=self.lf=LabelFrame(master, text='"%s" is' % chname, labelanchor = NW)
        Label.__init__(self, lf)
        self.var=DoubleVar()
        self.configure(textvariable=self.var)
        
        self.init(chname)

    def pack(self, *args,**env):
        Label.pack(self, side=LEFT,fill=BOTH)
        self.lf.pack(*args,**env)

        
#class Mylabel(Label):
#    def init(self,name):
#        self.configure(textvariable=name)
#    def __init__(self, master, name):
#        Label.__init__(self, master)
#        self.init(name)


class App(Frame):
    def init(self):
#        self.inputstr=StringVar()
#        self.inputstr.set('hoge')
#        Entry(self, textvariable=self.inputstr).pack()
#        Mylabel(self, self.inputstr).pack()
        self.master.title("CA monitor test")
        f=LabelFrame(self, text = 'ChLabel test', labelanchor = NW)
        f.pack(fill=BOTH)
        chname="SUM_GET_RFG_NUM"
        chnames=("jane","janet","fred","freddy")
        
        #self.labels=map(lambda chn,f=f:ChLabel(f, chn),chnames)
        self.labels=[ChLabel(f, chn) for chn in chnames]
        [l.pack(side=TOP,fill=X) for l in self.labels]

        
    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.init()
        self.pack()

    def mainloop(self):
        [l.start_monitor() for l in self.labels]
        Frame.mainloop(self)
        
def main():
    app = App()
    app.pack()
    app.mainloop()

if __name__ == "__main__":
    main()
                                    
