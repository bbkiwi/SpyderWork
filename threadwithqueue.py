# -*- coding: utf-8 -*-
"""
Created on Mon Dec 21 20:24:45 2015

@author: Bill
"""

import Queue as queue    # For Python 2.x use 'import Queue as queue'
import threading, time, random

def func(id, result_queue):
    print("Thread", id)
    time.sleep(random.random() * 5)
    result_queue.put((id, 'done', time.time()))

def main():
    q = queue.Queue()
    threads = [ threading.Thread(target=func, args=(i, q)) for i in range(15) ]
    for th in threads:
        th.daemon = True
        th.start()

    result1 = q.get()
    result2 = q.get()

    print("First result: {} Second result: {}".format(result1, result2))

if __name__=='__main__':
    main()