
"""
For testing and development
Animation class to handle timing and be able to start
via a Timer
"""


from bibliopixel.led import LEDMatrix
from bibliopixel.led import LEDStrip
from bibliopixel.drivers.visualizer import DriverVisualizer, ChannelOrder
from bibliopixel.drivers.dummy_driver import DriverDummy

import time
from random import randint, random
import threading
from threading import Timer
import math
import types
from bibliopixel import log
import re



class animThread(threading.Thread):
    def __init__(self, anim, args):
        super(animThread, self).__init__()
        self.setDaemon(True)
        self._anim = anim
        self._args = args

    def run(self):
        log.logger.info("Starting thread...bbbbb")
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
        self.now = time.time()
	
    def preRun(self, amt=1):
        self._led.all_off()
        pass

    def postRun(self):
        self._led.resetMasterBrightness()
        pass
    
    def preStep(self, amt=1):
        pass

    def postStep(self, amt=1):
        pass


    def step(self, amt=1):
        raise RuntimeError("Base class step() called. This shouldn't happen")
        pass
        
    def stopThread(self, wait=False):
        # NOTE _stopEvent is attribute wether or not animation is threaded
        # so should set the flag in all cases
       print '{:.3f} Stopping {}'.format(time.time() - self.now, id(self))
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
        print fps, id(self)
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
            self.postStep(amt)

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
            self.updateTimes.append(startupdate - self.now)
            #console.set_color(*self.textcol)
            #print '{:.4f} {} update step {}'.format(startupdate - now, name, cur_step)
            #console.set_color()
            if updateWithPush:
                self._led.update()
                pass
            else:
                self._led._updatenow.set()   # signals masterAnimation to act
                pass
            
            cur_step += 1

        self.animComplete = True
        self.postRun()

        if self._callback:
            self._callback(self)

    def run(self, amt = 1, fps=None, sleep=None, max_steps = 0, untilComplete = False, max_cycles = 0, threaded = False, joinThread = False, callback=None, updateWithPush=True):
        log.logger.info('{:.3f} Starting {}'.format(time.time() - self.now, id(self)))
        print '{:.3f} Starting {}'.format(time.time() - self.now, id(self))
        # TODO check orig if first run threaded and second time unthreaded may fail
        #   this is not a complete fix see BugAnimation.py 
        #   problems can happen is there is not enough delay between
        #   stopping it and restarting it (on my PC needed delay of )
        #   no problem if stop with stopThread(wait=True)
        self._threaded = threaded
        #if self._threaded:
        self._stopEvent.clear()
        self._callback = callback

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



def waitTillFrame(fps=1, waitfunc=time.sleep):
    # TODO the else part needs looking at as jumps to inf fps
    if fps < 1000:
        waitfunc(.001) # need min wait time
        s = time.time()
        f = s * fps # number of elapsed frames (fractional)
        nf = math.ceil(f) # the next integral frame
        breaktime = nf / fps
        #print breaktime - s
        waitfunc(breaktime - s)
    else:
        print 'no'
        breaktime = 0
    return breaktime
    #return time.time()
    
class OffAnim(BaseAnimation):
    def __init__(self, led, timeout=10):
        super(OffAnim, self).__init__(led)
        self._internalDelay = timeout * 1000

    def step(self, amt=1):
        self._led.all_off()

class AnimationQueue(BaseAnimation):
    def __init__(self, led, anims=None):
        super(AnimationQueue, self).__init__(led)
        if anims == None:
            anims = []
        self.anims = anims
        self.curAnim = None
        self.animIndex = 0;
        self._internalDelay = 0 #never wait
        self.fps = None
        self.untilComplete = False

    #overriding to handle all the animations
    def stopThread(self, wait = False):
        for a,r in self.anims:
            #a bit of a hack. they aren't threaded, but stops them anyway
            a._stopEvent.set()
        super(AnimationQueue, self).stopThread(wait)

    def addAnim(self, anim, amt = 1, fps=None, max_steps = 0, untilComplete = False, max_cycles = 0):
        a = (
            anim,
            {
                "amt": amt,
                "fps": fps,
                "max_steps": max_steps,
                "untilComplete": untilComplete,
                "max_cycles": max_cycles
            }
        )
        self.anims.append(a)

    def preRun(self, amt=1):
        if len(self.anims) == 0:
            raise Exception("Must provide at least one animation.")
        self.animIndex = -1

    def run(self, amt = 1, fps=None, sleep=None, max_steps = 0, untilComplete = False, max_cycles = 0, threaded = False, joinThread = False, callback=None):
        self.fps = fps
        self.untilComplete = untilComplete
        self.max_cycles = max_cycles
        super(AnimationQueue, self).run(amt = 1, fps=None, sleep=None, max_steps = 0, untilComplete = untilComplete, max_cycles = max_cycles, threaded = threaded, joinThread = joinThread, callback=callback)

    def step(self, amt=1):
        self.animIndex += 1
        if self.animIndex >= len(self.anims):
            if self.untilComplete and self.max_cycles <= 1:
                self.animComplete = True
            else:
                self.max_cycles -= 1
                self.animIndex = 0

        if not self.animComplete:
            self.curAnim = self.anims[self.animIndex]

            anim, run = self.curAnim
            run['threaded'] = False
            run['joinThread'] = False
            run['callback'] = None

            if run['fps'] == None and self.fps != None:
                run['fps'] = self.fps
            anim.run(**(run))


class BaseStripAnim(BaseAnimation):
    def __init__(self, led, start = 0, end = -1):
        super(BaseStripAnim, self).__init__(led)

        if not isinstance(led, LEDStrip):
            raise RuntimeError("Must use LEDStrip with Strip Animations!")

        self._start = start
        self._end = end
        if self._start < 0:
            self._start = 0
        if self._end < 0 or self._end > self._led.lastIndex:
            self._end = self._led.lastIndex

        self._size = self._end - self._start + 1

class BaseMatrixAnim(BaseAnimation):
    def __init__(self, led, width=0, height=0, startX=0, startY=0):
        super(BaseMatrixAnim, self).__init__(led)
        if not isinstance(led, LEDMatrix):
            raise RuntimeError("Must use LEDMatrix with Matrix Animations!")

        if width == 0:
            self.width = led.width
        else:
            self.width = width

        if height == 0:
            self.height = led.height
        else:
            self.height = height

        self.startX = startX
        self.startY = startY

class MasterAnimation(BaseMatrixAnim):
    """
    NOTE this version requires a modified BaseAnimation class
    ma = MasterAnimation(ledmaster, animTracks, runtime=1)
    Runs a number of animation tracks concurrently. 
    animTracks is list of tuples
          (animation with unique led, pixmap, pixheights, fps)
    All the animations in animTracks will run for runtime. Each of the
    animations, a, is mapped into ledmaster by its pixmap and conflicts 
    resolved by pixheights.
    For each tuple in animTracks consists of:
       animation e.g. a = Wave(LEDStrip(Driver...(num ..), ...)
           All of the animations in animTracks must have distinct instances
               of LEDStrip, LEDMatrix, ...!
           TODO fix this!
           Any Driver should be ok. Specifying threaded=False is recommended
              but it probably makes no difference. The updating is very
              fast as it is only signally MasterAnimation to act. 
       pixmap is list of size a._led.numLEDs of pixel indices of ledmaster
         if pixmap is None, it will be replaced by range(a._led.numLEDs)
       pixheights is list of size a._led.numLEDs of floats. Highest pixels
         are the ones that display. In case of ties, xor is used
         if pixheights is one value, pixheights is replaced by 
         the constant list. If pixheights is None the constant is 0
       fps a int or None for frames per second for this animation
          
    ma.run(fps=None, threaded=False) will run all the animiation tracks
       concurrently and wait till the runtime is over.       
    if fps is set faster frames from the tracks will be skipped. 
   
    if threaded is True is will not wait. 
    To wait use:
    while not masteranimation.stopped():
        pass
    """
    def __init__(self, led, animTracks, runtime=10, start=0, end=-1):
        super(MasterAnimation, self).__init__(led, start, end)
        
        # Early idea but don't like breaking _led 
        # XXX a replacement update function for animations in animTracks
        # XXXdef __update(self):
        # XXX   self._updatenow.set() 
           
        if not isinstance(animTracks, list):
            animTracks = [animTracks]
        self._animTracks = animTracks
        # modify the update methods of led and add threading Event atribute
        self._ledcopies = []
        #XXX self._restoreupdates = []
        
        # for all animations' leds add attributes: _updatenow, pixmap, pixheights
        ledcheck = set()
        self.ledsunique = True
        for a, pixmap, pixheights, f, start, stop in self._animTracks:
            # make list of the distinct ._led used by the animation
            #  and attach threading.Event() atribute to them
            if id(a._led) in ledcheck:
                self.ledsunique = False
            else:
                ledcheck.add(id(a._led))
                self._ledcopies.append(a._led)
                a._led._updatenow = threading.Event()
            
            #XXXself._restoreupdates.append(a._led.update)
            #XXXa._led.update = new.instancemethod(__update, a._led, None)
            # note if two animation tracks use the same _led, the last
            # will overwrite if not None
            if pixmap is None and not hasattr(a._led, 'pixmap'):
                a._led.pixmap = range(a._led.numLEDs)
            elif pixmap is not None:
                a._led.pixmap = pixmap  
                
            try:          
                if len(a._led.pixmap) != a._led.numLEDs:
                    raise TypeError()                  
            except TypeError:
                err = 'pixmap must be list same size as LEDs'
                log.logger.error(err)
                raise TypeError
                       
            if pixheights is None and not hasattr(a._led, 'pixheights'):
                a._led.pixheights = None
            elif pixheights is not None:
                a._led.pixheights = pixheights 
                
            err = 'pixheights must be list of values same size as LEDs'        
            if a._led.pixheights == None:
                a._led.pixheights = [0] * a._led.numLEDs
            elif isinstance(a._led.pixheights ,list):
                try:
                    if len(a._led.pixheights) != a._led.numLEDs:
                        raise TypeError()                  
                except TypeError:
                    log.logger.error(err)
                    raise TypeError
            else:
                try:
                    a._led.pixheights = [float(a._led.pixheights)] * a._led.numLEDs
                except ValueError:
                    err = 'pixheights must be list of values same size as LEDs'
                    log.logger.error(err)
                    raise ValueError            
                
#            self._ledcopies.append(a._led)
            
        self._runtime = runtime
        self._idlelist = []
        self.timedata = [[] for _  in self._animTracks] # [[]] * k NOT define k different lists!
        self._led.pixheights = [0] * self._led.numLEDs
        

    #overriding to handle all the animations
    def stopThread(self, wait = False):
        for w, pm, ph, f in self._animTracks:
            w._stopEvent.set()
        super(MasterAnimation, self).stopThread(wait)


    def preRun(self, amt=1):
        super(MasterAnimation, self).preRun(amt)
        self.starttime = time.time()
        # starts all the animations at the same time
#        for a, pm, ph, fps in self._animTracks:
#            a.run(fps=fps, max_steps=self._runtime * f, threaded = True, updateWithPush=False)
        # use threading.Timer to schedual start and stop
        for a, pm, ph, fps, start, stop  in self._animTracks:
            # must have threaded True
            t1 = Timer(start, a.run, kwargs={'fps':fps, 'threaded':True, 'updateWithPush':False, 'untilComplete':False})
            t2 = Timer(stop, a.stopThread, ())
            #waitTillFrame(fps)
            t1.start()
            t2.start()


        #print "In preRUN THREADS: " + ",".join([re.sub('<class |,|bibliopixel.\w*.|>', '', str(s.__class__)) for s in threading.enumerate()])

    def preStep(self, amt=1):
        # only step the master thread when something from ledcopies
        self._idlelist = [True] # to insure goes thru while loop at least once
        while all(self._idlelist):
            self._idlelist = [not ledcopy._updatenow.isSet() for ledcopy in self._ledcopies]
            #print self._idlelist
            if self._stopEvent.isSet() | all([a.stopped() for a, pm, ph, f, start, stop in self._animTracks]):
                self.animComplete = True
                #print all([a.stopped() for a, pm, pn, f in self._animTracks])
                #print 'breaking out'
                break
        self.activeanimind = [i for i, x in enumerate(self._idlelist) if x == False]
        # keep list of pixels in the active animations pixmaps
        # TODO maybe - keep track of pixels that are actually changed
        #    this would require looking at each animations step so costly
        self.activepixels = set()
        for i in self.activeanimind:
            self.activepixels = self.activepixels.union(set(self._ledcopies[i].pixmap))
#
    def postStep(self, amt=1):
        # clear the ones found in preStep
        #print len(self.activeanimind)
        [self._ledcopies[i]._updatenow.clear() for i in self.activeanimind]
        #self.animComplete = all([a.stopped() for a, f in self._animTracks])
        #print "In postStep animComplete {}".format(self.animComplete)

    def step(self, amt=1):
        """
        combines the buffers from the slave led's
        which then gets sent to led via update
        """
        def xortuple(a, b):
            return tuple(a[i] ^ b[i] for i in range(len(a)))
        # For checking if all the animations have their frames looked at
        #print "Anim {} at {:5g}".format(self.activeanimind, 1000*(time.time() - starttime))
 
       # save times activated for each animation
        [self.timedata[i].append(1000*(time.time() - self.starttime)) for i, x in enumerate(self._idlelist) if x == False]

        self._led.pixheights = [-10000] * self._led.numLEDs
        for ledcopy in self._ledcopies:
            # deals with all the pixels from each animation
            #for pixind, pix in enumerate(ledcopy.pixmap):
            # only deal with pixels that possibly could have been changed
            # i.e in union of pixmap of activeanimations
            active = ((pixind, pix) for pixind, pix in enumerate(ledcopy.pixmap) 
                                    if pix in self.activepixels)
            for pixind, pix in active:
                if self._led.pixheights[pix] == ledcopy.pixheights[pixind]:
                    self._led._set_base(pix,
                            xortuple(self._led._get_base(pix), ledcopy._get_push(pixind)))
                elif self._led.pixheights[pix] < ledcopy.pixheights[pixind]:
                    self._led._set_base(pix, ledcopy._get_push(pixind))
                    self._led.pixheights[pix] = ledcopy.pixheights[pixind]
        self._step += 1


    def run(self, amt = 1, fps=None, sleep=None, max_steps = 0, untilComplete = True, max_cycles = 0, threaded = True, joinThread = False, callback=None):
        super(MasterAnimation, self).run(amt = 1, fps=fps, sleep=None, max_steps = max_steps, untilComplete = untilComplete, max_cycles = 0, threaded = threaded, joinThread = joinThread, callback=callback)
#        while not self.animComplete:
#            pass

class Worm(BaseStripAnim):
    """
    colors a list the worm segment (starting with head) colors
    path a list of the LED indices over which the worm will travel
    cyclelen controls speed, worm movement only when LED upload
    cycles == 0 mod cyclelen
    height (of worm segments) is same length as colors: higher
    value worms segments go over top of lower value worms  
    Default is for worm on full strip
    Note the worms state is not a direct function of self._step, but
    rather self._headpostion which is initialized. So subsequent worm.run()
    will start where a previous call to worm.run() finished. 
    """
    def __init__(self, led, colors, path=None, cyclelen=1, direction=1,
                 height=None, start=0, end=-1):
        super(Worm, self).__init__(led, start, end)
        if path is None:
            path = range(led.numLEDs)
        self._path = path        
        if height is None:
            height = [0]*len(colors)
        elif type(height) == int:
            height = [height]*len(colors)
        self._colors = colors[:] # protect argument from change
        self._colors.append((0, 0, 0))  # add blank seqment to end worm
        self._cyclelen = cyclelen
        self._height = height[:] # protect argument from change
        self._height.append(-1)    # add lowest value for height
        self._activecount = 0
        self._direction = direction
        self._headposition = -self._direction
        #print self._colors
        #print self._height

    def step(self, amt=1):
        if self._activecount == 0:
            self._headposition += amt*self._direction
            self._headposition %= len(self._path)
            # Put worm into strip and blank end
            segpos = self._headposition
            for x in range(len(self._colors)):
                if True:
                    self._led.set(self._path[segpos], self._colors[x])
                    try:
                        self._led.pixheights[self._path[segpos]] = self._height[x]
                    except AttributeError:
                        pass # if _led can't deal with pixheights
                segpos -= self._direction
                segpos %= len(self._path)
        self._activecount += amt
        self._activecount %= self._cyclelen
        self._step += amt

def pathgen(nleft=0, nright=15, nbot=0, ntop=9, shift=0, turns=10, rounds=16):
    """
    A path around a rectangle from strip wound helically
    10 turns high by 16 round.
    rounds * turns must be number of pixels on strip
    nleft and nright is from 0 to rounds-1, 
    nbot and ntop from 0 to turns-1
    """
    def ind(x, y):
        return x + y * rounds
        
    assert 0 <= nleft <= nright -1 <= rounds and 0 <= nbot <= ntop -1 <= turns
    
    nled = rounds*turns
    sleft = range(ind(nleft, nbot), ind(nleft, ntop), rounds)
    tp = range(ind(nleft, ntop), ind(nright, ntop), 1)
    sright = range(ind(nright, ntop), ind(nright, nbot), -rounds)
    bt = range(ind(nright, nbot), ind(nleft, nbot), -1)
    path = sleft+tp+sright+bt
    if len(path) == 0:
        path = [ind(nleft, nbot)]
    path = map(lambda x: (shift+x) % nled, path)
    log.logger.info("pathgen({}, {}, {}, {}, {}) is {}".format(nleft, nright, nbot, ntop, shift, path))
    return path 



if __name__ == '__main__': 
    
    
    
    drivermaster = DriverVisualizer(160, pixelSize=62, stayTop=True, maxWindowWidth=1024)
    ledmaster = LEDMatrix(drivermaster, width=16, height=10, threadedUpdate=False)
    
    # Set up animations that will run concurrently
    # Some worms
    # segment colors
    
    lnin = [255, 222, 200, 150, 125]
    bluedimming = [(0, 0, i) for i in lnin]
    reddimming = [(i, 0, 0) for i in lnin]
    greendimming = [(0, i, 0) for i in lnin]
    cyandimming = [(0, i, i) for i in lnin]
    whitedimming = [(i, i, i) for i in lnin]
    
    # Worm arguments
    wormblue = (bluedimming, None, 1, 1, 6)
    wormred = (reddimming, None, 1, 1, 2)
    wormgreen = (greendimming, None, 1, 1, 3)
    wormcyan = (cyandimming, None, 1, 1, 4)
    wormwhite = (whitedimming, None, 1, -1, 5)
    
    # Worm pixmaps
    wormbluepixmap = pathgen(3, 12, 0, 9)
    wormredpixmap = pathgen(4, 11, 1, 8)
    wormgreenpixmap = pathgen(5, 10, 2, 7)
    wormcyanpixmap = pathgen(6, 9, 3, 6)
    wormwhitepixmap = pathgen(7, 8, 4, 5)
    
    # List of triple (animation arguments, pixmaps, fps, start, stop)
    wormdatalist = [(wormblue, wormbluepixmap, 10, 0, 10),
                    (wormred, wormredpixmap, 5, 1, 10),
                    (wormgreen, wormgreenpixmap, 19, 2, 8),
                    (wormcyan, wormcyanpixmap, 21, 8, 12),
                    (wormwhite, wormwhitepixmap, 16, 12, 14)]

    wormdatalist = [(wormblue, wormbluepixmap, 1, 0, 10),
                    (wormred, wormredpixmap, 5, 1, 10),
                    (wormgreen, wormgreenpixmap, 4, 2, 8),
                    (wormcyan, wormcyanpixmap, 10, 8, 12),
                    (wormwhite, wormwhitepixmap, 6, 12, 14)]

    wormdatalist = [(wormblue, wormbluepixmap, 4, 0, 10),
                    (wormred, wormredpixmap, 4, 1, 10),
                    (wormgreen, wormgreenpixmap, 4, 2, 8),
                    (wormcyan, wormcyanpixmap, 4, 3, 12),
                    (wormwhite, wormwhitepixmap, 4, 4, 14)]
                    
    #wormdatalist = [(wormblue, wormbluepixmap, 120),
    #                (wormred, wormredpixmap, 30),
    #                (wormgreen, wormgreenpixmap, 40),
    #                (wormcyan, wormcyanpixmap, 60),
    #                (wormwhite, wormwhitepixmap, 20)]
    
    #wormdatalist = [(wormblue, wormbluepixmap, 10)]
    
    # Each animation must have their own leds
    # ledlist is list of unique leds
    ledlist = [LEDStrip(DriverDummy(len(sarg)), threadedUpdate=False, 
                        masterBrightness=255) for aarg, sarg, fps, start, stop in wormdatalist]
    
    #ledlist = [LEDStrip(DriverVisualizer(len(sarg), pixelSize=62, stayTop=True, maxWindowWidth=1024),
    #                      threadedUpdate=False, masterBrightness=255)
    #                      for aarg, sarg, fps in wormdatalist]
    
    # Make the animation list
    # Worm animations as list tuple (animation instances, pixmap, pixheights, fps, start, stop) added
    animationlist = [(Worm(ledlist[i], *wd[0]), wd[1], -1, wd[2], wd[3], wd[4]) for i, wd in enumerate(wormdatalist)]
    # add animation 2 (wormgreen) at end with another time
    animationlist.append((animationlist[2][0],animationlist[2][1],animationlist[2][2], animationlist[2][3], 10, 15 ))

    # wait till integral number of seconds
    now = waitTillFrame() # global
    now = time.time() # global
    print now
    
    now = time.time() # GLOBAL
    masteranimation = MasterAnimation(ledmaster, animationlist, runtime=2)
    masteranimation.run(fps=None, threaded=False)

    # wait here before plotting otherwise data wont be ready
    while not masteranimation.stopped():
        pass

    print 'first anin updates number {}'.format(len(masteranimation._animTracks[0][0].updateTimes))
    # plot timing data collected from all the animations
    # horizontal axis is time in ms
    # vertical are the various animation and dot is when update sent to leds by master
    import matplotlib.pyplot as plt
    plt.clf()
    col = 'brgcwk'
    [plt.plot(masteranimation.timedata[i], [i] * len(masteranimation.timedata[i]), col[i%6]+'o') for i in range(len(animationlist))]
    ax = plt.axis()
    delx = .01 * (ax[1] - ax[0])
    plt.axis([ax[0]-delx, ax[1]+delx, ax[2]-1, ax[3]+1])
    plt.title("Master Animation Step Count {}".format(masteranimation._step))