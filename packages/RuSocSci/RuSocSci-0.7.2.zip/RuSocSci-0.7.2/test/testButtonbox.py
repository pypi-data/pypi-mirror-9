#!/usr/bin/env python
## Setup Section
from __future__ import print_function
import logging, time, sys
logging.getLogger().setLevel(logging.DEBUG)
from rusocsci import buttonbox

led = [False]*8

## Experiment Section
bb = buttonbox.Buttonbox()
while True:
	buttons = bb.getButtons()
	for b in buttons:
		print("button ({:3d}): #{}#{}".format(len(buttons), b, " "*50), end="\n")
		if ord(b) >= ord('a') and ord(b) < ord('a')+8:
			led[ord(b) - ord('a')] = False
		elif ord(b) >= ord('A') and ord(b) < ord('A')+8:
			led[ord(b) - ord('A')] = True
	bb.setLeds(led)
	sys.stdout.flush()
	time.sleep(.1)
