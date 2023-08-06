#!/usr/bin/python

import threading
import time,random
import ca


channel = 'yamamotoHost:xxxExample2'
up = threading.Lock()
dn = threading.Lock()
up.acquire()
dn.acquire()

tinytime=0.001
maxthreads=80

def shift_up():
    count = 0
    while 1:
        up.acquire()
        if (count % 100)==0:
            print 'shifting up... (%d times)' % count
        time.sleep(0.01)
        ca.Put(channel, 10.0)
        ca.flush_io()
        count = count + 1

def shift_down():
    count = 0
    while 1:
        dn.acquire()
        if (count % 100)==0:
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

def producer():
    global val,monch
    print "start producer"
    count=0
    while 1:
        production_lock.acquire()
        mtx.acquire()
        try:
            val=monch.val
        finally:
            mtx.release()
        ptoc.release()
        if (count % 100)==0:
            print "producer created %d product"%count, ptoc._Semaphore__value, time.ctime(time.time())
        count=count+1
        production_lock.release()
        time.sleep(tinytime)
        
def consumer(i):
    global val,monch
    count = 0
    print "start consumer %d"%i
    while 1:
        ptoc.acquire()
        mtx.acquire()
        try:
            if (count % 30)==0:
                cval=monch.val
                print "c[%d]:cousumed %d product"%(i, count), val ,cval,time.ctime(time.time())
        finally:
            mtx.release()
        count = count + 1
        time.sleep(tinytime)
        
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
        if (count%10)==0:
            print "s[%d]:"%i, count
        try:
            ca.Get("yamamotoHost:aiExample", tmo=tinytime)
            ca.Get("yamamotoHost:calcExample", tmo=tinytime)
            ca.Get("yamamotoHost:calcExample1", tmo=tinytime)
            ca.Get("yamamotoHost:calcExample2", tmo=tinytime)
            ca.Get("yamamotoHost:calcExample3", tmo=tinytime)
        finally:
            mtx.release()
        count=count+1
        time.sleep(0.1)


ptoc=threading.Semaphore()

production_lock=threading.Lock()

p=threading.Thread(None, producer, "Producer", ())

for i in range(maxthreads):
    c.append(threading.Thread(None, consumer, "Consumer %d"%i, (i,)))
    s.append(threading.Thread(None, spectator, "Spectator %d"%i, (i,)))

ca.Get("yamamotoHost:aiExample")
ca.Get("yamamotoHost:calcExample")
ca.Get("yamamotoHost:calcExample1")
ca.Get("yamamotoHost:calcExample2")
ca.Get("yamamotoHost:calcExample3")

monch=ca.channel("yamamotoHost:calcExample")
monch.wait_conn()
monch.autoUpdate()

su.start()
sd.start()
ca.Monitor(channel, val_monitor)


for i in range(maxthreads):
    #s[i].start()
    c[i].start()

p.start()

count = 0
while 1:
    mtx.acquire()        
    try:
        val = monch.val
        #val=random.random()
    except:
        val=None
        print "caGet Error in Main"
    mtx.release()
    if (count % 30) == 0:
        print 'Main:', count, val, ptoc._Semaphore__value
        print 'Main: locking ..' 
        production_lock.acquire()
        print 'Main: locked ...' ,ptoc._Semaphore__value
        time.sleep(0.1)
        production_lock.release()
        print 'Main: released .' ,ptoc._Semaphore__value
    count = count + 1
    time.sleep(0.1)
