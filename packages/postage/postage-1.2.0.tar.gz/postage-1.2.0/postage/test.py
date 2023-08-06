from microthreads import *

class MyThread(MicroThread):
    def create(self):
        print "CREATE"
        raise StopIteration
        
    def step(self):
        print "STEP"


mt = MyThread()
scheduler = MicroScheduler(autoquit=True)
scheduler.add_microthread(mt)

for i in scheduler.main():
    pass