#!/usr/bin/env python
"""
Animation class has bug if first run threaded and later unthreaded
"""
# import base classes and driver
from bibliopixel import LEDMatrix
# from bibliopixel.drivers.LPD8806 import DriverLPD8806, ChannelOrder
from bibliopixel.drivers.visualizer import DriverVisualizer, ChannelOrder
# import colors
import bibliopixel.colors as colors
from bibliopixel.animation import BaseStripAnim, BaseMatrixAnim
from logging import DEBUG, INFO, WARNING, CRITICAL, ERROR
from bibliopixel import log
log.setLogLevel(WARNING)
import time

import BiblioPixelAnimations.matrix.MatrixRain as MR
import threading


# set up led with it's driver for the MasterAnimation
driver = DriverVisualizer(160, pixelSize=31, stayTop=False)
led = LEDMatrix(driver, width=16, height=10, threadedUpdate=False)
rain = MR.MatrixRain(led, [colors.Green, colors.Cyan])

if __name__ == '__main__': 
    n = 3
    if n == 1:
        """
        run the animation threaded slowly, stop it and run
        again unthreaded but faster. It will stop 
        but the second run will fail to occur
        """
        rain.run(fps=5, threaded=True)
        print threading.enumerate()
        time.sleep(3) # let run for awhile
        rain.stopThread(wait=False) # tell it to stop
        # if no delay it will get to end of program
        # and the second call to rain.run unthreaded does not reset
        # the flag   _stopEvent
        #   so the second run will jump out of the while loop immediately
        #time.sleep(.1) # remove a see what happens
        print threading.enumerate()
        # BUG - however since the flag has been set the following
        # unthreaded rain.run which does not first clear it will not run
        rain.run(fps=30, max_steps=60, threaded=False)
        print threading.enumerate()
        # if no or too short delay, animThread will be left running
    elif n == 2:
        """
        run the animation threaded slowly, stop it and run
        again threaded but faster. The stopping will fail
        if the time to the second run is too short
        """
        rain.run(fps=5, threaded=True)
        print threading.enumerate()
        time.sleep(3) # let run for awhile
        rain.stopThread(wait=False) # tell it to stop
        # if no delay it will get to end of program
        # and the second call to rain.run threaded will reset the flag
        #   before its while loop terminates
        #   so the first thread will continue and not shut down 
        time.sleep(.1) # remove a see what happens
        print threading.enumerate()
        # and since the flag has been cleared before following
        #   and a threaded run clears it anyways
        #   threaded rain.run will run
        rain.run(fps=30, max_steps=60, threaded=True)
        print threading.enumerate()
        # if no or too short delay, animThread will be left running
    elif n == 3:
        rain.run(fps=10, threaded=True)
        print threading.enumerate()
        time.sleep(3) # let run for awhile
        rain.stopThread(wait=False) # tell it to stop no wait
        time.sleep(.1) # manual wait of 1/fps maybe
        # or stop with wait=True and don't need to sleep
        #rain.stopThread(wait=True) # tell it to stop and wait
       
        print threading.enumerate()
        rain._stopEvent.clear() # simulate fix in Animation.py to always clear
        rain.run(fps=30, max_steps=60, threaded=True) # or False
        print threading.enumerate()

 