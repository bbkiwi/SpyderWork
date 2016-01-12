
"""
Tests: 
Minor bugs related to scaled pixels in Strip and Matrix
and masterBrigthness

setting a given pixel to a given color and then asking for it with get should 
return the same value.
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
    pixelWidth = 10
    masterBrightness = 255
    driver = DriverVisualizer(160, pixelSize=8, stayTop=True)
    led = LEDStrip(driver, pixelWidth=pixelWidth,  masterBrightness=masterBrightness)
    dum = Dummy(led)
      
    print "masterBrightness is {}".format(dum._led.masterBrightness)  
    dum._led.all_off()
    print "Pixel width {}".format(dum._led.pixelWidth) 
    print "Numer of scaled pixels {}".format(dum._led.numLEDs)
    print "set scaled pixel 0 to red and scaled pixel 1 to green"    
    print "these colors are scaled via masterBrightness"    
    dum._led.set(0,(255, 0 ,0))
    dum._led.update()
    px1c = (0, 255 ,0)
    dum._led.set(1, px1c)
    dum._led.update()
    print "But when ask for pixel 0s color get {}".format(dum._led.get(0))
    print "Is it the value we set? {}".format(dum._led.get(0) == (255, 0, 0))
    print "But when ask for pixel 1s color get {}".format(dum._led.get(1))
    print "Is it the value we set? {}".format(dum._led.get(1) == px1c)
