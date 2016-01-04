from bibliopixel.animation import BaseMatrixAnim
import random
import bibliopixel.colors as colors

class FireFliesMod(BaseMatrixAnim):
    """Flashing Rainbow Fireflies in Grid"""
    def __init__(self, led, width = 1, count = 1):
        super(FireFliesMod, self).__init__(led)
        self._width = width
        self._count = count
	
    def step(self, amt = 1):
        #amt controls how colors change as color is
	#    self._step % len(colors.hue_rainbow)
	# so 1 moves slowly thru rainbow

        self._led.all_off();

        for i in range(self._count):
            pixel = random.randint(0, self._led.numLEDs - 1)
            color = colors.hue_rainbow[self._step % len(colors.hue_rainbow)]

            for i in range(self._width):
                if pixel + i < self._led.numLEDs:
		    # use base routine
                    self._led._set_base(pixel + i, color)

        self._step += amt


MANIFEST = [
    {
        "class": FireFliesMod, 
        "controller": "matrix", 
        "desc": "Flashing Rainbow Fireflies in Grid (color is step % 256)", 
        "display": "Fire Flies", 
        "id": "FireFliesMod", 
        "params": [
            {
                "default": 1, 
                "help": "", 
                "id": "width", 
                "label": "width of pixel", 
                "type": "int"
            }, 
            {
                "default": 1, 
                "help": "", 
                "id": "count", 
                "label": "Number of flashes per step", 
                "type": "int"
            }
        ], 
        "type": "animation"
    }
]