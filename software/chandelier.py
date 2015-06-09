#!/usr/bin/python

import os
import sys
import math
import serial
import struct
import function
import generator
import filter
import random
from time import sleep, time
from color import Color
from threading import Thread

BAUD_RATE = 38400
NUM_PIXELS = 4
NUM_NODES = 101

PACKET_SINGLE_COLOR = 0
PACKET_COLOR_ARRAY  = 1
PACKET_PATTERN      = 2
PACKET_ENTROPY      = 3
PACKET_NEXT         = 4
BROADCAST = 0

def crc16_update(crc, a):
    crc ^= a
    for i in xrange(0, 8):
        if crc & 1:
            crc = (crc >> 1) ^ 0xA001
        else:
            crc = (crc >> 1)
    return crc

class Chandelier(object):

    def __init__(self):
        self.ser = None

    def open(self, device):

        try:
            print "Opening %s" % device
            self.ser = serial.Serial(device, 
                                     BAUD_RATE, 
                                     bytesize=serial.EIGHTBITS, 
                                     parity=serial.PARITY_NONE, 
                                     stopbits=serial.STOPBITS_ONE,
                                     timeout=.01)
        except serial.serialutil.SerialException, e:
            print "Cant open serial port: %s" % device
            sys.exit(-1)

        # Wait for things to settle, then pipe some characters through the line to get things going
        sleep(.250)
        self.ser.write(chr(0))
        self.ser.write(chr(0))
        self.ser.write(chr(0))

    def _send_packet(self, dest, type, data):
        if not isinstance(data, bytearray):
            print "data argument to send_packet must be bytearray"
            return

        packet = chr(dest) + chr(type) + data
        crc = 0
        for ch in packet:
            crc = crc16_update(crc, ch)
        packet = struct.pack("<BB", 255,  len(packet) + 2) + packet + struct.pack("<H", crc)
        self.ser.write(packet)

    def send_entropy(self):
        for dest in xrange(NUM_NODES):
            self._send_packet(dest, PACKET_ENTROPY, bytearray(os.urandom(1)))

    def set_color(self, dest, col):
        self._send_packet(dest, PACKET_SINGLE_COLOR, bytearray((col[0] + chr(col[1]) + chr(col[2]))))

    def set_color_array(self, dest, colors):
        packet = bytearray()
        for col in colors:
            packet += bytearray((col[0]) + chr(col[1]) + chr(col[2]))
        self._send_packet(dest, PACKET_COLOR_ARRAY, packet)

    def send_pattern(self, dest, pattern):
        self._send_packet(dest, PACKET_PATTERN, bytearray(pattern.describe())) 

    def next_pattern(self, dest):
        self._send_packet(dest, PACKET_NEXT, bytearray()) 

    def debug_serial(self, duration):
        finish = duration + time()
        while time() < finish:
            if self.ser.inWaiting() > 0:
                ch = self.ser.read(1)
                sys.stdout.write(ch);
                sys.stdout.flush()

    def run(self, function, delay, duration = 0.0):
        start_t = time()
        while True:
            t = time() - start_t
            col = function[t]
            array = []
            for i in xrange(NUM_PIXELS):
                array.append(col)

            ch.set_color_array(BROADCAST, array)
            sleep(delay)

            if duration > 0 and t > duration:
                break

DELAY = .02

device = "/dev/ttyAMA0"
if len(sys.argv) == 2:
    device = sys.argv[1]

ch = Chandelier()
ch.open(device)
ch.send_entropy()

random.seed()
period_s = 1

rainbow = function.Rainbow(generator.Sawtooth(.55))
rainbow.chain(filter.FadeIn(1))
rainbow.chain(filter.FadeOut(1.0, 5.0))

purple = function.ConstantColor(Color(128, 0, 128))
purple.chain(filter.FadeIn(1.0))
purple.chain(filter.FadeOut(1.0, 5.0))

wobble = function.RandomColorSequence(period_s, random.randint(0, 255))
g = generator.Sin((math.pi * 2) / period_s, -math.pi/2, .5, .5)
wobble.chain(filter.Brightness(g))

funcs = [rainbow, purple, wobble]
#while True:
#    wobble = function.RandomColorSequence(period_s, random.randint(0, 255))
#    g = generator.Sin((math.pi * 2) / period_s, -math.pi/2, .5, .5)
#    wobble.chain(filter.Brightness(g))
#    funcs = [wobble]
#    funcs = [purple]

loaded = False

while True:
    for f in funcs:
        if not loaded:
            ch.send_pattern(BROADCAST, f)
            ch.debug_serial(1)
            ch.next_pattern(BROADCAST)
            ch.debug_serial(1)
            loaded = True
            continue
            
        ch.send_pattern(BROADCAST, f)
        ch.debug_serial(1)
        ch.next_pattern(BROADCAST)
        ch.debug_serial(3)
