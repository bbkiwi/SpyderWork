"""
For testing and development
bare bones of Animation class to handle timing and be able to start
by adding start and stop parameters to the Animation run method
"""

import time
from random import randint, random
import threading
from threading import Timer
#import console
import math
import types
import bisect

#import canvas

#def plotDot(x, y, color=(0, 0, 0), th=20):
#    canvas.set_fill_color(*color)
#    canvas.fill_ellipse(x - th / 2, y - th / 2, th, th)


class animThread(threading.Thread):
    def __init__(self, anim, args):
        super(animThread, self).__init__()
        self.setDaemon(True)
        self._anim = anim
        self._args = args

    def run(self):
        self._anim._run(**self._args)

class Animation(object):
    def __init__(self, textcol):
        self.textcol = textcol
        self.animComplete = False
        self._timeRef = 0
        self._internalDelay = None
        self._threaded = False
        self._thread = None
        self._stopEvent = threading.Event()
        self._stopEvent.clear()
        self.updateTimes = []
        
#    def _msTime(self):
#        return (time.time() - now) * 1000.0

    def stopThread(self, wait=False):
        # NOTE _stopEvent is attribute wether or not animation is threaded
        # so should set the flag in all cases
        #console.set_color(*self.textcol)
        print '{:.3f} Stopping {}'.format(time.time() - now, self.name)
        #console.set_color()
        self._stopEvent.set()
        if wait:
            self._thread.join()
#        if self._thread:
#            self._stopEvent.set()
#            if wait:
#                self._thread.join()

    def stopped(self):
        if self._thread:
            return not self._thread.isAlive()
        else:
            return True

    def _run(self, name, amt, fps, sleep, max_steps, max_cycles, gostop):
        # calculate fps based on sleep time (ms) 
        if sleep and fps is None:
            fps = 1000.0 / sleep
#        if fps is not None:
#            sleep = 1000.0 / fps
#
#        initSleep = sleep

        self._step = 0
        cur_step = 0
        cycle_count = 0
        self.animComplete = False
        
#        startupdate = self._msTime() - sleep # just to get started
        needtowait = False # don't wait upon initial entry
        while not self._stopEvent.isSet() and (
                 (max_steps > 0 and cur_step < max_steps) or
                 (max_steps == 0  and not self.animComplete)):

            # step processing starts here
            self._timeRef = time.time()
            

            #start = self._msTime()
            #console.set_color(*self.textcol)
            #print '{:.3f} {} step {} with amt = {}'.format(start, name, cur_step, amt)
            #console.set_color()
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
            
            # gostop is list of times to start, then stop, then start etc
            # will wait if in time gap where should be stopped till out of it
            if waitInGap(time.time() - now, gostop, waitfunc=self.waitfunc):
                break #  if outside last time to complete the Animation
              
            # update code starts here    
            startupdate = time.time()
            self.updateTimes.append(startupdate - now)
            #console.set_color(*self.textcol)
            print '{:.4f} {} update step {}'.format(startupdate - now, name, cur_step)
            #console.set_color()
            

            cur_step += 1
            

        self.animComplete = True

    def run(self, name=None, amt = 1, fps=None, sleep=None, max_steps = 0, 
            max_cycles = 0, threaded = False, joinThread = False, gostop=None):
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
            run_params = ["name", "amt", "fps", "sleep", 
                          "max_steps", "max_cycles", "gostop"]
            for p in run_params:
                if p in l:
                    args[p] = l[p]
            self._thread = animThread(self, args)
            self._thread.start()
            if joinThread:
                self._thread.join()
        else:
            self.waitfunc = time.sleep
            self._run(name, amt, fps, sleep, max_steps, max_cycles)      

def schedanim(name, fps, color, gostop=None, _internalDelay=None):
    """
    schedule animation name at fps with plot color st random is not given
    """
    a = Animation(color)
    a._internalDelay = _internalDelay
    #console.set_color(*color)  
    print 'Animation: {} fps={} gostop={}'.format(name, fps, gostop)
    #console.set_color()  
    kwargs={'name':name, 'fps':fps, 'threaded':True, 'gostop':gostop}
    a.run(**kwargs)
    return a
    
    
#def nwaitTillFrame(fps=1):
#    s = time.time()
#    f = s * fps
#    nf = math.ceil(f)
#    breaktime = nf / fps
#    if (breaktime - s) > 0.01:
#        time.sleep(breaktime - s - .01)
#    while True:
#        t = time.time()
#        if t >= breaktime:
#            return t
    
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
    
def waitInGap(t, gostop, waitfunc=time.sleep):
    if gostop:
        tmod = t % gostop[-1]
        indtoright = bisect.bisect(gostop, tmod)
        if indtoright % 2 == 0:
            goal = gostop[indtoright]
            twait = goal - tmod
            #print 'WAIT for {} till {}'.format(twait, goal)
            waitfunc(twait)
        else:
            #print 'GO'
            pass
        return time.time() - now >= gostop[-1]
    else:
        return False
          
    

#def buzzwaitTillFrame(fps=1):
#    s = time.time()
#    f = s * fps
#    nf = math.ceil(f)
#    breaktime = nf / fps
#    while True:
#        if time.time() >= breaktime:
#            return breaktime
#            #return time.time()

#console.set_color()  
#console.clear()
# wait till integral number of seconds
now = waitTillFrame() # global
now = time.time() # global
print now

anlist = []
anlist.append(schedanim('fancy worm', 1, (0, 0, 1), [0, 10]))
#anlist.append(schedanim('big bloom', 4, (1, 0, 0), [0, 8], _internalDelay=random))
anlist.append(schedanim('big bloom', 4, (1, 0, 0), [0, 8]))
anlist.append(schedanim('dimmer', 2, (0, 1, 0), [4, 7]))
anlist.append(schedanim('dumb', 5, (0, 1, 1), [0,1,2, 4,5]))

   
while any([not a.animComplete for a in anlist]):
    pass
  
time.sleep(.01)  # time for _Timer thread to die
print threading.enumerate()

h = 100*(len(anlist) + 2)
maxt = max([a.updateTimes[-1] for a in anlist])

#w=2000
##print w, h
#canvas.set_size(w + 200, h)
#for i, a  in enumerate(anlist):
#    for t in a.updateTimes:
#        plotDot(w * t / maxt, 100 * (i+1), color=a.textcol )


import matplotlib.pyplot as plt
plt.clf()
col = 'brgcwk'
[plt.plot(a.updateTimes, [i] * len(a.updateTimes), col[i%6]+'o') for i, a in enumerate(anlist)]
ax = plt.axis()
delx = .01 * (ax[1] - ax[0])
plt.axis([ax[0]-delx, ax[1]+delx, ax[2]-1, ax[3]+1])
#plt.title("Master Animation Step Count {}".format(masteranimation._step))
    
# threaded=False or threaded=True and joinThread=True will wait till finish before next stmt
#a1.run('ttt', fps=1, max_steps=15, threaded=True)
#a2.run('bbb', fps=10, max_steps=15, threaded=False)
