# -*- coding: utf-8 -*-
"""
Created on Tue Dec 15 13:13:22 2015
http://sebastianraschka.com/Articles/2014_multiprocessing_intro.html
@author: Bill
"""

import multiprocessing as mp
import random
import string

# Define an output queue
output = mp.Queue()

# define a example function
def rand_string(length, output):
    """ Generates a random string of numbers, lower- and uppercase chars. """
    rand_str = ''.join(random.choice(
                    string.ascii_lowercase
                    + string.ascii_uppercase
                    + string.digits)
               for i in range(length))
    output.put(rand_str)
    
def cube(x):
    return x**3
    
if __name__ == '__main__':
    
    
    # Setup a list of processes that we want to run
    processes = [mp.Process(target=rand_string, args=(15, output)) for x in range(10)]
    
    # Run processes
    for p in processes:
        p.start()
    
    # Exit the completed processes
    for p in processes:
        p.join()
    
    # Get process results from the output queue
    results = [output.get() for p in processes]
    
    print(results)
    
    pool = mp.Pool(processes=4)
    results = [pool.apply(cube, args=(x,)) for x in range(1,7)]
    print(results)
    
    results = pool.map(cube, range(1,7))
    print(results)
    
    results = [pool.apply_async(cube, args=(x,)) for x in range(1,7)]
    output = [p.get() for p in results]
    print(output)    
    