#!/usr/bin/env python
"""
Use version of DriverSlave that has pixmap and pixheights
"""
# import base classes and driver
from bibliopixel import LEDStrip, LEDMatrix
# from bibliopixel.drivers.LPD8806 import DriverLPD8806, ChannelOrder
from bibliopixel.drivers.visualizer import DriverVisualizer, ChannelOrder
from bibliopixel.drivers.dummy_driver import DriverDummy
# import colors
import bibliopixel.colors
from bibliopixel.animation import BaseStripAnim, BaseMatrixAnim, MasterAnimation
from logging import DEBUG, INFO, WARNING, CRITICAL, ERROR
from bibliopixel import log
log.setLogLevel(INFO)
import re
import time
from operator import or_, ior, ixor
# import matplotlib.pyplot as plt
import BiblioPixelAnimations.matrix.bloom as BA
import BiblioPixelAnimations.strip.Wave as WA
import sys

from wormanimclass import Worm, pathgen
# set up led with it's driver for the MasterAnimation
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

# List of triple (animation arguments, pixmaps, fps)
wormdatalist = [(wormblue, wormbluepixmap, 100),
                (wormred, wormredpixmap, 5),
                (wormgreen, wormgreenpixmap, 19),
                (wormcyan, wormcyanpixmap, 21),
                (wormwhite, wormwhitepixmap, 16)]

# Each animation must have their own leds
# ledlist is list of unique leds
ledlist = [LEDStrip(DriverDummy(len(sarg)), threadedUpdate=False, 
                    masterBrightness=255) for aarg, sarg, fps in wormdatalist]

#ledlist = [LEDStrip(DriverVisualizer(len(sarg), pixelSize=62, stayTop=True, maxWindowWidth=1024),
#                      threadedUpdate=False, masterBrightness=255)
#                      for aarg, sarg, fps in wormdatalist]

# Make the animation list
# Worm animations as list tuple (animation instances, pixmap, pixheights, fps) added
animationlist = [(Worm(ledlist[i], *wd[0]), wd[1], -1, wd[2]) for i, wd in enumerate(wormdatalist)]

# needed to run on pixelweb
def genParams():
    return {"start":0, "end":-1, "animcopies": animationlist}

if __name__ == '__main__':
    masteranimation = MasterAnimation(ledmaster, animationlist, runtime=2)

    # Master launches all in animationlist at preRun
    # Master steps when it gets a go ahdead signal from one of the
    # concurrent annimations


    # if give fps for master will skip faster frame
    masteranimation.run(fps=None, threaded=False)
    # if threaded is False will wait otherwise not

    # this will stop as soon as executed, so if threded=True above will
    #   be immediated stopped!
    # masteranimation.stopThread()

    # wait here before plotting otherwise data wont be ready
    while not masteranimation.stopped():
        pass

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
        "display": "Worm Chase",
        "id": "MMasterAnimation0",
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


