#!/usr/bin/python

import threading
import time,random
import ca

import gc
gc.set_debug(gc.DEBUG_LEAK)

channel = 'yamamotoHost:xxxExample'
up = threading.Lock()
dn = threading.Lock()
up.acquire()
dn.acquire()
ca.Get(channel)

tinytime=0.003
maxthreads=80

def shift_up():
    count = 0
    while 1:
        up.acquire()
        if (count % 300)==0:
            print 'shifting up... (%d times)' % count
        time.sleep(0.01)
        ca.Put(channel, 10.0)
        ca.flush_io()
        count = count + 1


def shift_down():
    count = 0
    while 1:
        dn.acquire()
        if (count % 300)==0:
            print 'shifting down... (%d times)' % count
        time.sleep(0.01)
        ca.Put(channel, 0.0)
        ca.flush_io()
        count = count + 1
        
def val_monitor(ch, val):
    if val[0] <= 5.0:
        up.release()
    else:
        dn.release()


su = threading.Thread(None, shift_up, "Up", ())
sd = threading.Thread(None, shift_down, "Down", ())


p  = []
c  = []
s  = []
ctop = []
ptoc = []

val  = 0
mtx  = threading.Lock()

def producer(i):
    global val
    mtx.acquire()
    try:
        val = ca.Get("yamamotoHost:calcExample")
    finally:
        mtx.release()
    while 1:
        ctop[i].acquire()
        mtx.acquire()
        try:
            val = ca.Get("yamamotoHost:calcExample",tmo=tinytime)
        finally:
            mtx.release()
        time.sleep(maxthreads*tinytime)
        ptoc[i].release()

        
def consumer(i):
    global val
    count = 0
    mtx.acquire()
    try:
        val = ca.Get("yamamotoHost:calcExample")
    finally:
        mtx.release()
    while 1:
        ptoc[i].acquire()
        mtx.acquire()
        try:
            if (count*maxthreads % 2000)==0:
                print "c[%d]:"%i, count, val , ca.Get("yamamotoHost:calcExample",tmo=tinytime)
        finally:
            mtx.release()
        count = count + 1
        time.sleep(maxthreads*tinytime)
        ctop[i].release()
        
def spectator(i):
    count=0
    mtx.acquire()
    try:
        ca.Get("yamamotoHost:aiExample")
        ca.Get("yamamotoHost:calcExample")
        ca.Get("yamamotoHost:calcExample1")
        ca.Get("yamamotoHost:calcExample2")
        ca.Get("yamamotoHost:calcExample3")
    finally:
        mtx.release()
    while 1:
        mtx.acquire()
        if (count%100)==0:
            print "s[%d]:"%i, count
        try:
            ca.Get("yamamotoHost:aiExample",tmo=tinytime)
            ca.Get("yamamotoHost:calcExample",tmo=tinytime)
            ca.Get("yamamotoHost:calcExample1",tmo=tinytime)
            ca.Get("yamamotoHost:calcExample2",tmo=tinytime)
            ca.Get("yamamotoHost:calcExample3",tmo=tinytime)
        finally:
            mtx.release()
        count=count+1
        time.sleep(tinytime)


for i in range(maxthreads):
    ptoc.append(threading.Lock())
    ctop.append(threading.Lock())
    ptoc[i].acquire()
    ctop[i].acquire()
    p.append(threading.Thread(None, producer, "Producer", (i,)))
    c.append(threading.Thread(None, consumer, "Consumer", (i,)))
    s.append(threading.Thread(None, spectator, "Spectator", (i,)))

ca.Get("yamamotoHost:aiExample")
ca.Get("yamamotoHost:calcExample")
ca.Get("yamamotoHost:calcExample1")
ca.Get("yamamotoHost:calcExample2")
ca.Get("yamamotoHost:calcExample3")

for i in range(maxthreads):
    #s[i].start()
    c[i].start()
    p[i].start()
    
for i in range(maxthreads):
    ctop[i].release()

su.start()
sd.start()
ca.Monitor(channel, val_monitor)

count = 0
while 1:
    mtx.acquire()        
    try:
        val = ca.Get("yamamotoHost:calcExample",tmo=tinytime)
    except:
        val=None
        print "caGet Error in Main"
    mtx.release()
    for i in range(maxthreads):
        if (count*maxthreads % 6000) == 0:
            print 'Main[%d]:'%i, count, val
            print 'Main[%d]: locking ..' % i
            ptoc[i].acquire()
            print 'Main[%d]: locked ...' % i
            time.sleep(maxthreads*tinytime)
            if ptoc[i].locked():
                ptoc[i].release()
                print 'Main[%d]: released .' % i
            else:
                print 'Main[%d]:Not locked .' % i
    count = count + 1
    time.sleep(maxthreads*tinytime)
