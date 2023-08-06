import wx
import ca,time,thread
from caAlarmSeverity import *

chname="jane"

class MyApp(wx.PySimpleApp):
    def OnInit(self):
        self.timer=wx.Timer()
        frame = wx.Frame(None, -1, "Hello from wxPython")
        self.frame=frame
        self.count=0
        self.ca_update_lock=thread.allocate() # initial state of the lock is free.
        self.ca_update_lock.acquire()

        self.ch=ca.channel(chname)
        self.ch.wait_conn()
        self.ch.get()
        self.ch.flush()

        self.panel=panel = wx.Panel(frame)
        self.sizer=sizer = wx.FlexGridSizer(cols=2, hgap=5, vgap=5)
        sizer.AddGrowableRow(1)
        sizer.AddGrowableCol(1)

        self.sizeCtrl = wx.TextCtrl(panel, -1, "", style=wx.TE_READONLY,size=(250,-1))
        sizer.Add(wx.StaticText(panel, 1, "channel value:"))
        sizer.Add(self.sizeCtrl, 1, wx.GROW)

        self.posCtrl = wx.TextCtrl(panel, -1, "",size=(250,-1),
                                   style=wx.TE_READONLY|wx.TE_MULTILINE)
        sizer.Add(wx.StaticText(panel, 1, "TimeStamp:"))
        sizer.Add(self.posCtrl, 1, wx.GROW)

        self.alarmCtrl = wx.TextCtrl(panel, -1, "",size=(250,-1),
                                   style=wx.TE_READONLY)
        sizer.Add(wx.StaticText(panel, 1, "AlarmStatus:"))
        sizer.Add(self.alarmCtrl, 1, wx.GROW)

        self.idleCtrl = wx.TextCtrl(panel, -1, "", style=wx.TE_READONLY,size=(250,-1))
        sizer.Add(wx.StaticText(panel, 1, "Counter:"))
        sizer.Add(self.idleCtrl, 1, wx.GROW)


        border = wx.BoxSizer()
        border.Add(sizer, 1, wx.ALL|wx.GROW, 6)
        panel.SetSizer(border)
        #sizer.SetSizeHints(frame)
        border.SetSizeHints(frame)

        self.frame.Title="channel name : %s "%self.ch.name
        panel.Update()
        frame.Show(True)
        self.SetTopWindow(frame)
        return True

    def StartTimer(self):
        self.timer.Start(milliseconds = 100, oneShot = False)

    def onTimer(self,event):
        self.idleCtrl.SetValue(str(self.count))
        if (self.ca_update_lock.acquire(False)):
            self.UpdateWin()

    def UpdateWin(self):
        if type(self.ch.val) == type(1.0):
            self.sizeCtrl.SetValue("%s"%self.ch.val )
            sec,subsec=divmod(self.ch.ts,1.0)
            self.posCtrl.SetValue("%s\n"%time.asctime(ca.TS2time(self.ch.ts) ))
            self.posCtrl.AppendText("\tmicro-sec:%06ld"%(1e6*subsec))
            #self.alarmCtrl.SetForegroundColor(AlarmSeverity.Colors[self.ch.sevr])
            self.alarmCtrl.SetValue("%-s / %s"%(AlarmSeverity.Strings[self.ch.sevr],AlarmStatus.Strings[self.ch.status]))

    def OnIdle(self, event):
        self.idleCtrl.SetValue(str(self.count))
        self.UpdateWin()

    def ca_callback(self,valstat):
        self.count +=1
        self.ch.update_val(valstat)
        #self.UpdateWin() # not a good Idea to call wx routines in CA callback. Just Que
        self.ca_update_lock.release() # or release a lock.

    def MainLoop(self):
        self.timer.Bind(wx.EVT_TIMER, self.onTimer)
        self.Bind(wx.EVT_TIMER, self.onTimer)
        self.Bind(wx.EVT_IDLE, self.OnIdle)
        self.ch.monitor(callback=self.ca_callback)
        self.ch.flush()
        self.StartTimer()
        wx.PySimpleApp.MainLoop(self)
        
if __name__ == "__main__":
    app = MyApp(0)
    app.MainLoop()
