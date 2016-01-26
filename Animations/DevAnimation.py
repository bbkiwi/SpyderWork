
"""
For testing and development
Animation class to handle timing and be able to start
via a Timer
"""

import time
from random import randint, random
import threading
from threading import Timer
#import console
import math
import types



class animThread(threading.Thread):
    def __init__(self, anim, args):
        super(animThread, self).__init__()
        self.setDaemon(True)
        self._anim = anim
        self._args = args

    def run(self):
        log.logger.info("Starting thread...")
        self._anim._run(**self._args)
        log.logger.info("Thread Complete")

class BaseAnimation(object):
    def __init__(self, led):
        self._led = led
        self.animComplete = False
        self._step = 0
        self._timeRef = 0
        self._internalDelay = None
        self._threaded = False
        self._thread = None
        self._callback = None
        self._stopEvent = threading.Event()
        self._stopEvent.clear()
        self.updateTimes = []
	
    def preRun(self, amt=1):
        self._led.all_off()

    def postRun(self):
        self._led.resetMasterBrightness()

    def preStep(self, amt=1):
        pass

    def postStep(self, amt=1):
        pass


    def step(self, amt=1):
        raise RuntimeError("Base class step() called. This shouldn't happen")

        
    def stopThread(self, wait=False):
        # NOTE _stopEvent is attribute wether or not animation is threaded
        # so should set the flag in all cases
       self._stopEvent.set()
        if wait:
            self._thread.join()

    def __enter__(self):
        return self

    def _exit(self, type, value, traceback):
        pass

    def __exit__(self, type, value, traceback):
        self._exit(type, value, traceback)
        self.stopThread(wait=True)
        self._led.all_off()
        self._led.update()
        self._led.waitForUpdate()

    def cleanup(self):
        return self.__exit__(None, None, None)
	
    def stopped(self):
        if self._thread:
            return not self._thread.isAlive()
        else:
            return True
	    
    def _run(self, amt, fps, sleep, max_steps, untilComplete, max_cycles, updateWithPush=True):
        self.preRun()
        # calculate fps based on sleep time (ms) 
        if sleep and fps is None:
            fps = 1000.0 / sleep
        self._step = 0
        cur_step = 0
        cycle_count = 0
        self.animComplete = False
        
        needtowait = False # don't wait upon initial entry
        while not self._stopEvent.isSet() and (
                 (max_steps == 0 and not untilComplete) or
                 (max_steps > 0 and cur_step < max_steps) or
                 (max_steps == 0 and untilComplete and not self.animComplete)):

            # step processing starts here
            self._timeRef = time.time()
            
            if hasattr(self, "_input_dev"):
                self._keys = self._input_dev.getKeys()
            self.preStep(amt)
            self.step(amt)

            #print '{:.3f} {} step {} with amt = {}'.format(start, name, cur_step, amt)            #console.set_color()
            mid = time.time()

            if self._internalDelay:
                if type(self._internalDelay) == types.BuiltinFunctionType:
                    self.waitfunc(self._internalDelay())
                else:
                    self.waitfunc(self._internalDelay / 1000.0)
            elif needtowait and fps is not None:
                waitTillFrame(fps, self.waitfunc) 
            else:                 
                needtowait = True
                            
            if self._stopEvent.isSet():
                break  
                

            # update code starts here    
            startupdate = time.time()
            self.updateTimes.append(startupdate - now)
            #console.set_color(*self.textcol)
            #print '{:.4f} {} update step {}'.format(startupdate - now, name, cur_step)
            #console.set_color()
            if updateWithPush:
                self._led.update()
            else:
                self._led._updatenow.set()   # signals masterAnimation to act

            cur_step += 1

        self.animComplete = True
        self.postRun()

        if self._callback:
            self._callback(self)


    def run(self, name=None, amt = 1, fps=None, sleep=None, max_steps = 0, max_cycles = 0, threaded = False, joinThread = False):
        self.name = name
        #console.set_color(*self.textcol)
        print '{:.3f} Starting {}'.format(time.time() - now, name)
        #console.set_color()
        # TODO check orig if first run threaded and second time unthreaded may fail
        #   this is not a complete fix see BugAnimation.py 
        #   problems can happen is there is not enough delay between
        #   stopping it and restarting it (on my PC needed delay of )
        #   no problem if stop with stopThread(wait=True)
        self._threaded = threaded
        #if self._threaded:
        self._stopEvent.clear()

        if self._threaded:
            self.waitfunc = self._stopEvent.wait
            args = {}
            l = locals()
            run_params = ["amt", "fps", "sleep", "max_steps", "untilComplete", "max_cycles", "updateWithPush"]
            for p in run_params:
                if p in l:
                    args[p] = l[p]
            self._thread = animThread(self, args)
            self._thread.start()
            if joinThread:
                self._thread.join()
        else:
            self.waitfunc = time.sleep
            self._run(amt, fps, sleep, max_steps, untilComplete, max_cycles, updateWithPush)

def schedanim(name, fps, color, st=None, _internalDelay=None):
    """
    schedule animation name at fps with plot color st random is not given
    """
    if st is None:
        st = randint(1,8)
    delst = randint(1,6)
    a = Animation(color)
    a._internalDelay = _internalDelay
    #console.set_color(*color)  
    print 'Animation: {} fps={} {} {}'.format(name, fps, st, st + delst)
    #console.set_color()  
    # NOTE Timer objects are threads, so can run Animation as threaded or not
    #t1 = Timer(st, a.run, args=(), kwargs={'name':name, 'fps':fps, 'threaded':True})
    t1 = Timer(st, a.run, kwargs={'name':name, 'fps':fps, 'threaded':False})
    t2 = Timer(st + delst, a.stopThread, ())
    #waitTillFrame(fps)
    t1.start()
    t2.start()
    return a


def waitTillFrame(fps=1, waitfunc=time.sleep):
    if fps < 1000:
        waitfunc(.001) # need min wait time
        s = time.time()
        f = s * fps # number of elapsed frames (fractional)
        nf = math.ceil(f) # the next integral frame
        breaktime = nf / fps
        # print breaktime - s
        waitfunc(breaktime - s)
    else:
        breaktime = 0
    return breaktime
    #return time.time()


# wait till integral number of seconds
now = waitTillFrame() # global
now = time.time() # global
print now

anlist = []
anlist.append(schedanim('fancy worm', 1, (1, 0, 0), st=0))
anlist.append(schedanim('big bloom', 12, (0, 1, 0), _internalDelay=random))
anlist.append(schedanim('dimmer', .5, (1, 0, 1)))
anlist.append(schedanim('dumb', 7, (0, 0, 1), st=0))

   
while any([not a.animComplete for a in anlist]):
    pass
  
time.sleep(.01)  # time for _Timer thread to die
print threading.enumerate()

h = 100*(len(anlist) + 2)
maxt = max([a.updateTimes[-1] for a in anlist])


import matplotlib.pyplot as plt
plt.clf()
col = 'brgcwk'
[plt.plot(a.updateTimes, [i] * len(a.updateTimes), col[i%6]+'o') for i, a in enumerate(anlist)]
ax = plt.axis()
delx = .01 * (ax[1] - ax[0])
plt.axis([ax[0]-delx, ax[1]+delx, ax[2]-1, ax[3]+1])
