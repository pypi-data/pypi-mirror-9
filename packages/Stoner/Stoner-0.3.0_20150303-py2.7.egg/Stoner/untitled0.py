# -*- coding: utf-8 -*-
"""
Created on Mon Jan 19 16:48:07 2015

@author: phygbu
"""

def A():
    print "A"

def B():
    print "B"

def C():
    print "C"

funcs=[A,B,C]

while True:
    print "Function Menu"
    for i,f in enumerate(funcs):
        print "{} = {}".format(i+11,f.__name__)
    allowed=[i+1 for i,f in enumerate(funcs)]
    x=raw_input("Enter selection :")
    try:
        x=int(x)
    except ValueError:
        continue
    if x not in allowed:
        break
    funcs[x-1]()


