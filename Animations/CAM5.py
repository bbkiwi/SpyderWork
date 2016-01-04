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
# Wave arguments
waveblue = ((0,0,255), 1)
wavered = ((0, 255, 0), 1)
wavegreen = ((255, 0, 0), 1)
wavecyan = ((255, 0, 255), 1)
wavewhite = ((255, 255, 255), 1)

# Wave slave driver arguments
wavebluepixmap = pathgen(1, 15, 0, 9)
waveredpixmap = pathgen(1, 14, 1, 8)
wavegreenpixmap = pathgen(2, 13, 2, 7)
wavecyanpixmap = pathgen(3, 12, 3, 6)
wavewhitepixmap = pathgen(4, 11, 4, 5)

# List of triple (animation arguments, slavedriver argument, fps)
wavedatalist = [(waveblue, wavebluepixmap, 5),
                (wavered, waveredpixmap, 5),
                (wavegreen, wavegreenpixmap, 5),
                (wavecyan, wavecyanpixmap, 5),
                (wavewhite, wavewhitepixmap, 5)]

# dummy  LED strips must each have their own slavedrivers
ledslaves = [LEDStrip(DriverSlave(len(sarg), pixmap=sarg, pixheights=-1), threadedUpdate=False) \
             for aarg, sarg, fps in wavedatalist]

# Make the animation list
# Wave animations as list pairs (animation instances, fps) added
animationlist = [(WA.Wave(ledslaves[i], *wd[0]), wd[2]) for i, wd in enumerate(wavedatalist)]

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
        "display": "Waves in Rings", 
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


 