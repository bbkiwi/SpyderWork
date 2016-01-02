#!/usr/bin/env python
import threading
import time

# import base classes and driver
from bibliopixel import LEDStrip

# from bibliopixel.drivers.LPD8806 import DriverLPD8806, ChannelOrder
from bibliopixel.drivers.visualizer import DriverVisualizer, ChannelOrder

# import colors
import bibliopixel.colors

from bibliopixel.animation import BaseStripAnim

from logging import DEBUG, INFO, WARNING, CRITICAL, ERROR

from bibliopixel import log
log.setLogLevel(WARNING)

import re

class NoStep(BaseStripAnim):
    """
    Least possible step so will take no time to see
    how long update LED takes
    """
    def __init__(self, led, start=0, end=-1):
        super(NoStep, self).__init__(led, start, end)

    def step(self, amt=1):
        # self._step += amt
        pass



# load driver and controller and animation queue
# driver = DriverLPD8806(160,c_order = ChannelOrder.GRB, SPISpeed = 16)

# by setting to 160 pixels and size 31 will produce 10 h, 16 wide
#  wrapped
#driver = DriverVisualizer(160, pixelSize=31, stayTop=True)
driver = DriverVisualizer(160, pixelSize=62, stayTop=True)

nbytes_load = 3 * 160

log.logger.info('before led instantiation {}'.format(', '.join(re.findall('(?<=<).*?\(.*?(?=,)',str(threading.enumerate())))))

#  True is faster! threadedUpdate to True or False
#  But CANT stop the updateThread see end of code
led = LEDStrip(driver, threadedUpdate=True)
#led = LEDStrip(driver)

log.logger.info('after led instantiation {}'.format(', '.join(re.findall('(?<=<).*?\(.*?(?=,)',str(threading.enumerate())))))



log.logger.info('before animation instantiation {}'.format(', '.join(re.findall('(?<=<).*?\(.*?(?=,)',str(threading.enumerate())))))

nostepAnim = NoStep(led)
#nostepAnim2 = NoStep(led)


log.logger.info('after animation instantiation {}'.format(', '.join(re.findall('(?<=<).*?\(.*?(?=,)',str(threading.enumerate())))))

start = time.time()
ntest = 1000
nostepAnim.run(max_steps=ntest, threaded=True)
#nostepAnim2.run(max_steps=ntest, threaded=True)

# idle and threaded animations will run jointly
log.logger.info('after start animation {}'.format(', '.join(re.findall('(?<=<).*?\(.*?(?=,)',str(threading.enumerate())))))

tt=0
while not nostepAnim.stopped():
    tt += 1

print "Ya Hoo - counted to {} while sending updates only".format(tt)

log.logger.info('after all animations stopped {}'.format(', '.join(re.findall('(?<=<).*?\(.*?(?=,)',str(threading.enumerate())))))


# Not sure is need or want this
led.waitForUpdate()

# NOTE if stop updateThreads while animations still running
#  havoc!
led.stopUpdateThreads()


log.logger.info('after stopped updateThread {}'.format(', '.join(re.findall('(?<=<).*?\(.*?(?=,)',str(threading.enumerate())))))

duration = time.time() - start
nbytes = nbytes_load
print "Took {:.2g}ms for {} transfers strip of {} bytes".format(duration*1000, ntest, nbytes)
tps = duration/ntest
print "Time per strip is {:.3}ms, strips per second is {:.5}".format(1000*tps, 1.0/tps)
tpb = duration/ntest/nbytes
print "Time per byte is {:.5}ms, bytes per second is {:.5}".format(1000*tpb, 1.0/tpb)
