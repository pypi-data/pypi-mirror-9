import wx
import ca,time,thread
from caAlarmSeverity import *

chname="jane"

class MyApp(wx.PySimpleApp):
    def OnInit(self):
        self.timer=wx.Timer()
        frame = wx.Frame(None, -1, "Hello from wxPython")
        self.frame=frame
        # initial state of the lock is free.
        self.ca_update_lock=thread.allocate() 
        self.ca_update_lock.acquire()

        self.ch=ca.channel(chname)
        self.ch.wait_conn()
        self.ch.get()
        self.ch.flush()

        self.panel=panel = wx.Panel(frame)
        self.sizer=sizer = wx.FlexGridSizer(cols=2, hgap=5, vgap=5)

        self.sizeCtrl = wx.TextCtrl(panel, -1, "", style=wx.TE_READONLY,size=(250,20))
        sizer.Add(wx.StaticText(panel, -1, "channel value:"))
        sizer.Add(self.sizeCtrl)

        border = wx.BoxSizer()
        border.Add(sizer, 0, wx.ALL, 20)
        panel.SetSizer(border)

        self.frame.Title="channel name : %s "%self.ch.name
        panel.Update()
        frame.Show(True)
        self.SetTopWindow(frame)
        return True

    def StartTimer(self):
        self.timer.Start(milliseconds = 100, oneShot = False)

    def onTimer(self,event):
        if (self.ca_update_lock.acquire(False)):
            self.UpdateWin()

    def UpdateWin(self):
        if type(self.ch.val) == type(1.0):
            self.sizeCtrl.SetValue("%s"%self.ch.val )

    def OnIdle(self, event):
        self.UpdateWin()

    def ca_callback(self,valstat):
        self.ch.update_val(valstat)
        #self.UpdateWin() # not a good Idea to call wx routines in CA callback.
        self.ca_update_lock.release() # Just Que or release a lock.

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
