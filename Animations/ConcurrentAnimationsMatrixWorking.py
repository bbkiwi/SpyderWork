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
from bibliopixel.animation import BaseStripAnim, BaseMatrixAnim, MasterAnimation
from logging import DEBUG, INFO, WARNING, CRITICAL, ERROR
from bibliopixel import log
log.setLogLevel(WARNING)
import re
import time
from operator import or_, ior, ixor
import matplotlib.pyplot as plt
import BiblioPixelAnimations.matrix.bloom as BA
import BiblioPixelAnimations.strip.Wave as WA


import sys
import os
# the mock-0.3.1 dir contains testcase.py, testutils.py & mock.py
sys.path.append(re.sub('Animations', '', os.getcwd()))
from wormanimclass import Worm, pathgen


drivermaster = DriverVisualizer(160, pixelSize=62, stayTop=False, maxWindowWidth=1024)
# drivermaster = DriverVisualizer(160, pixelSize=31, stayTop=False, , maxWindowWidth=512)
ledmaster = LEDMatrix(drivermaster)

# segment colors
lnin = [255, 222, 200, 150, 125]
bluedimming = [(0, 0, i) for i in lnin]
reddimming = [(i, 0, 0) for i in lnin]
greendimming = [(0, i, 0) for i in lnin]
cyandimming = [(0, i, i) for i in lnin]
whitedimming = [(i, i, i) for i in lnin]

# Worm arguments = (segment colors, path, cyclelength, direction, height)
wormblue = (bluedimming, None, 1, 1, 6)
wormred = (reddimming, None, 1, 1, 2)
wormgreen = (greendimming, None, 1, 1, 3)
wormcyan = (cyandimming, None, 1, 1, 4)
wormwhite = (whitedimming, None, 1, 1, 5)

# Worm slavedriver argument for pixmap
wormbluepixmap = pathgen(5, 10, 0, 9)
wormredpixmap = pathgen(1, 14, 1, 8)
wormgreenpixmap = pathgen(2, 13, 2, 7)
wormcyanpixmap = pathgen(3, 12, 3, 6)
wormwhitepixmap = pathgen(4, 11, 4, 5)

# List of triple (animation arguments, slavedriver argument, fps)
wormdatalist = [(wormblue, wormbluepixmap, 24),
                (wormred, wormredpixmap, 20),
                (wormgreen, wormgreenpixmap, 16),
                (wormcyan, wormcyanpixmap, 12),
                (wormwhite, wormwhitepixmap, 8)]

# dummy  LED strips must each have their own slavedriver as thread is attached
# to the driver
ledslaves = [LEDStrip(DriverSlave(len(sarg), pixmap=sarg, pixheights=-1), threadedUpdate=True) \
             for aarg, sarg, fps in wormdatalist]

# Make the animation list
# Worm animations as list pairs (animation instances, fps) added
animationlist = [(Worm(ledslaves[i], *wd[0]), wd[2]) for i, wd in enumerate(wormdatalist)]

# add a matrix animation background
ledslaveb = LEDMatrix(DriverSlave(160, None, 0), width=16, height=10,  threadedUpdate=True)
bloom = BA.Bloom(ledslaveb)
animationlist.append((bloom, 10))

# add the wave strip animation on the outside boards
wpixm = pathgen(0, 15, 0, 9)
ledslavew = LEDStrip(DriverSlave(len(wpixm), wpixm, 1),  threadedUpdate=True)
wave = WA.Wave(ledslavew, (255, 0, 255), 1)
animationlist.append((wave, 30))

 
# needed to run on pixelweb     
def genParams():
    return {"start":0, "end":-1, "animcopies": animationlist}

    
if __name__ == '__main__':  
      
    #masteranimation = MasterAnimation(ledmaster, [w._led for w, f in animationlist])
    masteranimation = MasterAnimation(ledmaster, animationlist, runtime=1)

    # Master launches all in animationlist at preRun
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
    while not all([w.stopped() for w, f in animationlist]):
        pass    
 
    #time.sleep(.1)
    # stop the master  
    masteranimation.stopThread(True) # need True
   
    print [a.stopped() for a, f in animationlist]
    
    print "After all stopped THREADS: " + ",".join([re.sub('<class |,|bibliopixel.\w*.|>', '', str(s.__class__)) for s in threading.enumerate()])
  
#    
    print "Master Animation Step Count {}".format(masteranimation._step)
#    ledmaster.waitForUpdate()
    ledmaster.stopUpdateThreads()   
    [w._led.stopUpdateThreads() for w, f in animationlist]
#    
    print "After more stops THREADS: " + ",".join([re.sub('<class |,|bibliopixel.\w*.|>', '', str(s.__class__)) for s in threading.enumerate()])

    # plot timing data collected from all the animations
    # horizontal axis is time in ms
    # vertical are the various animation and dot is when update sent to leds by master
    plt.clf()
    col = 'brgcwk'
    [plt.plot(masteranimation.timedata[i], [i] * len(masteranimation.timedata[i]), col[i%6]+'o') for i in range(len(animationlist))]
    ax = plt.axis()
    delx = .01 * (ax[1] - ax[0])
    plt.axis([ax[0]-delx, ax[1]+delx, ax[2]-1, ax[3]+1])    
    

MANIFEST = [
    {
        "class": MasterAnimation, 
        "type": "preset",
        "preset_type": "animation",
        "controller": "matrix", 
        "desc": None, 
        "display": "Matrix Master Animation ", 
        "id": "MMasterAnimation", 
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


 