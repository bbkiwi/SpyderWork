#!/usr/bin/env python
import threading
# import base classes and driver
from bibliopixel import LEDStrip
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

class MasterAnimation(BaseStripAnim):
    """
    Takes copies of fake leds, combines using heights and mixing to fill and update
    a led
    NEED now ledcopies is list of the leds associated with each animation
    NEED also mapping of the leds into master led (i.e. path list)
    NEED also height of each animations and merging method if same height
    """
    def __init__(self, led, ledcopies, start=0, end=-1):
        super(MasterAnimation, self).__init__(led, start, end)
        if not isinstance(ledcopies, list):
            ledcopies = [ledcopies]
        self._ledcopies = ledcopies
        # self._idlelistinit = [True] * len(ledcopies)
        self._idlelist = []
        #self.timedata = [[]] * len(self._ledcopies) # wrong as '5' empty lists are the same!
        self.timedata = [[] for _ in range(5)]
         
    def preStep(self, amt=1):
        #print 'prestep {}'.format(self._step)
        # only step the master thread when something from ledcopies
        #  has been done i.e. its event _wait must be false (I THINK)
        # TODO is this good code???? or is there a better way to block
        self._idlelist = [True]
        while all(self._idlelist):
            self._idlelist = [not ledcopy.driver[0]._thread._wait.isSet() for ledcopy in self._ledcopies]
            #idlelist = [not ledcopy.driver[0]._thread._wait.wait() for ledcopy in self._ledcopies]
            if self._stopEvent.isSet():
                self.animComplete = True
                print 'breaking out'
                break
            pass
#        
    def postStep(self, amt=1):
        # clear all after the step
        #print 'clearing all'
        #[ledcopy.driver[0]._thread._wait.clear() for ledcopy in self._ledcopies]
        #clear the ones found in preStep
        activewormind = [i for i, x in enumerate(self._idlelist) if x == False]
        [self._ledcopies[i].driver[0]._thread._wait.clear() for i in activewormind]
        pass
 
    def step(self, amt=1):
        """
        combines the buffers from the slave led's
        which then gets sent to led via update
        """
        #activewormind = [i for i, x in enumerate(self._idlelist) if x == False]
        #print "Worm {} at {:5g}".format(activewormind, 1000*(time.time() - starttime))
        # save times activated for each worm         
        [self.timedata[i].append(1000*(time.time() - starttime)) for i, x in enumerate(self._idlelist) if x == False]
        
        #print self._idlelist
        #print type(self._led.buffer)
        #self._led.buffer = self._ledcopies[0].buffer
        self._led.buffer = [0] * 480
        #print type(self._led.buffer)
        for ledcopy in self._ledcopies:
            #self._led.buffer = map(or_, ledcopy.buffer, self._led.buffer)
            #print self._led.buffer
            #print ledcopy.buffer
            self._led.buffer = map(ixor, self._led.buffer, ledcopy.buffer)
        #print 'stepped'
            
        #self._led.buffer = self._ledcopy.buffer
        self._step += 1

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
        self._colors = colors
        self._colors.append((0, 0, 0))  # add blank seqment to end worm
        self._path = path
        self._cyclelen = cyclelen
        self._height = height
        self._height.append(-1)    # add lowest value for height
        self._activecount = 0
        self._direction = direction
        self._headposition = -self._direction

    def step(self, amt=1):
        if self._activecount == 0:
            self._headposition += amt*self._direction
            self._headposition %= len(self._path)
            # Put worm into strip and blank end
            segpos = self._headposition
            for x in range(len(self._colors)):
                if True:  #self._height[x] >= LEDsegheights[self._path[segpos]]: # or x == len(self.colors) - 1:
                    self._led.set(self._path[segpos], self._colors[x])
                    # LEDsegheights[self._path[segpos]] = self._height[x]
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
    drivermaster = DriverVisualizer(160, pixelSize=62, stayTop=False)
    # dummy strips must each have their own slavedriver as thread is attached
    # to the driver
    ledslaves = [LEDStrip(DriverSlave(160, 0), threadedUpdate=True) for _ in range(5)]
    ledmaster = LEDStrip(drivermaster, threadedUpdate=True)
    
    lnin = [255, 222, 200, 150, 125]
    bluedimming = [(0, 0, i) for i in lnin]
    reddimming = [(i, 0, 0) for i in lnin]
    greendimming = [(0, i, 0) for i in lnin]
    cyandimming = [(0, i, i) for i in lnin]
    whitedimming = [(i, i, i) for i in lnin]
    
    wormblue = Worm(ledslaves[0], bluedimming, pathgen(5, 10, 0, 9), 1, 1)
    wormred = Worm(ledslaves[1], reddimming, pathgen(1, 14, 1, 8), 1, 1)
    wormgreen = Worm(ledslaves[2], greendimming, pathgen(2, 13, 2, 7), 1, 1)
    wormcyan = Worm(ledslaves[3], cyandimming, pathgen(3, 12, 3, 6), 1, 1)
    wormwhite = Worm(ledslaves[4], whitedimming, pathgen(4, 11, 4, 5), 1, 1)
    
#    wormblue = Worm(ledslaves[0], bluedimming, pathgen(5, 10, 0, 9), 1, 1)
#    wormred = Worm(ledslaves[0], reddimming, pathgen(1, 14, 1, 8), 1, 1)
#    wormgreen = Worm(ledslaves[0], greendimming, pathgen(2, 13, 2, 7), 1, 1)
#    wormcyan = Worm(ledslaves[0], cyandimming, pathgen(3, 12, 3, 6), 1, 1)
#    wormwhite = Worm(ledslaves[0], whitedimming, pathgen(4, 11, 4, 5), 1, 1)
#
    wormlist = [(wormblue, 24),  (wormred, 20), (wormgreen, 16), (wormcyan, 12), (wormwhite, 8)]
    #wormlist = [(wormblue, 24),  (wormred, 24), (wormgreen, 24), (wormcyan, 24), (wormwhite, 24)]
    #wormlist = [(wormblue, 24)]
    masteranimation = MasterAnimation(ledmaster, [w._led for w, f in wormlist])

    starttime = time.time()
    runtime = 1
    
    # Master steps when it gets a go ahdead signal from one of the
    # concurrent annimations
    masteranimation.run(threaded=True)
     
    # Run all the slave animations and master threaded
    # The slave animations updated their buffers at the correct
    #   time and rather than update, just signal the master they
    #   are ready to be combined and sent to the actual leds
#    for w, f in wormlist:
#        w.run(fps=f, max_steps=runtime*f, threaded=True)
    for w, f in wormlist:
        w.run(fps=f, max_steps=runtime * f, threaded=True)
    
    
    # idle and threaded animations will run jointly
    while not all([w.stopped() for w, f in wormlist]):
        pass    
    
    masteranimation.stopThread(True) # need True
    
    print "Master Animation Step Count {}".format(masteranimation._step)
    ledmaster.waitForUpdate()
    ledmaster.stopUpdateThreads()
    
    [w._led.stopUpdateThreads() for w, f in wormlist]
    
    print threading.enumerate()
    
    plt.clf()
    col = 'brgcw'
    [plt.plot(masteranimation.timedata[i], [i] * len(masteranimation.timedata[i]), col[i]+'o') for i in range(5)]
    ax = plt.axis()
    plt.axis([ax[0]-100, ax[1]+10, ax[2]-1, ax[3]+1])    
    
    
#    while True:
#        pass