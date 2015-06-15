#!/usr/bin/python

import os
import sys
import math
from chandelier import Chandelier, BROADCAST
import function
import generator
import filter
import random
from time import sleep, time
from color import Color

DELAY = .02

device = "/dev/ttyAMA0"
if len(sys.argv) == 2:
    device = sys.argv[1]

ch = Chandelier()
ch.open(device)
ch.off(BROADCAST)
ch.send_entropy()

random.seed()
period_s = 1

#hsv = function.HSV(generator.Sawtooth(.15))
#
#rainbow = function.Rainbow(generator.Sawtooth(.15))
##rainbow.chain(filter.FadeIn(1))
##rainbow.chain(filter.FadeOut(1.0, 5.0))
#
#green = function.ConstantColor(Color(255, 0, 0))
##green.chain(filter.FadeIn(1.0))
#
#purple = function.ConstantColor(Color(0, 0, 255))
##purple.chain(filter.FadeIn(1.0))
##purple.chain(filter.FadeOut(1.0, 5.0))

wobble = function.RandomColorSequence(period_s, random.randint(0, 255))
g = generator.Sin((math.pi * 2) / period_s, -math.pi/2, .5, .5)
g = generator.Sparkle()
wobble.chain(filter.Brightness(g))

ch.run(wobble, DELAY, 20)