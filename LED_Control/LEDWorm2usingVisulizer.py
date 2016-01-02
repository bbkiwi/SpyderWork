#!/usr/bin/python

# Worms on LED strip
#    160 long wound on a cylinder 10 times round
# use visualizer to display strip and this takes the time of about 127 strips/sec
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

led = LEDStrip(driver, threadedUpdate=True)



class Worm:
# colors a list the worm segment (starting with head) colors of 9 bit integers first hi 3 bits red level, next 3 green, next 3 blue
#   color levels correspond to 0b0,0b1,0b11,0b111,0b1111,0b11111,0b111111,0b1111111
# path a list of the LED indices over which the worm will travel (from 0 to 159 for 5 m strip)
# cyclelen controls speed, worm movement only when LED upload cycles == 0 mod cyclelen
# height (of worm segments) is same length as colors: higher value worms segments go over top of lower value worms
#    equal value segments are xor'd with LED strip
    def __init__(self, colors, path, cyclelen, direction=1, height=None):
        if height==None:
            height = [0]*len(colors)
        elif type(height) == int:
            height = [height]*len(colors)
        self.colors = colors
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
        self.height = height
        self.height.append(-1)    # add lowest value for height 
        self.activecount = 0
        self.direction = direction
        self.headposition = -self.direction

    def  move(self,LEDStripBuf,LEDsegheights):
        self.acted = self.activecount == 0
        if self.acted:
            self.headposition += self.direction
            self.headposition %= len(self.path)
            # Put worm into strip and blank end
            segpos = self.headposition
            for x in range(len(self.colors)):
                strippos = 3*self.path[segpos]
                if DEBUG: print "x = ",x," segpos = ",segpos," strippos = ",strippos, " colors[x] = ",bin(self.colors[x]), " height[x] = ", self.height[x]
                if self.height[x] >= LEDsegheights[self.path[segpos]]: # or x == len(self.colors) - 1:
                    LEDStripBuf[strippos] = self.reds[x]
                    LEDStripBuf[strippos+1] = self.greens[x]
                    LEDStripBuf[strippos+2] = self.blues[x]
                    LEDsegheights[self.path[segpos]] = self.height[x]
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
LEDsegheights = [-1]*strip_len
# spi.xfer2(list(reset + clear + reset))


lnin = [7,7,6,6,6,5,5]
#lnin = lnin * 10

bluedimming = [i for i in lnin]
reddimming = [8*8*i for i in lnin]
greendimming = [8*i for i in lnin]
cyandimming = [8*i+i for i in lnin]
whitedimming = [8*8*i + 8*i + i for i in lnin]


wormblue = Worm(bluedimming, pathgen(0, 15, 0, 9), 10, 1)
wormred = Worm(reddimming, pathgen(1, 14, 1, 8), 12, 1)
wormgreen = Worm(greendimming, pathgen(2, 13, 2, 7), 15, 1)
wormcyan = Worm(cyandimming, pathgen(3, 12, 3, 6), 20, 1)
wormwhite = Worm(whitedimming, pathgen(4, 11, 4, 5), 30, 1)

# Loop and dump to the SPI port.
delay = raw_input("delay? ")
if delay == '':
    delay = 0
else:
    delay = eval(delay)

ntest = 10000

if DEBUG: print "Main Loop..."
start = time.time()
ntran = 0
for _ in range(0, ntest):
    # Update LEDStripBuf
    LEDsegheights = [-1]*strip_len
    wormblue.move(LEDStripBuf, LEDsegheights)    
    wormred.move(LEDStripBuf, LEDsegheights)    
    wormgreen.move(LEDStripBuf, LEDsegheights)    
    wormcyan.move(LEDStripBuf, LEDsegheights)  
    wormwhite.move(LEDStripBuf, LEDsegheights)  
     
    if any([wormblue.acted, wormred.acted, wormgreen.acted, wormcyan.acted, wormwhite.acted]):    
        ntran += 1
        led.setBuffer(LEDStripBuf)
        led.update()
    time.sleep(delay)
    
    
duration = time.time() - start
nbytes = len(LEDStripBuf)
print "Took {:.2g}ms for {} transfers strip of {} bytes".format(duration*1000, ntran, nbytes)
tps = duration/ntran
print "Time per strip is {:.3}ms, strips per second is {:.5}".format(1000*tps, 1.0/tps)
tpb = duration/ntran/nbytes
print "Time per byte is {:.5}ms, bytes per second is {:.5}".format(1000*tpb, 1.0/tpb)
