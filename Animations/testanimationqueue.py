# -*- coding: utf-8 -*-
"""
Created on Sun Jan 03 16:31:41 2016

@author: Bill
"""


from bibliopixel import LEDStrip, LEDMatrix
from bibliopixel.drivers.visualizer import DriverVisualizer, ChannelOrder
import bibliopixel.colors 
from bibliopixel.animation import BaseStripAnim, BaseMatrixAnim, MasterAnimation, AnimationQueue
from logging import DEBUG, INFO, WARNING, CRITICAL, ERROR
from bibliopixel import log
log.setLogLevel(INFO)
import re
import time
import BiblioPixelAnimations.matrix.bloom as BA
import BiblioPixelAnimations.strip.Wave as WA
from wormanimclass import Worm, pathgen

class dimLights(BaseStripAnim):
    def __init__(self, led, color, start=0, end=-1):
        super(dimLights, self).__init__(led, start, end)
        self.color = color
        self._dir = -1
        self._brightness = 255
        
    def preRun(self,amt=1):
        self._led.fill(self.color)
        
    def step(self, amt=1):      
        self._brightness +=  self._dir * amt
        if self._brightness < 0:
            self._brightness = 0
            self._dir = 1
        elif self._brightness > 255:
             self._brightness = 255
             self._dir = -1
             
        self._led.changeBrightness(self._brightness)
#        self._led.setMasterBrightness(self._brightness) 
#        self._led.setBuffer(self._led.unscaledbuffer)
        self._step += amt        

if __name__ == '__main__':  
    driver = DriverVisualizer(160, pixelSize=62, stayTop=False, maxWindowWidth=1024)
    led = LEDStrip(driver, masterBrightness=100, masterBrightnessLimit=200)
    
    animQ = AnimationQueue(led)
    w1 = Worm(led, [(255, 100, 50)]*10)
    w2 = Worm(led, [(2, 100, 250)]*10)
    dim = dimLights(led, (0, 255, 0))
    
    animQ.addAnim(w1, fps=20, max_steps=20)
    animQ.addAnim(dim, amt=5, fps=30, max_steps=100)
    animQ.addAnim(w2, fps=10, max_steps = 10)
    
    animQ.run()
   
import bibliopixel.colors as colors   
MANIFEST = [
    {
        "class": dimLights, 
        "controller": "strip", 
        "desc": "Changes brightness of fixed color screen", 
        "display": "dimLights", 
        "id": "dimLights", 
        "params": [
           {
                "default": colors.Green, 
                "help": "Solid Color", 
                "id": "color", 
                "label": "color", 
                "type": "color"
            }
        ], 
        "type": "animation"
    }
]