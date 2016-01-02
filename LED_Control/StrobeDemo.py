#!/usr/bin/env python
import random

#import base classes and driver
#from bibliopixel import *
from bibliopixel import LEDStrip
#from led import LEDStrip

#from bibliopixel.drivers.LPD8806 import DriverLPD8806, ChannelOrder
from bibliopixel.drivers.visualizer import DriverVisualizer, ChannelOrder

#import colors
import bibliopixel.colors

from bibliopixel.animation import BaseStripAnim
#from animation import BaseStripAnim
#from animation import *

from logging import DEBUG, INFO, WARNING, CRITICAL, ERROR
from bibliopixel import log
log.setLogLevel(INFO)

class FireFliesMod(BaseStripAnim):
    """Random pixels flash each cycle and move thru rainbow colors"""
    def __init__(self, led, width = 1, count = 1, start=0, end=-1):
        super(FireFliesMod, self).__init__(led, start, end)
        self._width = width
        self._count = count

    def step(self, amt = 1):
        amt = 1 #anything other than 1 would be just plain silly
        if self._step >= len(bibliopixel.colors.hue_rainbow):
            self._step = 0

        self._led.all_off();

        for i in range(self._count):
            pixel = random.randint(0, self._led.numLEDs - 1)
            color = bibliopixel.colors.hue_rainbow[self._step]

            for i in range(self._width):
                if pixel + i < self._led.numLEDs:
                    self._led.set(pixel + i, color)

        self._step += amt

class StrobeAll(BaseStripAnim):
    """All pixels flash each cycle and move thru rainbow colors"""
    def __init__(self, led, width = 1, count = 1, start=0, end=-1):
        super(StrobeAll, self).__init__(led, start, end)
        self._width = width
        self._count = count

    def step(self, amt = 1):
        amt = 1 #anything other than 1 would be just plain silly
        if self._step >= len(bibliopixel.colors.hue_rainbow):
            self._step = 0

        if self._step % 10 != 0:
	    self._led.all_off();
	else:
	    self._led.fill(bibliopixel.colors.hue_rainbow[0]);
            #self._led.fill(bibliopixel.colors.hue_rainbow[self._step]);

        self._step += amt
	
class OffAll(BaseStripAnim):
    """All pixels turned off testing how concurency works"""
    def __init__(self, led, width = 1, count = 1, start=0, end=-1):
        super(OffAll, self).__init__(led, start, end)
        self._width = width
        self._count = count

    def step(self, amt = 1):
        amt = 1 #anything other than 1 would be just plain silly
        self._led.all_off()
        self._step += amt

class StripTest(BaseStripAnim):
    def __init__(self, led, start=0, end=-1):
        #The base class MUST be initialized by calling super like this
        super(StripTest, self).__init__(led, start, end)
        #Create a color array to use in the animation
        self._colors = [colors.Red, colors.Orange, colors.Yellow, colors.Green, colors.Blue, colors.Indigo]

    def step(self, amt = 1):
        #Fill the strip, with each sucessive color
        for i in range(self._led.numLEDs):
            self._led.set(i, self._colors[(self._step + i) % len(self._colors)])
        #Increment the internal step by the given amount
        self._step += amt

class Worm(BaseStripAnim):
    """
    colors a list the worm segment (starting with head) colors 
    path a list of the LED indices over which the worm will travel 
    cyclelen controls speed, worm movement only when LED upload cycles == 0 mod cyclelen
    height (of worm segments) is same length as colors: higher value worms segments go over top of lower value worms
    """
    def __init__(self, led, colors, path, cyclelen, direction=1, height=None, start=0, end=-1):
	super(Worm, self).__init__(led, start, end)
        if height==None:
            height = [0]*len(colors)
        elif type(height) == int:
            height = [height]*len(colors)
        self._colors = colors
        self._colors.append((0,0,0))     # add blank seqment to end worm        
        self._path = path
        self._cyclelen = cyclelen   # movement only occurs on LED upload cycles == 0 mod cyclelen
        self._height = height
        self._height.append(-1)    # add lowest value for height 
        self._activecount = 0
        self._direction = direction
        self._headposition = -self._direction

    def  step(self, amt=1):
        if self._activecount == 0:
            self._headposition += amt*self._direction
            self._headposition %= len(self._path)
            # Put worm into strip and blank end
            segpos = self._headposition
            for x in range(len(self._colors)):                
                if True: #self._height[x] >= LEDsegheights[self._path[segpos]]: # or x == len(self.colors) - 1:
		    self._led.set(self._path[segpos], self._colors[x])
                    #LEDsegheights[self._path[segpos]] = self._height[x]
                segpos -= self._direction
                segpos %= len(self._path)
        self._activecount += amt
        self._activecount %= self._cyclelen
        self._step += amt

	
#load driver and controller and animation queue
#driver = DriverLPD8806(160,c_order = ChannelOrder.GRB, SPISpeed = 16)
#driver = DriverVisualizer(160, 16, 10, 30, stayTop=True)
# by setting to 160 pixels and size 31 will produce 10 h, 16 wide
#  wrapped
driver = DriverVisualizer(160, pixelSize=31, stayTop=True)

# not much difference whether set threadedUpdate to True or False
#  But CANT stop the updateThread see end of code
#led = LEDStrip(driver, threadedUpdate=True) 
led = LEDStrip(driver)

#print led.buffer
#print len(led.buffer)
#print led.bufByteCount

ledfake = LEDStrip(driver)
def dummy():
    print 'hello'
    
ledfake.update = dummy


# Set up 3 worms - my 160 led strip is wound in a spiral around a cylinder approximately 
# 10 times. Led's x+16 is above and only slightly to left of led x. While led x+17 is above
# and a bit more to right. 

#lnin = [255, 255>>1, 255>>2, 255>>3, 255>>4, 255>>5, 255>>6 ]
lnin = [255, 222, 200, 150, 125]
bluedimming = [(0,0,i) for i in lnin ]
reddimming = [(i,0,0) for i in lnin ]
greendimming = [(0,i,0) for i in lnin ]
cyandimming = [(0,i,i) for i in lnin ]

def pathgen(ntb=0, nlr=0):
    adjtopbot = ntb*16
    ff = nlr+adjtopbot
    sleft = range(ff,160-adjtopbot,16)
    tp = range(sleft[-1]+1,sleft[-1]+15-2*nlr)
    sright = range(tp[-1]+1,0+adjtopbot,-16)
    bt = range(sright[-1]-1,ff,-1)
    path = sleft+tp+sright+bt
    return path


#path = range(11,160,16)+range(12,160,16)[::-1]+range(13,160,16)+range(14,160,16)[::-1]
wormblue = Worm(led, bluedimming, pathgen(0,0), 1, 1)

wormred = Worm(led, reddimming, pathgen(1,1), 1, 1) 

#path3a = range(8,100,17)+range(10,100,17)[::-1]
#path3b = range(5+17,117,17)+range(7+17,117,17)[::-1]
wormgreen = Worm(led, greendimming, pathgen(2,2), 1, 1)
wormcyan = Worm(led, cyandimming, pathgen(3,3), 1, -1)

#run threaded animations
#off1.run(fps=200, max_steps = 1000, threaded=True)
#off2.run(fps=200, max_steps = 1000, threaded=True)
#off3.run(fps=200, max_steps = 1000, threaded=True)
#off4.run(fps=200, max_steps = 1000, threaded=True)
runtime = 10

#print driver._thread.run
#driver._thread.run = updateThread.run

#wormgreen.run(fps=10, max_steps = 30, threaded=True, joinThread=True) # will have to finish before next

wormblue.run(fps=24, max_steps = runtime*24, threaded=True)
wormred.run(fps=20, max_steps = runtime*20, threaded=True)
wormgreen.run(fps=16, max_steps = runtime*16, threaded=True) 
#wormgreenb.run(fps=1, max_steps = 30, threaded=True, joinThread=True) # will have to finish before next
wormcyan.run(fps=12, max_steps = runtime*12, threaded=True) 
#animation1.run(fps=5, max_steps = 30,threaded=True) # runs concurrently with next
#animation2.run(fps=30, max_steps = 100, threaded=True)
# idle and threaded animations will run jointly

# output of each has more than bytes meaning only more than 
#  one worm at a time is in buffer
tt=0
oldb = led.buffer[:]
wormlist = [wormblue, wormred, wormgreen, wormcyan]

# dont need this wait loop but will leave threads running

while not all([w.stopped() for w in wormlist]):
#while not wormblue.stopped() or not wormred.stopped() or not wormgreen.stopped()   or not wormcyan.stopped():
    tt+=1
    #if led.buffer != oldb:
    #    print filter(lambda x:x!=0,led.buffer)
    #    oldb = led.buffer[:]
    #print led.buffer
    pass
print "Ya Hoo"
print tt

# if used with led = LEDStrip(driver, threadedUpdate=True)  
#driver._thread.stop()
#  doesn't stop it!
#driver._thread.join()

