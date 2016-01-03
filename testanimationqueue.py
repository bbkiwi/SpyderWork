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


driver = DriverVisualizer(160, pixelSize=62, stayTop=False, maxWindowWidth=1024)
led = LEDStrip(driver)

animQ = AnimationQueue(led)
w1 = Worm(led, [(255, 100, 50)]*10)
w2 = Worm(led, [(2, 100, 250)]*10)
animQ.addAnim(w1, fps=20, max_steps=200)
animQ.addAnim(w2, fps=10, max_steps = 100)
animQ.run()