# -*- coding: utf-8 -*-
"""
Created on Tue Jan 12 14:17:32 2016

@author: Bill
"""

import new


class Z(object):
    def q(self):
        return self

z = Z()

print z.q()

def method(self):
    return self
    
def method2(self):
    print 'hello {}'.format(self)



z.q = new.instancemethod(method2, z, None)

z.q()