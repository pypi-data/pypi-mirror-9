#!/usr/bin/env python

# PyQt tutorial 5


import sys
from PyQt4 import QtCore, QtGui
import ca


class MyWidget(QtGui.QWidget):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)

        quit = QtGui.QPushButton("Quit")
        quit.setFont(QtGui.QFont("Times", 18, QtGui.QFont.Bold))

        lcd = QtGui.QLCDNumber(2)

        slider = QtGui.QSlider(QtCore.Qt.Horizontal)
        slider.setRange(0, 99)
        slider.setValue(0)
        self.slider=slider

        self.connect(quit, QtCore.SIGNAL("clicked()"),
                     QtGui.qApp, QtCore.SLOT("quit()"))
        self.connect(slider, QtCore.SIGNAL("valueChanged(int)"),
                     lcd, QtCore.SLOT("display(int)"))

        layout = QtGui.QVBoxLayout()
        layout.addWidget(quit);
        layout.addWidget(lcd);
        layout.addWidget(slider);
        self.setLayout(layout);

        
    def init_ca(self, name="fred"):
        self.ch=ca.channel(name)
        self.ch.wait_conn()
        self.ch.monitor(self.ca_callback)
        self.ch.flush()

    def ca_callback(self,vals):
        self.ch.update_val(vals)
        self.slider.setValue(100*self.ch.val)

app = QtGui.QApplication(sys.argv)
widget = MyWidget()
widget.show()
widget.init_ca("jane")
sys.exit(app.exec_())
