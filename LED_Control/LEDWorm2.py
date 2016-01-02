#!/usr/bin/python

# Worms on LED strip
#    160 long wound on a cylinder 10 times round

#import RPi.GPIO as GPIO
import time
import spidev


DEBUG = 0

# Configurable values
spi = spidev.SpiDev()
# note spi.writebytes, spi.xfer2, spi.xfer must take list NOT bytearray or
#   they will fail and terminate program
# Open SPI device
spi.open(0,0)




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
            self.greens[x] = 0x80 | ((1 << ((self.colors[x] >> 3) & 0x7)) - 1)   # G
            self.reds[x] = 0x80 | ((1 << ((self.colors[x] >> 6) & 0x7)) - 1)   # R
            self.blues[x] = 0x80 | ((1 << ((self.colors[x] ) & 0x7)) - 1)   # B               
        self.path = path
        self.cyclelen = cyclelen   # movement only occurs on LED upload cycles == 0 mod cyclelen
        self.height = height
        self.height.append(-1)    # add lowest value for height 
        self.activecount = 0
        self.direction = direction
        self.headposition = -self.direction

    def  move(self,LEDStrip,LEDsegheights):
        if self.activecount == 0:
            self.headposition += self.direction
            self.headposition %= len(self.path)
            # Put worm into strip and blank end
            segpos = self.headposition
            for x in range(len(self.colors)):
                strippos = 3*self.path[segpos]
                if DEBUG: print "x = ",x," segpos = ",segpos," strippos = ",strippos, " colors[x] = ",bin(self.colors[x]), " height[x] = ", self.height[x]
                if self.height[x] >= LEDsegheights[self.path[segpos]]: # or x == len(self.colors) - 1:
                    LEDStrip[strippos] = self.greens[x]
                    LEDStrip[strippos+1] = self.reds[x]
                    LEDStrip[strippos+2] = self.blues[x]
                    LEDsegheights[self.path[segpos]] = self.height[x]
                segpos -= self.direction
                segpos %= len(self.path)
        self.activecount += 1
        self.activecount %= self.cyclelen


strip_len = 160  # this is the length of the payload
numzerobytes = (strip_len-1)/32 + 1 # number of zero bytes needed to reset
reset = bytearray(numzerobytes)
clear = bytearray(3*strip_len)
for cnt in range(len(clear)):
    clear[cnt] = 0x80

# Clear and Reset Strip
if DEBUG: print "Clear and Reset Strip"
LEDStrip = list(clear+reset) # must be array to use spi.xfer2 and acts as the buffer with reset taged on
LEDsegheights = [-1]*strip_len
spi.xfer2(list(reset + clear + reset))

colors = raw_input("Worm colors sep by commas ")
if colors =="":
    colors = [7,6,5,4,3,2,1]
else:
    colors = eval("[" + colors + "]")
path = raw_input("Path in LED strip ")
if path =="":
    #path = range(6,19) + range(39,52)
    #path = range(58)
    path = range(11,160,16)+range(12,160,16)[::-1]+range(13,160,16)+range(14,160,16)[::-1]
else:
    path = eval(path)
    
worm1 = Worm(colors, path, 20, 1, 5)
if DEBUG: print worm1.colors, worm1.path, worm1.cyclelen, worm1.direction, worm1.height

w2c = [0b111000000, 0b110000000, 0b101000000, 0b100000000, 0b011000000, 0b010000000, 0b001000000]
worm2 = Worm(w2c, range(160), 1, -1, 1) 
if DEBUG: print worm2.colors, worm2.path, worm2.cyclelen, worm2.direction, worm2.height

path3 = range(8,100,17)+range(10,100,17)[::-1]
worm3 = Worm([0b010000, 0b010000, 0b010000, 0b001000], path3, 7, -1, 3) 
if DEBUG: print worm3.colors, worm3.path, worm3.cyclelen, worm3.direction, worm3.height

path4 = range(5,100,17)+range(7,100,17)[::-1]
worm4 = Worm([0b010000, 0b010000, 0b010000, 0b001000], path4, 8, -1, 3) 
if DEBUG: print worm4.colors, worm4.path, worm4.cyclelen, worm4.direction, worm4.height

# Loop and dump to the SPI port.
delay = raw_input("delay? ")
if delay == '':
    delay = 1
else:
    delay = eval(delay)

# Set spi speed
spmhz = raw_input("Mhz (41.6 max)? ")
if spmhz == '':
    spmhz = 2
else:
    spmhz = eval(spmhz)

spi.max_speed_hz = int(spmhz*1000000)
print "bits_per_word = {}".format(spi.bits_per_word)
print "cshigh = {}".format(spi.cshigh)
print "loop = {}".format(spi.loop)
print "lsbfirst = {}".format(spi.lsbfirst)
print "max_speed_hz = {}".format(spi. max_speed_hz)
print "mode = {}".format(spi.mode)
print "threewire = {}".format(spi.threewire)



if DEBUG: print "Main Loop..."
while True:
    # Update LEDStrip
    LEDsegheights = [-1]*strip_len
    worm1.move(LEDStrip, LEDsegheights)    
    worm2.move(LEDStrip, LEDsegheights)    
    worm3.move(LEDStrip, LEDsegheights)    
    worm4.move(LEDStrip, LEDsegheights)    
#    spi.writebytes(LEDStrip + reset)
    spi.xfer2(LEDStrip)
    #spidev.flush()
    time.sleep(delay)
    
