# -*- coding: utf-8 -*-
"""
Created on Tue Dec 22 22:03:27 2015
https://pymotw.com/2/threading/
"""

import logging
import threading
import time

logging.basicConfig(level=logging.DEBUG,
                    format='(%(threadName)-10s) %(message)s',
                    )
                    
#def wait_for_event(e):
#    """Wait for the event to be set before doing anything"""
#    logging.debug('wait_for_event starting at %3.1f', time.time() - starttime)
#    event_is_set = e.wait()
#    logging.debug('event set: %s at %3.1f', event_is_set, time.time() - starttime)

def wait_for_event(e):
    """Wait for the event to be set before doing anything"""
    logging.debug('wait_for_event starting at %3.1f', time.time() - starttime)
    event_is_set = e.isSet()
    while not event_is_set:
        event_is_set = e.isSet()        
    time.sleep(.001)
    logging.debug('event set: %s at %3.1f', event_is_set, time.time() - starttime)

def wait_for_event_timeout(e, t):
    """Wait t seconds and then timeout"""
    while not e.isSet():
        logging.debug('wait_for_event_timeout starting at %3.1f', time.time() - starttime)
        event_is_set = e.wait(t)
        logging.debug('event set: %s at %3.1f', event_is_set, time.time() - starttime)
        if event_is_set:
            logging.debug('processing event at %3.1f', time.time() - starttime)
        else:
            logging.debug('doing other work at %3.1f', time.time() - starttime)

starttime = time.time()

e = threading.Event()
t1 = threading.Thread(name='block', 
                      target=wait_for_event,
                      args=(e,))
t1.start()

t2 = threading.Thread(name='non-block', 
                      target=wait_for_event_timeout, 
                      args=(e, 2))
t2.start()

logging.debug('Waiting before calling Event.set() at %3.1f', time.time() - starttime)
time.sleep(3.2)
e.set()
logging.debug('Event is set at %3.1f', time.time() - starttime)
pass


