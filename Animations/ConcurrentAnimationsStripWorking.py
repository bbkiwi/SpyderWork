#!/usr/bin/env python
"""
Use version of DriverSlave that has pixmap and pixheights
"""
import threading
# import base classes and driver
from bibliopixel import LEDStrip, LEDMatrix
# from bibliopixel.drivers.LPD8806 import DriverLPD8806, ChannelOrder
from bibliopixel.drivers.visualizer import DriverVisualizer, ChannelOrder
from bibliopixel.drivers.slave_driver import DriverSlave
# import colors
import bibliopixel.colors
from bibliopixel.animation import BaseStripAnim
from logging import DEBUG, INFO, WARNING, CRITICAL, ERROR
from bibliopixel import log
log.setLogLevel(WARNING)
import re
import time
from operator import or_, ior, ixor
import matplotlib.pyplot as plt
import BiblioPixelAnimations.matrix.bloom as BA


class MasterAnimation(BaseStripAnim):
    """
    Takes copies of fake leds, combines using heights and mixing to fill and update
    a led
    NEED now ledcopies is list of the leds associated with each animation
    NEED also mapping of the leds into master led (i.e. path list)
    NEED also height of each animations and merging method if same height
    """
    def __init__(self, led, animcopies, runtime=10, start=0, end=-1):
        super(MasterAnimation, self).__init__(led, start, end)
        if not isinstance(animcopies, list):
            animcopies = [animcopies]
        self._animcopies = animcopies
        self._ledcopies = [a._led for a, f in animcopies]
        self._runtime = runtime
        self._idlelist = []
        self.timedata = [[] for _ in range(len(self._ledcopies))] # [[]] * 5 NOT define 5 different lists!
        self._led.pixheights = [0] * self._led.numLEDs

    def preRun(self, amt=1): 
        runtime = 5
        super(MasterAnimation, self).preRun(amt)
        self.starttime = time.time()
        for w, f in self._animcopies:
            w.run(fps=f, max_steps=self._runtime * f, threaded = True)
        #print "In preRUN THREADS: " + ",".join([re.sub('<class |,|bibliopixel.\w*.|>', '', str(s.__class__)) for s in threading.enumerate()])
        	
    def preStep(self, amt=1):
        self.animComplete = all([a.stopped() for a, f in self._animcopies])
        #print 'prestep {}'.format(self._step)
        # only step the master thread when something from ledcopies
        #  has been done i.e. its event _wait must be false (I THINK)
        # TODO is this good code???? or is there a better way to block
        self._idlelist = [True] # to insure goes thru while loop at least once
        while all(self._idlelist):
            self._idlelist = [not ledcopy.driver[0]._updatenow.isSet() for ledcopy in self._ledcopies]
            if self._stopEvent.isSet() | self.animComplete:
                self.animComplete = True
                #print 'breaking out'
                break
#        
    def postStep(self, amt=1):
        # clear the ones found in preStep
        activewormind = [i for i, x in enumerate(self._idlelist) if x == False]
        [self._ledcopies[i].driver[0]._updatenow.clear() for i in activewormind]
 
    def step(self, amt=1):
        """
        combines the buffers from the slave led's
        which then gets sent to led via update
        """
        # For checking if all the animations have their framse looked at
        #activewormind = [i for i, x in enumerate(self._idlelist) if x == False]
        #print "Worm {} at {:5g}".format(activewormind, 1000*(time.time() - starttime))
        # save times activated for each worm         
        [self.timedata[i].append(1000*(time.time() - self.starttime)) for i, x in enumerate(self._idlelist) if x == False]
        
        #self._led.buffer = [0] * 480
        self._led.pixheights = [-100] * self._led.numLEDs
        #print type(self._led.buffer)
        for ledcopy in self._ledcopies:
            # self._led.buffer = map(ixor, self._led.buffer, ledcopy.buffer)
            # use pixheights but assume all buffers same size
            # print ledcopy.driver[0].pixheights
            for pix in range(self._led.numLEDs): # TODO improve using pix changed
            #for ledcopy in self._ledcopies:
                if self._led.pixheights[pix] == ledcopy.driver[0].pixheights[pix]:
                    for i in range(3):
                        self._led.buffer[3*pix + i] ^= ledcopy.buffer[3*pix + i]
                elif self._led.pixheights[pix] < ledcopy.driver[0].pixheights[pix]:
                    for i in range(3):
                        self._led.buffer[3*pix + i] = ledcopy.buffer[3*pix + i]
                        self._led.pixheights[pix] = ledcopy.driver[0].pixheights[pix]    
        self._step += 1
        self.animComplete = all([a.stopped() for a, f in self._animcopies])

        
    def run(self, amt = 1, fps=None, sleep=None, max_steps = 0, untilComplete = True, max_cycles = 0, threaded = True, joinThread = False, callback=None):
        # self.fps = fps
        # self.untilComplete = untilComplete
        super(MasterAnimation, self).run(amt = 1, fps=fps, sleep=None, max_steps = max_steps, untilComplete = untilComplete, max_cycles = 0, threaded = True, joinThread = joinThread, callback=callback)
   

class Worm(BaseStripAnim):
    """
    colors a list the worm segment (starting with head) colors
    path a list of the LED indices over which the worm will travel
    cyclelen controls speed, worm movement only when LED upload
    cycles == 0 mod cyclelen
    height (of worm segments) is same length as colors: higher
    value worms segments go over top of lower value worms
    """
    def __init__(self, led, colors, path, cyclelen, direction=1,
                 height=None, start=0, end=-1):
        super(Worm, self).__init__(led, start, end)
        if height is None:
            height = [0]*len(colors)
        elif type(height) == int:
            height = [height]*len(colors)
        self._colors = colors[:] # protect argument from change
        self._colors.append((0, 0, 0))  # add blank seqment to end worm
        self._path = path
        self._cyclelen = cyclelen
        self._height = height
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
                if True:  #self._height[x] >= LEDsegheights[self._path[segpos]]: # or x == len(self.colors) - 1:
                #if self._height[x] >= self._led.driver[0].pixheights[self._path[segpos]]: # or x == len(self.colors) - 1:
                    self._led.set(self._path[segpos], self._colors[x])
                    self._led.driver[0].pixheights[self._path[segpos]] = self._height[x]
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

drivermaster = DriverVisualizer(160, pixelSize=62, stayTop=False, maxWindowWidth=1024)
# using pixelSize 62 and changed code of visualizer.py to have maxWindowWidth=1024
#drivermaster = DriverVisualizer(160, pixelSize=31, stayTop=False)
#ledmaster = LEDStrip(drivermaster, threadedUpdate=True)
ledmaster = LEDStrip(drivermaster)

lnin = [255, 222, 200, 150, 125]
bluedimming = [(0, 0, i) for i in lnin]
bluedimming = [(0, 0, 0) for i in lnin]
reddimming = [(i, 0, 0) for i in lnin]
greendimming = [(0, i, 0) for i in lnin]
cyandimming = [(0, i, i) for i in lnin]
whitedimming = [(i, i, i) for i in lnin]

# Worm arguments
wormblue = (bluedimming, pathgen(5, 10, 0, 9), 1, 1, 6)
wormred = (reddimming, pathgen(1, 14, 1, 8), 1, 1, 2)
wormgreen = (greendimming, pathgen(2, 13, 2, 7), 1, 1, 3)
wormcyan = (cyandimming, pathgen(3, 12, 3, 6), 1, 1, 4)
wormwhite = (whitedimming, pathgen(4, 11, 4, 5), 1, 1, 5)

# List of pair (animation arguments, fps)
wormdatalist = [(wormblue, 24),  (wormred, 20), (wormgreen, 16), (wormcyan, 12), (wormwhite, 8)]
#wormdatalist = [(wormwhite, 8)]
#wormdatalist = []

# dummy strips must each have their own slavedriver as thread is attached
# to the driver
ledslaves = [LEDStrip(DriverSlave(160, pixheights=-1), threadedUpdate=True) for _ in range(len(wormdatalist))]

# Make the Worm animations an list pairs (animation, fps)
wormlist = [(Worm(ledslaves[i], *d[0]), d[1]) for i, d in enumerate(wormdatalist)]

ledslaveb = LEDMatrix(DriverSlave(160, None, 0), width=16, height=10,  threadedUpdate=True)
bloom = BA.Bloom(ledslaveb)
wormlist.append((bloom, 10))

      
def genParams():
    return {"start":0, "end":-1, "animcopies": wormlist}

    
if __name__ == '__main__':  
      
    #masteranimation = MasterAnimation(ledmaster, [w._led for w, f in wormlist])
    masteranimation = MasterAnimation(ledmaster, wormlist, 5)

    
    # Master launches all in wormlist at preRun
    # NOT WORKING past first time????
    # Master steps when it gets a go ahdead signal from one of the
    # concurrent annimations
    masteranimation.run(fps=None)  # if give fps for master will skip faster frames 
     
    # Run all the slave animations and master threaded
    # master starts up slave animations
    # The slave animations update their buffers at the correct
    #   time and rather than update, just signal the master they 
    #   are ready to be combined and sent to the actual leds

    #NEED some time for these to start or fails to work (sometimes) 
    # maybe to prevent calling stopped() before they get going???       
    time.sleep(.001)

    #print threading.enumerate()
    print "After start master THREADS: " + ",".join([re.sub('<class |,|bibliopixel.\w*.|>', '', str(s.__class__)) for s in threading.enumerate()])

    # idle and threaded animations will run jointly
    while not all([w.stopped() for w, f in wormlist]):
        pass    
 
    #time.sleep(.1)
    # stop the master  
    masteranimation.stopThread(True) # need True
   
    print [a.stopped() for a, f in wormlist]
    
    print "After all stopped THREADS: " + ",".join([re.sub('<class |,|bibliopixel.\w*.|>', '', str(s.__class__)) for s in threading.enumerate()])
  
#    
    print "Master Animation Step Count {}".format(masteranimation._step)
#    ledmaster.waitForUpdate()
    ledmaster.stopUpdateThreads()   
    [w._led.stopUpdateThreads() for w, f in wormlist]
#    
    print "After more stops THREADS: " + ",".join([re.sub('<class |,|bibliopixel.\w*.|>', '', str(s.__class__)) for s in threading.enumerate()])

    plt.clf()
    col = 'brgcwk'
    [plt.plot(masteranimation.timedata[i], [i] * len(masteranimation.timedata[i]), col[i%6]+'o') for i in range(len(wormlist))]
    ax = plt.axis()
    delx = .01 * (ax[1] - ax[0])
    plt.axis([ax[0]-delx, ax[1]+delx, ax[2]-1, ax[3]+1])    
    

MANIFEST = [
    {
        "class": MasterAnimation, 
        "type": "preset",
        "preset_type": "animation",
        "controller": "strip", 
        "desc": None, 
        "display": "Strip Master Animation", 
        "id": "SMasterAnimation", 
        "params": [
            {
                "default": 10, 
                "help": "", 
                "id": "runtime", 
                "label": "Runtime", 
                "type": "int"
            }
        ], 
        "preconfig": genParams, 
    }
]


 