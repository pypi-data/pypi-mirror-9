#!/usr/bin/env python
## Setup Section
from __future__ import print_function
import logging, time, sys
from psychopy import core, visual, event
from rusocsci import buttonbox

logging.getLogger().setLevel(logging.DEBUG)


led = [False]*8
win = visual.Window([400,300], monitor="testMonitor", color='white')
message = visual.TextStim(win, font="monospace", color='red', text='Press button on buttonbox or escape for exit.')
message.setAutoDraw(True)
win.flip()

## Experiment Section
bb = buttonbox.Buttonbox()
while not event.getKeys(['escape']):
	buttons = bb.getButtons()
	for b in buttons:
		print("button ({:3d}): #{}#{}".format(len(buttons), b, " "*50), end="\n")
		message.setText("button {:1s}, ascii: {:3d}".format(b,  ord(b)))
		win.flip()
		if ord(b) >= ord('a') and ord(b) < ord('a')+8:
			led[ord(b) - ord('a')] = False
		elif ord(b) >= ord('A') and ord(b) < ord('A')+8:
			led[ord(b) - ord('A')] = True
	bb.setLeds(led)
	sys.stdout.flush()
	time.sleep(.01)
	
bb.close()
win.close()
core.quit()
