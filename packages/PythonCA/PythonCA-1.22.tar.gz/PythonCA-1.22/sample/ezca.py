import ca
from ca import pend_io,pend_event, ch_state, Get,Put, Monitor, ClearMonitor

class ezch(ca.channel):
    def __init__(self, name):
        ca.channel.__init__(self, name, cb=self.conn_handler)

    def conn_handler(self, *args,**env):
        self.update_info()
        cs=self.conn_state
        if cs == ch_state.cs_conn:
            print self.name, "is connected"
        elif cs == ch_state.cs_never_conn:
            print self.name, " never connected"
        elif cs == ch_state.cs_prev_conn:
            print self.name, " disconnected"
        elif cs == ch_state.cs_close:
            print self.name, " closed"
        else:
            print self.name, "unexpected connection state",cs

        if self.isConnected():
            self.autoUpdate()
