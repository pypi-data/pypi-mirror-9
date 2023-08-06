#!/bin/env python
# -*- coding:utf-8 -*-
import ca
#import fakeca as ca
from caAlarmSeverity import *

import sys
from PyQt4 import QtCore, QtGui
import PyQt4.Qt as Qt

import types,time,thread
from math import modf

class LabeledEntry(QtGui.QWidget):
    def __init__(self, text, *args):
        QtGui.QWidget.__init__(self,*args)
        self.label=QtGui.QLabel(self.tr(text))
        self.entry=QtGui.QLabel()
        mylayout = QtGui.QHBoxLayout()
        mylayout.addWidget(self.label)
        mylayout.addWidget(self.entry)
        self.setLayout(mylayout)
        self.entry.setDisabled(True)
    def setText(self, text):
        self.entry.setText(text)

class CaInfoWidget(QtGui.QWidget):
    def init_ca(self, ch):
        if( type(ch) in types.StringTypes):
            self.ch=ca.channel(ch)
            self.ch.wait_conn()
        elif isinstance(ch, ca.channel):
            self.ch=ch
        else:
            raise "No Channel object  nor Channel name"
        self.ca_update_lock=thread.allocate()
            
    def __init__(self, ch, *args):
        QtGui.QWidget.__init__(self,*args)
        self.init_ca(ch)

        quit = QtGui.QPushButton("Quit")
        quit.setFont(QtGui.QFont("Times", 18, QtGui.QFont.Bold))
        self.connect(quit, QtCore.SIGNAL("clicked()"),
                     QtGui.qApp, QtCore.SLOT("quit()"))

        controlsLayout=QtGui.QVBoxLayout()
        self.controlsGroup = Qt.QGroupBox(self.ch.name)

        self.varEntry=LabeledEntry(self.tr("Value:"))
        self.tsEntry=LabeledEntry(self.tr("   TS:"))
        self.statusEntry=LabeledEntry(self.tr("Status:"))
        self.counterEntry=LabeledEntry(self.tr("Counter:"))
        controlsLayout.addWidget(self.varEntry)
        controlsLayout.addWidget(self.tsEntry)
        controlsLayout.addWidget(self.statusEntry)
        controlsLayout.addWidget(self.counterEntry)
        self.controlsGroup.setLayout(controlsLayout)
        layout=Qt.QVBoxLayout()
        layout.addWidget(self.controlsGroup)
        layout.addWidget(quit)
        self.statusEntry.setText(self.tr("<font color=\"%s\" "
                                         " style=\"background-color:pink\">%s / %s</font>"%(
                    "green","N/A","N/A")))
        self.setLayout(layout)
        self.ucounter =0
        self.counter =0

    def Update_Info(self):
        if not self.ch.val:
            return
        self.ucounter += 1
        self.varEntry.setText(self.tr("%s"%self.ch.val))
        self.tsEntry.setText(self.tr(ca.TS2Ascii(self.ch.ts)))
        self.statusEntry.setText(self.tr("<font color=\"%s\" style=\"background-color:pink\">%s / %s</font>"%(
                    AlarmSeverity.Colors[self.ch.sevr],
                    AlarmSeverity.Strings[self.ch.sevr],
                    AlarmStatus.Strings[self.ch.status])))
        self.counterEntry.setText(self.tr("%d/%d/%d"%(
                self.counter,self.ucounter,self.counter-self.ucounter)))
        try:
            self.ca_update_lock.release()
        except:
            pass

    def start_monitor(self):
        print "start monitor"
        self.ca_update_lock.acquire(False)
        self.ch.monitor(callback=self.ca_callback)
        self.ch.flush()
        self.ca_update_lock.release()

    def clear_monitor(self):
        print "cancel monitor"
        self.ch.clear_monitor()
        self.ch.flush()
        try:
            self.ca_update_lock.release()
        except:
            pass

    def ca_callback(self,vals):
        self.counter +=1
        self.ch.update_val(vals)
        if self.ca_update_lock.acquire(False):
            self.Update_Info()
        else:
            print "callback canceled"
    def __del__(self):
        try:
            self.clear_monitor()
        finally:
            del self.ch
def mkApp():
    return QtGui.QApplication(sys.argv)

def test():
    app = QtGui.QApplication(sys.argv)
    widget = CaInfoWidget("jane")
    widget.show()
    widget.Update_Info()
    widget.start_monitor()
    sys.exit(app.exec_())

if __name__ =="__main__":
    test()
else:
    app = QtGui.QApplication(sys.argv)
