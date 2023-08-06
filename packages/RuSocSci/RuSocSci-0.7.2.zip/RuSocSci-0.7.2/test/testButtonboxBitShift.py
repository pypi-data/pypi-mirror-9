#!/usr/bin/env python
from rusocsci import buttonbox

bb = buttonbox.Buttonbox()
val = 0

while True:
	try:
		d = ord(bb.getButtons()[0]) # A-H for turning on, a-h for turning off
		val |= 1 << d - ord('A') & 255 # turn on these bits
		val ^= 1 << d - ord('a') # turn off these bits, except on capitals
	except:
		pass
	bb.setLeds(val = val)
