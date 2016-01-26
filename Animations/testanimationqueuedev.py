# -*- coding: utf-8 -*-
"""
Created on Sun Jan 03 16:31:41 2016

@author: Bill
"""


from bibliopixel import LEDStrip, LEDMatrix
from bibliopixel.drivers.visualizer import DriverVisualizer, ChannelOrder
import bibliopixel.colors as colors
from bibliopixel.animation import BaseAnimation, BaseStripAnim, BaseMatrixAnim, MasterAnimation
from logging import DEBUG, INFO, WARNING, CRITICAL, ERROR
from bibliopixel import log
log.setLogLevel(WARNING)
import re
import time
import BiblioPixelAnimations.matrix.bloom as BA
import BiblioPixelAnimations.strip.Wave as WA
from bibliopixel.tests.wormanimclass import Worm, pathgen


class AnimationQueue(BaseAnimation):
    def __init__(self, led, anims=None):
        super(AnimationQueue, self).__init__(led)
        if anims == None:
            anims = []
        self.anims = anims
        self.curAnim = None
        self.animIndex = 0;
        self._internalDelay = 0 #never wait
        self.fps = None
        self.untilComplete = False

    #overriding to handle all the animations
    def stopThread(self, wait = False):
        for a,r in self.anims:
            #a bit of a hack. they aren't threaded, but stops them anyway
            a._stopEvent.set()
        super(AnimationQueue, self).stopThread(wait)

    def addAnim(self, anim, amt = 1, fps=None, max_steps = 0, untilComplete = False, max_cycles = 0):
        a = (
            anim,
            {
                "amt": amt,
                "fps": fps,
                "max_steps": max_steps,
                "untilComplete": untilComplete,
                "max_cycles": max_cycles
            }
        )
        self.anims.append(a)

    def preRun(self, amt=1):
        if len(self.anims) == 0:
            raise Exception("Must provide at least one animation.")
        self.animIndex = -1

    def run(self, amt = 1, fps=None, sleep=None, max_steps = 0, untilComplete = False, max_cycles = 0, threaded = False, joinThread = False, callback=None):
        self.fps = fps
        self.untilComplete = untilComplete
        self.max_cycles = max_cycles
        super(AnimationQueue, self).run(amt = 1, fps=None, sleep=None, max_steps = 0, untilComplete = untilComplete, max_cycles = max_cycles, threaded = threaded, joinThread = joinThread, callback=callback)

    def step(self, amt=1):
        self.animIndex += 1
        if self.animIndex >= len(self.anims):
            if self.untilComplete and self.max_cycles <= 1:
                self.animComplete = True
            else:
                self.max_cycles -= 1
                self.animIndex = 0

        if not self.animComplete:
            self.curAnim = self.anims[self.animIndex]

            anim, run = self.curAnim
            run['threaded'] = True
            run['joinThread'] = False
            run['callback'] = None

            if run['fps'] == None and self.fps != None:
                run['fps'] = self.fps
            anim.run(**(run))


class dimLights(BaseStripAnim):
    def __init__(self, led, start=0, end=-1):
        super(dimLights, self).__init__(led, start, end)
        self._dir = -1
        self._brightness = led.masterBrightness

    def preRun(self,amt=1):
        #self._led.fill(self.color)
        self._count = 0


    def step(self, amt=1):

        # self._led.fill(colors.hue2rgb_rainbow(self._count % 255))

        self._brightness +=  self._dir * amt
        if self._brightness < 0:
            self._brightness = 0
            self._dir = 1
        elif self._brightness > 255:
             self._brightness = 255
             self._dir = -1            
             
        self._led.changeBrightness(self._brightness)
        #print "buffer {} unscaled {}".format(self._led.buffer[0:3],  self._led.unscaledbuffer[0:3])
        self._step += amt
        self._count += 1

if __name__ == '__main__':
    driver = DriverVisualizer(160, pixelSize=62, stayTop=False, maxWindowWidth=1024)
    led = LEDStrip(driver, masterBrightness=255, masterBrightnessLimit=200)

    w1 = Worm(led, [(255, 100, 50)]*10)
    w2 = Worm(led, [(2, 100, 250)]*10)
    dim = dimLights(led)

#    animQ.addAnim(w2, fps=10, max_steps=40)
    #animQ.addAnim(dim, amt=5, fps=30, max_steps=70)
#    animQ.addAnim(w1, fps=5, max_steps = 10)
 
 
    animQ = AnimationQueue(led)
    #animQ.addAnim(dim, amt=10, fps=5, max_steps=40)
    animQ.addAnim(w1, fps=5, max_steps=40)
    animQ.addAnim(w2, fps=5, max_steps=20)
                     
    animQ.run(untilComplete=True, max_cycles=2)
               
    
