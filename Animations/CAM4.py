#!/usr/bin/env python
"""
Demo using concurrent animation via MasterAnimation
"""
# import base classes and driver
from bibliopixel import LEDStrip, LEDMatrix
# from bibliopixel.drivers.LPD8806 import DriverLPD8806, ChannelOrder
from bibliopixel.drivers.visualizer import DriverVisualizer, ChannelOrder
from bibliopixel.drivers.dummy_driver import DriverDummy
# import colors
import bibliopixel.colors as colors
from bibliopixel.animation import BaseStripAnim, BaseMatrixAnim, MasterAnimation
from logging import DEBUG, INFO, WARNING, CRITICAL, ERROR
from bibliopixel import log
log.setLogLevel(WARNING)
import re
import time
from operator import or_, ior, ixor
# import matplotlib.pyplot as plt
import BiblioPixelAnimations.matrix.MatrixRain as MR
import BiblioPixelAnimations.strip.Wave as WA
import sys


from bibliopixel.tests.wormanimclass import Worm, pathgen
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


ledlist = [LEDStrip(DriverDummy(len(sarg)), threadedUpdate=False, 
                    masterBrightness=255) for aarg, sarg, fps in wormdatalist]

#ledlist = [LEDStrip(DriverVisualizer(len(sarg), pixelSize=62, stayTop=True, maxWindowWidth=1024),
#                      threadedUpdate=False, masterBrightness=255)
#                      for aarg, sarg, fps in wormdatalist]

# Make the animation list
# Worm animations as list tuple (animation instances, pixmap, pixheights, fps) added
animationlist = [(Worm(ledlist[i], *wd[0]), wd[1], None, wd[2]) for i, wd in enumerate(wormdatalist)]

ledslaveb = LEDMatrix(DriverDummy(160), width=16, height=10,  threadedUpdate=False, masterBrightness=100)
rain = MR.MatrixRain(ledslaveb, [colors.Green, colors.Cyan])
#animationlist.append((rain, range(159,-1,-1), 0, 5))
animationlist.append((rain, None, 0, 30))

# needed to run on pixelweb     
def genParams():
    return {"start":0, "end":-1, "animTracks": animationlist}

if __name__ == '__main__':  
    masteranimation = MasterAnimation(ledmaster, animationlist, runtime=5)

    # Master launches all in animationlist at preRun
    # Master steps when it gets a go ahdead signal from one of the
    # concurrent annimations
    masteranimation.run(fps=None, threaded = False)  # if give fps for master will skip faster frames 
    masteranimation.stopThread() 
    
    #import threading
    #print threading.enumerate()
    
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
MANIFEST = [
    {
        "class": MasterAnimation, 
        "type": "preset",
        "preset_type": "animation",
        "controller": "matrix", 
        "desc": None, 
        "display": "Small Worms in ray pattern and dim rain", 
        "id": "MMasterAnimation4", 
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


 