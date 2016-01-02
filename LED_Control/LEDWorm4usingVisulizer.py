#!/usr/bin/python
"""
Worms on LED strip
   160 long wound on a cylinder 10 times round
   sped up loop by transfering only when a worm had 
   been active
   levels implements expect when tied
"""
import time

# import base classes and driver
from bibliopixel import LEDStrip

# from bibliopixel.drivers.LPD8806 import DriverLPD8806, ChannelOrder
from bibliopixel.drivers.visualizer import DriverVisualizer, ChannelOrder
from WormThreadTest import pathgen

DEBUG = 0

# Configurable values
# spi = spidev.SpiDev()
# note spi.writebytes, spi.xfer2, spi.xfer must take list NOT bytearray or
#   they will fail and terminate program
# Open SPI device
# spi.open(0,0)

driver = DriverVisualizer(160, pixelSize=62, stayTop=True)
#driver = DriverVisualizer(160, pixelSize=31, stayTop=True)

threadedUpdate = True
led = LEDStrip(driver, threadedUpdate=threadedUpdate)



class Worm:
# colors a list the worm segment (starting with head) colors of 9 bit integers first hi 3 bits red level, next 3 green, next 3 blue
#   color levels correspond to 0b0,0b1,0b11,0b111,0b1111,0b11111,0b111111,0b1111111
# path a list of the LED indices over which the worm will travel (from 0 to 159 for 5 m strip)
# cyclelen controls speed, worm movement only when LED upload cycles == 0 mod cyclelen
# height (of worm segments) is same length as colors: higher value worms segments go over top of lower value worms
#    equal value segments are xor'd with LED strip
    def __init__(self, colors, path, cyclelen, direction=1, height=None, strip_len=160):
        numzerobytes = (strip_len-1)/32 + 1 # number of zero bytes needed to reset spi
        reset = bytearray(numzerobytes)  
        clear = bytearray(3*strip_len)
        for cnt in range(len(clear)):
            # clear[cnt] = 0x80
            clear[cnt] = 0x0     
        # LEDStripBuf = list(clear+reset)   
        self.LEDStripBuf = list(clear)  # for using visualizer no reset bytes needed
        self.LEDsegheights = [-1]*strip_len        
        if height==None:
            height = [0]*len(colors)
        elif type(height) == int:
            height = [height]*len(colors)
        self.colors = list(colors) # don't want to change parameter colors
        self.colors.append(0)     # add blank seqment to end worm 
        self.greens = bytearray(len(self.colors))
        self.reds = bytearray(len(self.colors))
        self.blues = bytearray(len(self.colors))
        for x in range(len(self.colors)):
            self.greens[x] =  ((1 << ((self.colors[x] >> 3) & 0x7)) - 1) << 1    # G
            self.reds[x] =    ((1 << ((self.colors[x] >> 6) & 0x7)) - 1) << 1   # R
            self.blues[x] =   ((1 << ((self.colors[x] ) & 0x7)) - 1) << 1   # B               
        self.path = path
        self.cyclelen = cyclelen   # movement only occurs on LED upload cycles == 0 mod cyclelen
        self.height = list(height) # don't want to change parameter height
        self.height.append(-1)    # add lowest value for height 
        self.activecount = 0
        self.direction = direction
        self.headposition = -self.direction

    def  move(self):
        self.pixchanged = set() # empty set
        self.acted = self.activecount == 0
        if self.acted:
            self.headposition += self.direction
            self.headposition %= len(self.path)
            # Put worm into strip and blank end
            segpos = self.headposition
            for x in range(len(self.colors)):
                ledpos = self.path[segpos]
                strippos = 3 * ledpos
                self.LEDStripBuf[strippos] = self.reds[x]
                self.LEDStripBuf[strippos+1] = self.greens[x]
                self.LEDStripBuf[strippos+2] = self.blues[x]
                self.LEDsegheights[ledpos] = self.height[x]
                self.pixchanged.add(ledpos)
                segpos -= self.direction
                segpos %= len(self.path)
        self.activecount += 1
        self.activecount %= self.cyclelen





strip_len = 160  # this is the length of the payload
numzerobytes = (strip_len-1)/32 + 1 # number of zero bytes needed to reset spi
reset = bytearray(numzerobytes)  

clear = bytearray(3*strip_len)
for cnt in range(len(clear)):
    # clear[cnt] = 0x80
    clear[cnt] = 0x0

# Clear and Reset Strip
if DEBUG: print "Clear and Reset Strip"
# LEDStripBuf = list(clear+reset)   
LEDStripBuf = list(clear)  # for using visualizer no reset bytes needed
#LEDsegheights = [-1]*strip_len
# spi.xfer2(list(reset + clear + reset))


lnin = [7,7,6,6,6,5,5]
#lnin = lnin * 10

bluedimming = [i for i in lnin]
reddimming = [8*8*i for i in lnin]
greendimming = [8*i for i in lnin]
cyandimming = [8*i+i for i in lnin]
whitedimming = [8*8*i + 8*i + i for i in lnin]


wormblue = Worm(bluedimming, pathgen(5, 10, 0, 9), 10, 1, 5)
wormred = Worm(reddimming, pathgen(1, 14, 1, 8), 12, 1, 4)
wormgreen = Worm(greendimming, pathgen(2, 13, 2, 7), 15, 1, 6)
wormcyan = Worm(cyandimming, pathgen(3, 12, 3, 6), 20, 1, 2)
wormwhite = Worm(whitedimming, pathgen(4, 11, 4, 5), 30, 1, 1)

wormlist = [wormblue, wormred, wormgreen, wormcyan, wormwhite]

# Loop and dump to the SPI port.
delay = raw_input("delay? ")
if delay == '':
    delay = 0
else:
    delay = eval(delay)

ntest = 1000

if DEBUG: print "Main Loop..."
start = time.clock()
ntran = 0
dum = 0
durupdate, durfixbuf, durspixfer = 0, 0, 0
maxslt = 0
for _ in range(ntest):
    # Update LEDStripBuf
    startframe = time.clock()
    [w.move() for w in wormlist]
    # time.sleep(.003)
    afterupdatetime = time.clock()
    afterfixbuffertime = time.clock()
    afterspixfertime = time.clock()
 
    if any([w.acted for w in wormlist]): 
        ntran += 1
        # find those pixels that got moved and update LEDStripBuf
        pixchanged = list(set.union(*[w.pixchanged for w in wormlist]))
        # print pixchanged
        for pix in pixchanged:
            wormheights = [w.LEDsegheights[pix] for w in wormlist]  
            # TODO handle if worms tied for max height (average?)
            amaxind = wormheights.index(max(wormheights))
            for i in range(3):
                LEDStripBuf[3*pix + i] = wormlist[amaxind].LEDStripBuf[3*pix + i]
        afterfixbuffertime = time.clock()
        led.setBuffer(LEDStripBuf)
        led.update()
        afterspixfertime = time.clock()
	
    durupdate += afterupdatetime - startframe
    durfixbuf += afterfixbuffertime - afterupdatetime
    durspixfer += afterspixfertime - afterfixbuffertime
    # in windows time.clock seems finer resolution but time.sleep works
    # to time truncated to ms
    sleeptime = round(1000*(delay + startframe - time.clock()))/1000
    
    if sleeptime > 0:
        time.sleep(sleeptime)
    maxslt = max(maxslt, sleeptime)
        
  
print maxslt  
    
duration = time.clock() - start
nbytes = len(LEDStripBuf)

print "threadedUpdate = {}".format(threadedUpdate)
print "Took {:.5g}ms for {} frames on strip of {} bytes".format(duration*1000, ntest, nbytes)
tpf = duration/ntest
print "Time per frame is {:.5}ms, fps is {:.5}".format(1000*tpf, 1.0/tpf)
print "Took {:.5g}ms per frame for update {} frames on strip of {} bytes".format(durupdate*1000/ntest, ntest, nbytes)
print "Took {:.5g}ms per frame for fixing buffer on {} frames on strip of {} bytes".format(durfixbuf*1000/ntest, ntran, nbytes)
print "Took {:.5g}ms per frame for led upload and sending to visualizer of buffer on {} frames on strip of {} bytes".format(durspixfer*1000/ntest, ntran, nbytes)
