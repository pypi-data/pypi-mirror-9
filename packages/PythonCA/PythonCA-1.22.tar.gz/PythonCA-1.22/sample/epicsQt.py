import sys
import ca
import PyQt4.Qt as Qt

class epicsPoll(Qt.QObject):
    def __init__(self):
        Qt.QObject.__init__(self)
        self.startTimer(100)
    def timerEvent(self, event):
        ca.poll()


class epicsQt(Qt.QObject):
    def __init__(self, pvName):
        Qt.QObject.__init__(self)
        self.pv = ca.channel(pvName, cb = self.connectCB)
        self.never_conn=True

    # Callback functions

    def controlCB(self, epicsArgs):
        print epicsArgs

    def valueCB(self, epicsArgs):
        print self.pv.name,epicsArgs

    def connectCB(self):
        pass

if __name__ == '__main__':
    app = Qt.QApplication(sys.argv)
    poll = epicsPoll()

    win = Qt.QWidget()
    layout = Qt.QVBoxLayout()
    win.setLayout(layout)

    layout.addWidget(Qt.QLabel(win))
    layout.addWidget(Qt.QLabel(win))

    pvs=[]
    for i in range(350):
        pvs.append(epicsQt('catest'))

    win.show()
    sys.exit(app.exec_())
