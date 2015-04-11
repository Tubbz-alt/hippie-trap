#!/usr/bin/python

import serial
import struct
from time import sleep

BAUD_RATE = 38400

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

    def set_color(self, red, green, blue):
        packet = chr(red) + chr(green) + chr(blue);
        crc = 0
        for ch in packet:
            crc = crc16_update(crc, ord(ch))
        packet = struct.pack("<BB", 255,  len(packet) + 2) + packet + struct.pack("<H", crc)
        self.ser.write(packet)

ch = Chandelier()
ch.open("/dev/ttyAMA0")

while True:
    ch.set_color(255, 0, 0)
    sleep(1)
    ch.set_color(0, 0, 255)
    sleep(1)