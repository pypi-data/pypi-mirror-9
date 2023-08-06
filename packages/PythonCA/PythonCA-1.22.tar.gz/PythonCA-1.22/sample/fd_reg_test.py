import UserDict,select
import ca

class SimpleFileManager(UserDict.UserDict):
    def __init__(self):
        UserDict.UserDict.__init__(self)

    def mainloop(self):
        fds=self.keys()
        while 1:
            r,w,e=select.select(fds,fds,[],None)
            #print r,w,e
            if r:
                ca.poll()
                
    def do_one_event(self):
        fds=self.keys()
        r,w,e=select.select(fds,[],[])
        for f in r:
            ca.poll()

    def loop(self):
        after(fmgr.loop)
        self.do_one_event()

fmgr=SimpleFileManager()

def fd_register(arg, fd, cond):
    print "fd_register",fd, cond, arg
    if cond:
        fmgr[fd]=arg
    else:
        if fmgr.has_key(fd):
            del fmgr[fd]
import ca

def test():
    ca.add_fd_registration(fd_register,0.01)
    ca.Monitor("freddy")
    ca.Monitor("fred")
    ca.Monitor("jane")
    ca.Monitor("janet")
    
    fmgr.mainloop()

if __name__ == "__main__":
    test()
