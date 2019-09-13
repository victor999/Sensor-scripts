#!/usr/bin/env python
# script for scanning BT sensors, get data and write it to thingspeak.com log
# create a file /home/pi/thing.sp wit the following content
#
# mac_address
# channel_id
# write_api_key
from __future__ import print_function
import argparse
import binascii
import os
import sys
from time import gmtime, strftime
from bluepy import btle
import sys

import thingspeak

if len(sys.argv) == 2:
        filename = str(sys.argv[1])       
else:
        filename = '/home/pi/thing-env.sp'

print(filename)

F = open(filename, "r")
mac_address = F.readline().replace('\n', '')
mac_address = mac_address.replace('\r', '')
channel_id = F.readline().replace('\n', '')
channel_id = channel_id.replace('\r', '')
write_api = F.readline().replace('\n', '')
write_api = write_api.replace('\r', '')
F.close()

print(channel_id)
print(write_api)


channel = thingspeak.Channel(id=channel_id, write_key=write_api)

print(channel)

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

        #if dev.rssi < self.opts.sensitivity:
        #    return

        if(dev.addr == mac_address):
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

            print("Pressure")
            pressValStr = str(format(ord(dev.rawData[20]), 'x')) + str(format(ord(dev.rawData[19]), 'x')) + str(format(ord(dev.rawData[18]), 'x')) + str('{:02x}'.format(ord(dev.rawData[17]), 'x'))
            print(pressValStr)
            pressureData = int(pressValStr, 16)
            print(str(pressureData))
            g_pressure = pressureData / 1000.0
            print(str(g_pressure))

            print("Humidity")
            humValStr = str(format(ord(dev.rawData[26]), 'x')) + str('{:02x}'.format(ord(dev.rawData[25]), 'x'))
            print(humValStr);
            humidityData = int(humValStr, 16)
            print(str(humidityData))
            g_humidity = humidityData / 100
            print(str(g_humidity))

            if(isNewDev):
                channel.update({1:g_temperature, 2:g_humidity, 3:g_pressure})
		f=open("th_sp.log", "a+")
		f.write(strftime("%Y-%m-%d %H:%M:%S", gmtime()))
		f.write("\n")
		f.write(pressValStr)
		f.write("\n")
		f.write(str(pressureData))
		f.write("\n")
		f.write(str(g_pressure))
		f.write("\n")
		f.write(humValStr)
		f.write("\n")
		f.write(str(humidityData))
		f.write("\n")
		f.write(str(g_humidity))
		f.write("\n")
		f.close()


def main():

    scanner = btle.Scanner(0).withDelegate(ScanHandler(btle.DefaultDelegate))

    print (ANSI_RED + "Scanning for devices..." + ANSI_OFF)
    devices = scanner.scan(30)


if __name__ == "__main__":
    main()
