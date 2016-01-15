#!/usr/bin/env python

import sqlite3
import threading
import time
import urllib2
import sys
import serial
import requests

# Original script by: Fernando Lourenco
#	JimmyReb Modifications
#	v1.10 Tidy up
#	v1.11 Add script execution greeting and timestamps
#	v1.12 Add voltage to sensor database
#	v1.13 Change database name and location
#	v1.14 Fix time import
#	v1.15 Print sensor output


# global variables

#Sqlite Database where to store readings
dbname='/var/temperature/tempslog.db'
#logFile='/var/temperature/temps.log'

#Serial devices
DEVICE = '/dev/ttyAMA0'
BAUD = 9600
ser = serial.Serial(DEVICE, BAUD)

#Timeout (in s) for waiting to read a temperature from RF sensors
TIMEOUT = 30

# store the temperature in the database
def log_temperature(temp):

    try:
        conn=sqlite3.connect(dbname)
        curs=conn.cursor()

        curs.execute("INSERT INTO temps values(datetime('now','localtime'), '{0}', '{1}' )".format(temp['temperature'],temp['id']))
        # commit the changes
        conn.commit()
        conn.close()

    except Exception as e:
        text_file = open("debug.txt", "a+")
        text_file.write("{0} ERROR:\n{1}\n".format(time.strftime("%Y/%m/%d %H:%M:%S", time.gmtime()),str(e)))
        text_file.close()

def log_voltage(deviceid, volts):

    try:
        conn=sqlite3.connect(dbname)
        curs=conn.cursor()
        curs.execute("UPDATE sensors SET volts='{0}' where id='{1}'".format(volts, deviceid))
        conn.commit()
        conn.close()

    except Exception as e:
        text_file = open("debug.txt", "a+")
        text_file.write("{0} ERROR:\n{1}\n".format(time.strftime("%Y/%m/%d %H:%M:%S", time.gmtime()),str(e)))
        text_file.close()

# get temperature
# returns -100 on error, or the temperature as a float
def get_temp():
    global ser

    tempvalue = -100
    deviceid = '??'
    voltage = 0

    fim = time.time()+ TIMEOUT

    while (time.time()<fim) and (tempvalue == -100):
        n = ser.inWaiting() # n = length of string
        if n != 0:
            data = ser.read(n)
            nb_msg = len(data) / 12
            for i in range (0, nb_msg):
                msg = data[i*12:(i+1)*12]
                print time.strftime('\n%b %d, %Y %l:%M%p')
                deviceid = msg[1:3]
                if msg[3:7] == "TEMP":
                    tempvalue = msg[7:]
                    print("%s %s %s" % (msg[1:3], msg[3:7], tempvalue))
                else:
                    print(msg)
                if msg[3:7] == "BATT":
                    volts = msg[7:11]
                    if volts == "LOW":
                        volts = 0
                    log_voltage(deviceid, volts)
        else:
            time.sleep(5)

    return {'temperature':tempvalue, 'id':deviceid}


# main function
def main():
    print time.strftime('%b %d, %Y %l:%M%p')
    print("Monitoring serial port: " + DEVICE + " and entering data in: " + dbname)
    while True:
        temperature = get_temp()

        if temperature['temperature'] != -100:
            # Store the temperature in the database
            log_temperature(temperature)

if __name__=="__main__":
    main()
