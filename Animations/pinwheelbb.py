from bibliopixel.animation import BaseMatrixAnim
import bibliopixel.colors as colors

import math

class PinwheelBB(BaseMatrixAnim):
    """
    Every 255 steps the center of rotation is shifted
    horizontally to right side and then resets to left side. 
    """
    def __init__(self, led, dir = True):
        super(PinwheelBB, self).__init__(led)
        self._center = (self.width / 2, self.height / 2)
        self._dir = dir
        self._len = (self.width*2) + (self.height*2) - 2

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

        self._step += amt
        if(self._step >= 255):
            self._step = 0
            cX += 1
	    if cX >= self.width:
	        cX = 1
	    self._center = (cX, cY)



MANIFEST = [
    {
        "class": PinwheelBB,
        "controller": "matrix",
        "desc": "Rotating rainbow lines with center shifting",
        "display": "Pin-Wheel BB",
        "id": "PinwheelBB",
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
