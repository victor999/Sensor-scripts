#!/usr/bin/env python
# script for scanning BT sensors, get data and upload to weather underground
# create a file /home/pi/weather.u with the following content
# mac_address
# station_id
# station_password

from __future__ import print_function
import argparse
import binascii
import os
import sys
from bluepy import btle
import requests

F = open("/home/pi/weather.u", "r")
mac_address = F.readline().replace('\n', '')
mac_address = mac_address.replace('\r', '')
WU_station_id = F.readline().replace('\n', '')
WU_station_id = WU_station_id.replace('\r', '')
WU_station_pwd = F.readline().replace('\n', '')
WU_station_pwd = WU_station_pwd.replace('\r', '')
F.close()

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
                temperatureF = 32 + 1.8 * g_temperature
                # create a string to hold the first part of the URL
                WUurl = "https://weatherstation.wunderground.com/weatherstation/updateweatherstation.php?"
                WUcreds = "ID=" + WU_station_id + "&PASSWORD="+ WU_station_pwd
                date_str = "&dateutc=now"
                action_str = "&action=updateraw"

                temperature_str = "{0:.2f}".format(temperatureF)
                #humidity_str = "{0:.2f}".format(humidity)

                r= requests.get(
                    WUurl +
                    WUcreds +
                    date_str +
#                   "&humidity=" + humidity_str +
                    "&tempf=" + temperature_str +
                    action_str)

                print("Received " + str(r.status_code) + " " + str(r.text))


                        
            

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

