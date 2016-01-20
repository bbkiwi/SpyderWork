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
log.setLogLevel(WARNING)
import re
import time
from operator import or_, ior, ixor
# import matplotlib.pyplot as plt
import BiblioPixelAnimations.matrix.bloom as BA
import BiblioPixelAnimations.strip.Wave as WA
import sys

from bibliopixel.tests.wormanimclass import Worm, pathgen

class dimLights(BaseStripAnim):
    def __init__(self, led, start=0, end=-1):
        super(dimLights, self).__init__(led, start, end)
        self._dir = -1
        self._brightness = led.masterBrightness

    def preRun(self,amt=1):
        #self._led.fill(self.color)
        self._count = 0

    def step(self, amt=1):
        self._brightness +=  self._dir * amt
        if self._brightness < 0:
            self._brightness = 0
            self._dir = 1
        elif self._brightness > 255:
             self._brightness = 255
             self._dir = -1     
        # forces immediate change      
        self._led.changeBrightness(self._brightness)
        # will only show when dimmed animation pushes frame
        #  so want dimmed animation fps faster than dimming fps
        #self._led.setMasterBrightness(self._brightness)
        self._step += amt
        self._count += 1

class shiftPixmap(BaseStripAnim):
    def __init__(self, led, ledmaster, start=0, end=-1):
        super(shiftPixmap, self).__init__(led, start, end)
        self.ledmaster = ledmaster
        
    def step(self, amt=1):
        self.ledmaster.all_off()
        # any routine that moves pixmap
        self._led.pixmap  = [(p + amt) % self.ledmaster.numLEDs for p in self._led.pixmap]

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
wormbluepixmap = pathgen(5, 10, 0, 9)
wormredpixmap = pathgen(4, 11, 1, 8)
wormgreenpixmap = pathgen(5, 10, 2, 7)
wormcyanpixmap = pathgen(6, 9, 3, 6)
wormwhitepixmap = pathgen(7, 8, 4, 5)

# List of triple (animation arguments, pixmaps, fps)
#wormdatalist = [(wormblue, wormbluepixmap, 10),
#                (wormred, wormredpixmap, 5),
#                (wormgreen, wormgreenpixmap, 19),
#                (wormcyan, wormcyanpixmap, 21),
#                (wormwhite, wormwhitepixmap, 16)]
#                
wormdatalist = [(wormblue, wormbluepixmap, 40),
                (wormred, wormredpixmap, 3),
                (wormgreen, wormgreenpixmap, 13),
                (wormcyan, wormcyanpixmap, 6),
                (wormwhite, wormwhitepixmap, 2)]

#wormdatalist = [(wormblue, wormbluepixmap, 10)]

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

dim0 = dimLights(ledlist[0])
shift2 = shiftPixmap(ledlist[2], ledmaster)
dim1 = dimLights(ledlist[1])

# Not work but if below run these as threads does
animationlist.append((dim0, None, None, 10))
animationlist.append((dim1, None, None, 20))
animationlist.append((shift2, None, None, 1))


#animationlist.insert(0,(dim, animationlist[0][1], 7, 120))


# needed to run on pixelweb
def genParams():
    return {"start":0, "end":-1, "animTracks": animationlist}

if __name__ == '__main__':
    runtime = 10
    masteranimation = MasterAnimation(ledmaster, animationlist, runtime=runtime)

    # Master launches all in animationlist at preRun
    # Master steps when it gets a go ahdead signal from one of the
    # concurrent annimations


    # if give fps for master will skip faster frames
    # if all animations in animation list run at same fps using this
    #    as fps will minimize update to ledmaster
    # if fps is faster than those in animation list will get false WARNING
#    dim0.run(fps=10, amt=10, threaded=True, updateWithPush=False)
#    dim1.run(fps=20, amt=20, threaded=True, updateWithPush=False)
#    #shift2.run(fps=fps, max_steps = fps * runtime, threaded=True, updateWithPush=False)
#    shift2.run(fps=1, threaded=True, updateWithPush=False)
    masteranimation.run(fps=None, threaded=False)
    print 'master done'
    dim0.stopThread()
    dim1.stopThread()
    shift2.stopThread()
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
        "display": "Worm Chase with dimming and shifting",
        "id": "WCDS",
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


