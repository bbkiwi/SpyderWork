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
sys.path.append('D:\Bill\SpyderWork') # to get wormanimclass
from wormanimclass import Worm, pathgen


drivermaster = DriverVisualizer(160, pixelSize=62, stayTop=False, maxWindowWidth=1024)
# drivermaster = DriverVisualizer(160, pixelSize=31, stayTop=False, , maxWindowWidth=512)
ledmaster = LEDStrip(drivermaster, threadedUpdate=False)

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
ledslaves = [LEDStrip(DriverSlave(len(sarg), pixmap=sarg, pixheights=-1), threadedUpdate=False) \
             for aarg, sarg, fps in wormdatalist]

# Make the animation list
# Worm animations as list pairs (animation instances, fps) added
animationlist = [(Worm(ledslaves[i], *wd[0]), wd[2]) for i, wd in enumerate(wormdatalist)]

# add a matrix animation background
ledslaveb = LEDMatrix(DriverSlave(160, None, 0), width=16, height=10,  threadedUpdate=False)
bloom = BA.Bloom(ledslaveb)
animationlist.append((bloom, 10))

# add the wave strip animation on the outside boards
wpixm = pathgen(0, 15, 0, 9)
ledslavew = LEDStrip(DriverSlave(len(wpixm), wpixm, 1),  threadedUpdate=False)
wave = WA.Wave(ledslavew, (255, 0, 255), 1)
animationlist.append((wave, 30))

 
# needed to run on pixelweb     
def genParams():
    return {"start":0, "end":-1, "animcopies": animationlist}

    
if __name__ == '__main__':  
      
    masteranimation = MasterAnimation(ledmaster, animationlist, runtime=1)

    # Master launches all in animationlist at preRun
    # Master steps when it gets a go ahdead signal from one of the
    # concurrent annimations
    masteranimation.run(fps=None, threaded = False)  # if give fps for master will skip faster frames 
    masteranimation.stopThread() 
 
    # plot timing data collected from all the animations
    # horizontal axis is time in ms
    # vertical are the various animation and dot is when update sent to leds by master
    plt.clf()
    col = 'brgcwk'
    [plt.plot(masteranimation.timedata[i], [i] * len(masteranimation.timedata[i]), col[i%6]+'o') for i in range(len(animationlist))]
    ax = plt.axis()
    delx = .01 * (ax[1] - ax[0])
    plt.axis([ax[0]-delx, ax[1]+delx, ax[2]-1, ax[3]+1])    
    plt.title("Master Animation Step Count {}".format(masteranimation._step))

MANIFEST = [
    {
        "class": MasterAnimation, 
        "type": "preset",
        "preset_type": "animation",
        "controller": "matrix", 
        "desc": None, 
        "display": "Strip Master Animation ", 
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


 