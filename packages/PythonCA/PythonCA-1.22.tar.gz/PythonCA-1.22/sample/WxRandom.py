import wx
import ca

#import niseca as ca

import time,thread
from caAlarmSeverity import *

chname="jane"

class MyApp(wx.PySimpleApp):
    def OnInit(self):
        self.timer=wx.Timer()
        self.timer.Bind(wx.EVT_TIMER, self.onTimer)
        self.Bind(wx.EVT_TIMER, self.onTimer)
        frame = wx.Frame(None, -1, "Hello from wxPython")
        self.frame=frame

        self.ch=ca.channel(chname)
        self.ch.wait_conn()
        self.ch.get()
        self.ch.flush()
        self.ca_update_lock=thread.allocate() # initial state of the lock is free.
        self.ca_update_lock.acquire()

        self.panel=panel = wx.Panel(frame)
        self.sizer=sizer = wx.FlexGridSizer(cols=2, hgap=5, vgap=5)

        self.gauge=wx.Gauge(panel, -1,1000,(110,50),(250,20))
        self.gvalue=0
        self.gvalue_lock=thread.allocate()
        self.count=0

        sizer.Add(wx.StaticText(panel, -1, "Gauge:"))
        sizer.Add(self.gauge)
        
        self.sizeCtrl = wx.TextCtrl(panel, -1, "", style=wx.TE_READONLY,size=(250,20))
        sizer.Add(wx.StaticText(panel, -1, "channel value:"))
        sizer.Add(self.sizeCtrl)

        self.posCtrl = wx.TextCtrl(panel, -1, "",size=(250,40),
                                   style=wx.TE_READONLY|wx.TE_MULTILINE)
        sizer.Add(wx.StaticText(panel, -1, "TimeStamp:"))
        sizer.Add(self.posCtrl)

        self.alarmCtrl = wx.TextCtrl(panel, -1, "",size=(250,20),
                                   style=wx.TE_READONLY)
        sizer.Add(wx.StaticText(panel, -1, "AlarmStatus:"))
        sizer.Add(self.alarmCtrl)

        self.idleCtrl = wx.TextCtrl(panel, -1, "", style=wx.TE_READONLY,size=(250,20))
        sizer.Add(wx.StaticText(panel, -1, "Counter:"))
        sizer.Add(self.idleCtrl)

        self.Bind(wx.EVT_IDLE, self.OnIdle)
        self.Bind(wx.EVT_WINDOW_DESTROY, self.Cleanup)

        border = wx.BoxSizer()
        border.Add(sizer, 0, wx.ALL, 20)
        panel.SetSizer(border)

        self.frame.Title="channel name : %s "%self.ch.name
        panel.Update()
        frame.Show(True)
        self.SetTopWindow(frame)

        return True

    def Cleanup(self,evt):
        self.timer.Stop()
        self.ch.clear_monitor()
        self.ch.flush()
        self.Unbind(wx.EVT_IDLE)
        
    def StartTimer(self):
        self.timer.Start(milliseconds = 100, oneShot = False)

    def onTimer(self,event):
        self.count +=1
        self.gvalue_lock.acquire()
        self.gvalue = self.count % 1000
        self.gauge.SetValue(self.gvalue)
        #self.gauge.Pulse()
        self.idleCtrl.SetValue(str(self.count))
        self.gvalue_lock.release()
        if (self.ca_update_lock.acquire(False)):
            self.UpdateWin()

    def UpdateWin(self):
        if type(self.ch.val) == type(1.0):
            self.sizeCtrl.SetValue("%s"%self.ch.val )
            sec,subsec=divmod(self.ch.ts,1.0)
            self.posCtrl.SetValue("%s\n"%time.asctime(time.localtime(self.ch.ts) ))
            self.posCtrl.AppendText("\tmicro-sec:%06ld"%(1e6*subsec))
            #self.alarmCtrl.SetForegroundColor(AlarmSeverity.Colors[self.ch.sevr])
            self.alarmCtrl.SetValue("%-s / %s"%(AlarmSeverity.Strings[self.ch.sevr],AlarmStatus.Strings[self.ch.status]))

    def OnIdle(self, event):
        #self.gauge.Pulse()
        self.idleCtrl.SetValue(str(self.count))
        self.UpdateWin()

    def ca_callback(self,valstat):
        self.ch.update_val(valstat)
        #self.UpdateWin() # not a good Idea to call wx routines in CA callback. Just Que
        self.ca_update_lock.release() # or release a lock.
        
    def MainLoop(self):
        self.ch.monitor(callback=self.ca_callback)
        self.ch.flush()
        self.StartTimer()
        wx.PySimpleApp.MainLoop(self)
        
if __name__ == "__main__":
    app = MyApp(0)
    app.MainLoop()
