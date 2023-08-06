#!/usr/bin/env python
## Setup Section
from __future__ import print_function
import logging, time, sys, serial
logging.getLogger().setLevel(logging.DEBUG)
from rusocsci import buttonbox

## Experiment Section
bb = buttonbox.Buttonbox()
#bb = serial.Serial('COM21', baudrate=115200)

# secret undocumented initialization protocol
#time.sleep(.5)
#bb.sendMarker(val=255)
#bb.write(chr(255))
#bb.write(chr(56))
#time.sleep(3)

#bb.sendMarker(val=56) # turn on central reference

for j in range(1):
	for i in range(10, 56):
		#bb.write(chr(i))
		#bb.flush
		bb.sendMarker(val=i)
		time.sleep(.1)
bb.sendMarker(val=255)
bb.close()