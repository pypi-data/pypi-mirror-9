import ca

def ca_fd_register(arg, fd, condition):
  print arg,fd,condition
  if condition : 
      arg.append(fd)
  else:
      arg.remove(fd)

iwfd=[]

ca.add_fd_registration(ca_fd_register,iwfd)
print "create channel"

#ch=ca.channel("KEKB:CO_IOC:COCCC:CLOCK")
ch=ca.channel("fred")

print "waiting connection"
ch.pend_event(0.1)
print "waiting connection"
ch.pend_event(0.1)
print "waiting connection"
ch.wait_conn()


def myMonitor(val,ch=ch):
  ch.update_val(val)
  print val,ch.val
print "autoUpdate"

ch.autoUpdate()
print "pend_event"
ch.pend_event(1)

ch.monitor(myMonitor)

print ch.val

import select

def loop():
  global iwfd
  while 1:
    ifd,ofd,efd=select.select(iwfd,[],[],None)
    for fd in ifd:
      print fd
      ca.pend_event(0.0001)
  else:
    print "done"
