# -*- coding: utf-8 -*-
"""
"""


from bibliopixel import LEDStrip, LEDMatrix
from bibliopixel.drivers.visualizer import DriverVisualizer
from bibliopixel.animation import BaseStripAnim, BaseMatrixAnim,  AnimationQueue
from logging import DEBUG, INFO, WARNING, CRITICAL, ERROR
from bibliopixel import log
log.setLogLevel(INFO)
import time



class Dummy(BaseStripAnim):
    def __init__(self, led, start=0, end=-1):
        super(Dummy, self).__init__(led, start, end)

    def step(self, amt=1):
        pass

if __name__ == '__main__':
    driver = DriverVisualizer(160, pixelSize=10, stayTop=True)
    led = LEDStrip(driver, pixelWidth=1, masterBrightness=100)
    dum = Dummy(led)
    
    dum._led.all_off()
    print "set scaled pixel 0 to full red but it gets scaled"    
    dum._led.set(0,(255, 0 ,0))
    dum._led.update()
    print "But when ask for pixel 0s color get {}".format(dum._led.get(0))
    print "Are they the same? {}".format(dum._led.get(0) == (255, 0, 0))
   