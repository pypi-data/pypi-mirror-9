#!/usr/bin/python

import serial, logging, os, time
# /dev/serial/by-id/*FTDI* for FTDI (0403:6001) in Arduino 2009
# /dev/ttyACM? for Arduino Uno R3 (2341:0043) and Arduino Leonardo (2341:8036)

try:
	port = os.popen('ls -t /dev/serial/by-id/*FTDI*').read().split()[0]
except:
	port="com4"

print("port: {}".format(port))
device = serial.Serial(port, baudrate=115200, parity='N', timeout = 0.0)

device.flushInput()
# The following three lines cause a reset of the Arduino. 
# See "Automatic (Software) Reset" in the documentation.
# Make sure not to send data for the first second after reset.
device.setDTR(False) 
time.sleep(.1)
device.setDTR(True)

#idString = "joystick streaming angle, Ready!" + "0d0a".decode("hex")
# collect byes up to "!\x0d\x0a" that identify the type of device
beginTime = time.time()
bytesRead = ""
while len(bytesRead) < 3 or bytesRead[-3:] != "!\x0d\x0a":
	if time.time() > beginTime + 3:
		logging.error("USB serial timeout: '{}'".format(bytesRead))
		exit()
	bytes = device.read()
	bytesRead += bytes
	
print(device, bytesRead[:-2])

