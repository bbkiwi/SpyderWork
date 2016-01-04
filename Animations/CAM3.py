#!/usr/bin/env python
"""
Use version of DriverSlave that has pixmap and pixheights
"""
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
# import matplotlib.pyplot as plt
import BiblioPixelAnimations.matrix.bloom as BA
import BiblioPixelAnimations.strip.Wave as WA
import sys

sys.path.append('D:\Bill\SpyderWork') # to get wormanimclass
from wormanimclass import Worm, pathgen
# set up led with it's driver for the MasterAnimation
drivermaster = DriverVisualizer(160, pixelSize=62, stayTop=False, maxWindowWidth=1024)
ledmaster = LEDMatrix(drivermaster, width=16, height=10, threadedUpdate=False)

# Set up animations that will run concurrently
# Some worms
# segment colors

lnin = [200, 100]
bluedimming = [(0, 0, i) for i in lnin]
reddimming = [(i, 0, 0) for i in lnin]
greendimming = [(0, i, 0) for i in lnin]
cyandimming = [(0, i, i) for i in lnin]
whitedimming = [(i, i, i) for i in lnin]

# Worm arguments
wormblue = (bluedimming, None, 1, 1, 2)
wormred = (reddimming, None, 1, 1, 2)
wormgreen = (greendimming, None, 1, 1, 2)
wormcyan = (cyandimming, None, 1, 1, 2)
wormwhite = (whitedimming, None, 1, 1, 2)
wormwhite2 = (whitedimming, None, 1, 1, 2)

# Worm slave driver arguments
wormbluepixmap = range(88,160, 16)
wormredpixmap = range(88,0, -16)
wormgreenpixmap = range(88,160, 17)
wormcyanpixmap = range(88,0, -17)
wormwhitepixmap = range(88,96)
wormwhite2pixmap = range(88,80,-1)

# List of triple (animation arguments, slavedriver argument, fps)
wormdatalist = [(wormblue, wormbluepixmap, 10),
                (wormred, wormredpixmap, 12),
                (wormgreen, wormgreenpixmap, 10),
                (wormcyan, wormcyanpixmap, 12),
                (wormwhite, wormwhitepixmap, 16),
		(wormwhite2, wormwhite2pixmap, 16)]
moredata = [tuple([w, map(lambda x:(x+8)%160, p), f]) for w, p, f in wormdatalist]
wormdatalist.extend(moredata)

# dummy  LED strips must each have their own slavedrivers
ledslaves = [LEDStrip(DriverSlave(len(sarg), pixmap=sarg, pixheights=-1), threadedUpdate=False) \
             for aarg, sarg, fps in wormdatalist]

# Make the animation list
# Worm animations as list pairs (animation instances, fps) added
animationlist = [(Worm(ledslaves[i], *wd[0]), wd[2]) for i, wd in enumerate(wormdatalist)]

# needed to run on pixelweb     
def genParams():
    return {"start":0, "end":-1, "animcopies": animationlist}

if __name__ == '__main__':  
    masteranimation = MasterAnimation(ledmaster, animationlist, runtime=20)

    # Master launches all in animationlist at preRun
    # Master steps when it gets a go ahdead signal from one of the
    # concurrent annimations
    masteranimation.run(fps=None, threaded = False)  # if give fps for master will skip faster frames 
    masteranimation.stopThread() 
    
    #import threading
    #print threading.enumerate()
 
MANIFEST = [
    {
        "class": MasterAnimation, 
        "type": "preset",
        "preset_type": "animation",
        "controller": "matrix", 
        "desc": None, 
        "display": "Small Worms in ray pattern", 
        "id": "MMasterAnimation3", 
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


 