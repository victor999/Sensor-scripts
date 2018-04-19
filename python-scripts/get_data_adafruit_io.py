#!/usr/bin/env python
# script for scanning BT sensors, get data and write it to io.adafruit log
# create a file /home/pi/ada.fr wit the following content
#
# mac_address
# aio_key
from __future__ import print_function
import argparse
import binascii
import os
import sys
from bluepy import btle

from Adafruit_IO import *

F = open("/home/pi/ada.fr", "r")
mac_address = F.readline().replace('\n', '')
mac_address = mac_address.replace('\r', '')
aio_key = F.readline().replace('\n', '')
aio_key = aio_key.replace('\r', '')
F.close()

print(mac_address)
print(aio_key)

aio = Client(aio_key)

if os.getenv('C', '1') == '0':
    ANSI_RED = ''
    ANSI_GREEN = ''
    ANSI_YELLOW = ''
    ANSI_CYAN = ''
    ANSI_WHITE = ''
    ANSI_OFF = ''
else:
    ANSI_CSI = "\033["
    ANSI_RED = ANSI_CSI + '31m'
    ANSI_GREEN = ANSI_CSI + '32m'
    ANSI_YELLOW = ANSI_CSI + '33m'
    ANSI_CYAN = ANSI_CSI + '36m'
    ANSI_WHITE = ANSI_CSI + '37m'
    ANSI_OFF = ANSI_CSI + '0m'


def dump_services(dev):
    services = sorted(dev.services, key=lambda s: s.hndStart)
    for s in services:
        print ("\t%04x: %s" % (s.hndStart, s))
        if s.hndStart == s.hndEnd:
            continue
        chars = s.getCharacteristics()
        for i, c in enumerate(chars):
            props = c.propertiesToString()
            h = c.getHandle()
            if 'READ' in props:
                val = c.read()
                if c.uuid == btle.AssignedNumbers.device_name:
                    string = ANSI_CYAN + '\'' + \
                        val.decode('utf-8') + '\'' + ANSI_OFF
                elif c.uuid == btle.AssignedNumbers.device_information:
                    string = repr(val)
                else:
                    string = '<s' + binascii.b2a_hex(val).decode('utf-8') + '>'
            else:
                string = ''
            print ("\t%04x:    %-59s %-12s %s" % (h, c, props, string))

            while True:
                h += 1
                if h > s.hndEnd or (i < len(chars) - 1 and h >= chars[i + 1].getHandle() - 1):
                    break
                try:
                    val = dev.readCharacteristic(h)
                    print ("\t%04x:     <%s>" %
                           (h, binascii.b2a_hex(val).decode('utf-8')))
                except btle.BTLEException:
                    break


class ScanHandler(btle.DefaultDelegate):

    def __init__(self, opts):
        btle.DefaultDelegate.__init__(self)
        self.opts = opts

    def handleDiscovery(self, dev, isNewDev, isNewData):
        
        if dev.rssi < self.opts.sensitivity:
            return

        print(dev.addr)

        if(dev.addr == mac_address):
            print('found')
            print(dev.addr)

            print(hex(ord(dev.rawData[11])))
            print(hex(ord(dev.rawData[12])))

            tempValStr = str(format(ord(dev.rawData[12]), 'x')) + str('{:02x}'.format(ord(dev.rawData[11]), 'x'))
            print("tempValStr")
            print(tempValStr);
            
            tempVal2 = int(tempValStr, 16)

            print("tempVal2")
            print(tempVal2);
            
            if tempVal2 > 0x7FFF:
                tempVal2 -= 0x10000
            print("Temperature")
            print(str(tempVal2))

            g_temperature = float(tempVal2) / 100
            print(g_temperature)

            print("Battery")
            batValData = int(hex(ord(dev.rawData[17])), 16)
            print(hex(ord(dev.rawData[17])))
            print(str(batValData))
            g_batVal = batValData / 10.0           
            print(str(g_batVal))

            if(isNewDev):
                aio.send('Temperature', g_temperature)
                aio.send('Battery', g_batVal)

                        
            

def main():

    chData = []

    parser = argparse.ArgumentParser()

    parser.add_argument('-i', '--hci', action='store', type=int, default=0,
                        help='Interface number for scan')
    parser.add_argument('-t', '--timeout', action='store', type=int, default=4,
                        help='Scan delay, 0 for continuous')
    parser.add_argument('-s', '--sensitivity', action='store', type=int, default=-128,
                        help='dBm value for filtering far devices')
    parser.add_argument('-d', '--discover', action='store_true',
                        help='Connect and discover service to scanned devices')
    parser.add_argument('-a', '--all', action='store_true',
                        help='Display duplicate adv responses, by default show new + updated')
    parser.add_argument('-n', '--new', action='store_true',
                        help='Display only new adv responses, by default show new + updated')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='Increase output verbosity')


    arg = parser.parse_args(sys.argv[1:])

    scanner = btle.Scanner(arg.hci).withDelegate(ScanHandler(arg))

    print (ANSI_RED + "Scanning for devices..." + ANSI_OFF)
    devices = scanner.scan(30)


if __name__ == "__main__":
    main()
