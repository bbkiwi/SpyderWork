#!/usr/bin/env python
from bibliopixel.animation import BaseMatrixAnim
import bibliopixel.colors as colors
import math

class PinwheelShift(BaseMatrixAnim):
    """
    Every 255 steps the led buffer is shifted 1 pixel
    up to 15 and then resets to 0. The effect on an
    LED strip wound in a helix with 16 leds per revolution
    is to rotate the display
    """

    def __init__(self, led, dir = True):
        super(PinwheelShift, self).__init__(led)
        self._center = (self.width / 2, self.height / 2)
        self._dir = dir
        self._len = (self.width*2) + (self.height*2) - 2
	self._shiftamt = 0
	
    def _rotatebuffer(self):
        n = 3*self._shiftamt
        self._led.buffer = self._led.buffer[-n:] + self._led.buffer[:-n]

    def step(self, amt):
        if self._dir:
            s = 255 - self._step
        else:
            s = self._step

        pos = 0
        cX, cY = self._center
        for x in range(self.width):
            c = colors.hue_helper(pos, self._len, s)
            self._led.drawLine(cX, cY, x, 0, c)
            pos += 1

        for y in range(self.height):
            c = colors.hue_helper(pos, self._len, s)
            self._led.drawLine(cX, cY, self.width-1, y, c)
            pos += 1

        for x in range(self.width-1, -1, -1):
            c = colors.hue_helper(pos, self._len, s)
            self._led.drawLine(cX, cY, x, self.height-1, c)
            pos += 1

        for y in range(self.height-1, -1, -1):
            c = colors.hue_helper(pos, self._len, s)
            self._led.drawLine(cX, cY, 0, y, c)
            pos += 1
	    
	# this modifies the _let.buffer directly
	self._rotatebuffer()

        self._step += amt
        if(self._step >= 255):
            self._step = 0
	    self._shiftamt += 1
            if self._shiftamt > 15:
	        self._shiftamt = 0

MANIFEST = [
    {
        "class": PinwheelShift,
        "controller": "matrix",
        "desc": "Rotating rainbow lines that move",
        "display": "Pin-Wheel Helix Strip Shift",
        "id": "PinwheelShift",
        "params": [
            {
                "default": True,
                "help": "On clockwise, Off for counter-clockwise.",
                "id": "dir",
                "label": "Direction",
                "type": "bool"
            }
        ],
        "type": "animation"
    }
]

if __name__ == "__main__":
    from bibliopixel import *
    from bibliopixel.drivers.LPD8806 import DriverLPD8806, ChannelOrder

    #load driver and controller and animation queue
    driver = DriverLPD8806(160,c_order = ChannelOrder.GRB, SPISpeed = 16)
    led = LEDMatrix(driver,16,10,serpentine=False)

    pw = PinwheelShift(led)
    print len(pw._led.buffer)

    #run animation
    pw.run(amt=4, fps=25)
