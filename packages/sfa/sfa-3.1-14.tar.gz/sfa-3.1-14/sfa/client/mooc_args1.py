#!/usr/bin/env python

from operator import add

def fact (n):
    return 1 if n<=0 else n*fact(n-1)

# on a real number
def polynom (c):
    return 2*x**2+3*x+1

# a list of real numbers
def polynom_sum (l):
    return reduce (add, [ polynom (x) for x in l ] )

# two real numbers
def polynom2 (x,y=1.):
    return 3*x*y**2-3*x**2*y+2

### problem:
#
# write a stub that can be called from the command line like this
#
# stub fact 12
# stub polynom 1.4
# stub polynom_sum 1+1j
# stub
