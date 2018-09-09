#!/usr/bin/env python

import os
import sys
import math
from random import random, randint
from colorsys import hsv_to_rgb
from hippietrap.hippietrap import HippieTrap, BROADCAST, NUM_NODES
from hippietrap.color import Color
from time import sleep, time

STEPS = 500

with HippieTrap() as ch:
    ch.set_brightness(BROADCAST, 100)
    try:
        ch.start_pattern(BROADCAST)
        while True:
            for i in range(15):
                bottle = randint(1, NUM_NODES)
                led = randint(1, 4)
                hue = random()
                rgb = hsv_to_rgb(hue, 1.0, 1.0)
                ch.set_color(bottle, Color(int(255 * rgb[0]), int(255 * rgb[1]), int(255 * rgb[2])))

            ch.send_decay(BROADCAST, 4)
            sleep(.3)

    except KeyboardInterrupt:
        ch.stop_pattern(BROADCAST)
        ch.clear(BROADCAST)
