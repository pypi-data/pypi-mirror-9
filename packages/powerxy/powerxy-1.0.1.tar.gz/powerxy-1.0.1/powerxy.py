#! /usr/bin/python
""" This script used for  evaluate power(x,y).  x, y can be float or int.
x is the base number, and y is the exponent"""
import string
import sys
if len(sys.argv)<2:
    print "Usage: power doubleX doubleY"
base, exponent = sys.argv[1], sys.argv[2]
b = string.atof(base)
e = string.atof(exponent)
print b**e
