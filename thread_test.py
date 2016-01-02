# -*- coding: utf-8 -*-
"""
Created on Tue Dec 22 21:41:12 2015
https://stackoverflow.com/questions/2846653/python-multithreading-for-dummies
"""

# thread_test.py
import threading
import time 

class Monitor(threading.Thread):
    def __init__(self, mon):
        threading.Thread.__init__(self)
        self.mon = mon

    def run(self):
        while True:
            if self.mon[0] == 2:
                print "Mon = 2"
                self.mon[0] = 3;
                