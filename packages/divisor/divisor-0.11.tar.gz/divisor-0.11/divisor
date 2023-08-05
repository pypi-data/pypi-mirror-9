#!/usr/bin/python

# The one minute game challenge.  Make a game in 1 minute.

# (after) I didn't measure it, but this took about 2 minutes.  It's a game.
# Things that embarass me about it:
# - It requires a console to run.  It's not graphical.
# - It feels like edutainment.

import sys
import random

num = 4
while(True):
    print num
    d = raw_input("divisor: ")
    d = int(d)
    if num % d != 0:
        print "Not divisible."
        sys.exit(0)
    if d <= 1:
        print "Too small."
        sys.exit(1)
    if d >= num:
        print "Too large."
        sys.exit(1)
    num += d
    if bool(random.getrandbits(1)):
        num += 1
