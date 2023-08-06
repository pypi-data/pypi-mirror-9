#!/usr/bin/python

import threading
import time,random
import ca


channel = 'yamamotoHost:xxxExample'
up = threading.Lock()
dn = threading.Lock()
up.acquire()
dn.acquire()
ca.Get(channel)

tinytime=0.001
maxthreads=20

def shift_up():
    count = 0
    while 1:
        up.acquire()
        if (count*maxthreads % 6000)==0:
            print 'shifting up... (%d times)' % count,time.ctime(time.time())
        time.sleep(0.01)
        ca.Put(channel, 10.0)
        ca.flush_io()
        count = count + 1


def shift_down():
    count = 0
    while 1:
        dn.acquire()
        if (count*maxthreads % 6000)==0:
            print 'shifting down... (%d times)' % count,time.ctime(time.time())
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
    while 1:
        ctop[i].acquire()
        mtx.acquire()
        try:
            val=monch.val
        finally:
            mtx.release()
        time.sleep(tinytime)
        ptoc[i].release()

        
def consumer(i):
    global val
    count = 0
    while 1:
        ptoc[i].acquire()
        mtx.acquire()
        try:
            if (count*maxthreads % 10000)==0:
                print "c[%d]:"%i, count, val , monch.val ,time.ctime(time.time())
        finally:
            mtx.release()
        count = count + 1
        time.sleep(tinytime)
        ctop[i].release()
        
def spectator(i):
    count=0
    mtx.acquire()
    channels=map(ca.channel,
                 ("yamamotoHost:aiExample",
                  "yamamotoHost:calcExample",
                  "yamamotoHost:calcExample1",
                  "yamamotoHost:calcExample2",
                  "yamamotoHost:calcExample3",))
    [(x.wait_conn(),x.autoUpdate()) for x in channels]
    mtx.release()

    while 1:
        mtx.acquire()
        if (count*maxthreads % (400+i*maxthreads))==0:
            print "s[%d]:"%i, count, time.ctime(time.time()),
            try:
                print [x.val for x in channels],
            finally:
                print 
        try:
            v=[x.val for x in channels],
        finally:
            mtx.release()
        count=count+1
        time.sleep(tinytime*maxthreads**2)

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

monch=ca.channel("yamamotoHost:calcExample")
monch.wait_conn()
monch.autoUpdate()

for i in range(maxthreads):
    s[i].start()
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
        val = monch.val
    except:
        val=None
        print "caGet Error in Main"
    mtx.release()
    for i in range(maxthreads):
        if (count*maxthreads % 30000) == i:
            print 'Main[%d]:'%i, count, val,time.ctime(time.time())
            print 'Main[%d]: locking ..' % i,time.ctime(time.time())
            ptoc[i].acquire()
            print 'Main[%d]: locked ...' % i,time.ctime(time.time())
            time.sleep(tinytime)
            if ptoc[i].locked():
                ptoc[i].release()
                print 'Main[%d]: released .' % i,time.ctime(time.time())
            else:
                print 'Main[%d]:Not locked .' % i,time.ctime(time.time())
    count = count + 1
    time.sleep(tinytime)
