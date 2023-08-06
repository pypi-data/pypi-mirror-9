# Copyright (C) 2014 Jonathan Peirce, Wilbert van Ham
# Distributed under the terms of the GNU General Public License (GPL).

from os import path
from psychopy.app.builder.experiment import CodeGenerationException, _valid_var_re
from psychopy.app.builder.components._base import BaseComponent
from psychopy.app.builder.experiment import Param

__author__ = 'Wilbert van Ham'

thisFolder = path.abspath(path.dirname(__file__))  # abs path of this file's folder
iconFile = path.join(thisFolder, 'rusocsciBox.png')
tooltip = 'Rusocsci Buttonbox:\nget button presses and releases,\nset LEDs and markers'

		
class RusocsciBoxComponent(BaseComponent):
	"""
	An event class for checking an Rusocsci bitsi mode buttonbox using rusocsci library
	"""
	categories = ['Responses', 'Stimuli']  # which section(s) in the components panel
	def __init__(self, exp, parentName, name='rusocscibox',
			allowedKeys="'A','B','C','D','E','F','G','H'",
			store='first key',
			deviceNumber="", port="", 
			marker=[0,0,0,0,0,0,0,0], markerValue="", resetMarker=True,
			forceEndRoutine=True, storeCorrect=False, correctAns="", discardPrev=True,
			startType='time (s)', startVal=0.0,
			stopType='duration (s)', stopVal='1.0',
			startEstim='', durationEstim=''):
		self.type = 'RusocsciButtonbox'
		self.url = "https://www.socsci.ru.nl/~wilberth/python/rusocsci.html"

		self.exp=exp#so we can access the experiment if necess
		self.exp.requirePsychopyLibs(['gui'])
		self.parentName=parentName
		
		#params
		self.params={}
		self.params['name'] = Param(name, valType='code', hint="A name for this Buttonbox object (e.g. bbox)", label="Name")

		self.order=['discard previous', 'forceEndRoutine','allowedKeys',#NB name and timing params always come 1st
			'store','storeCorrect','correctAns',
			]
		self.params['name']=Param(name,  valType='code', hint="A name for this keyboard object (e.g. response)",
			label="Name")
		self.params['allowedKeys']=Param(allowedKeys, valType='code', allowedTypes=[],
			updates='constant', allowedUpdates=['constant','set every repeat'],
			hint="A comma-separated list of keys (with quotes), upper case for button press, lower case for button release ",
			label="Allowed keys")
		self.params['startType']=Param(startType, valType='str',
			allowedVals=['time (s)', 'frame N', 'condition'],
			hint="How do you want to define your start point?",
			label="")
		self.params['stopType']=Param(stopType, valType='str',
			allowedVals=['duration (s)', 'duration (frames)', 'time (s)', 'frame N', 'condition'],
			hint="How do you want to define your end point?")
		self.params['startVal']=Param(startVal, valType='code', allowedTypes=[],
			hint="When does the keyboard checking start?")
		self.params['stopVal']=Param(stopVal, valType='code', allowedTypes=[],
			updates='constant', allowedUpdates=[],
			hint="When does the keyboard checking end?")
		self.params['startEstim']=Param(startEstim, valType='code', allowedTypes=[],
			hint="(Optional) expected start (s), purely for representing in the timeline")
		self.params['durationEstim']=Param(durationEstim, valType='code', allowedTypes=[],
			hint="(Optional) expected duration (s), purely for representing in the timeline")
		self.params['discard previous']=Param(discardPrev, valType='bool', allowedTypes=[],
			updates='constant', allowedUpdates=[],
			hint="Do you want to discard any keypresses occuring before the onset of this component?",
			label="Discard previous")
		self.params['store']=Param(store, valType='str', allowedTypes=[],allowedVals=['last key', 'first key', 'all keys', 'nothing'],
			updates='constant', allowedUpdates=[],
			hint="Choose which (if any) keys to store at end of trial",
			label="Store")
		self.params['forceEndRoutine']=Param(forceEndRoutine, valType='bool', allowedTypes=[],
			updates='constant', allowedUpdates=[],
			hint="Should the keypress force the end of the routine (e.g end the trial)?",
			label="Force end of Routine")
		self.params['storeCorrect']=Param(storeCorrect, valType='bool', allowedTypes=[],
			updates='constant', allowedUpdates=[],
			hint="Do you want to save the response as correct/incorrect?",
			label="Store correct")
		self.params['correctAns'] = Param(correctAns, valType='code', allowedTypes=[],
			updates='constant', allowedUpdates=[],
			hint="What is the 'correct' response? NB, won't work for multiple answers",
			label="Correct answer")
		self.params['markerValue'] = Param(markerValue, valType='code', 
			updates='constant', allowedUpdates=['constant','set every repeat', 'set very frame'],
			hint="Send 8 bit marker value (0-255), this will overide the 8 markers.",
			label="Marker value")
		self.params['m0'] = Param(marker[0], valType='bool', label="Marker 0 / A")
		self.params['m1'] = Param(marker[1], valType='bool', label="Marker 1 / B")
		self.params['m2'] = Param(marker[2], valType='bool', label="Marker 2 / C")
		self.params['m3'] = Param(marker[3], valType='bool', label="Marker 3 / D")
		self.params['m4'] = Param(marker[4], valType='bool', label="Marker 4 / E")
		self.params['m5'] = Param(marker[5], valType='bool', label="Marker 5 / F")
		self.params['m6'] = Param(marker[6], valType='bool', label="Marker 6 / G")
		self.params['m7'] = Param(marker[7], valType='bool', label="Marker 7 / H")
		self.params['resetMarker'] = Param(resetMarker, valType='bool', hint="Reset marker at end", label="Reset Marker")
		
		# advanced
		self.params['deviceNumber'] = Param(deviceNumber, valType='code', allowedTypes=[],
			updates='constant', allowedUpdates=[],
			hint="Device number, if you have multiple devices which one do you want (0, 1, 2...), 0 is last inserted",
			label="Device number", categ='Advanced')
		self.params['port'] = Param(port, valType='code', allowedTypes=[],
			updates='constant', allowedUpdates=[],
			hint="Port name, (COM1, /dev/ttyUSB0, ...) overrides device number",
			label="Port name", categ='Advanced')
		#del self.params['discard previous'] # not an option, always true

	def writeStartCode(self, buff):
		"""
		code for start of the script (import statements)
		This is executed before the window is created. Error dialogs must appear here.
		"""
		buff.writeIndented("#rusocsciBox writeStartCode\n")
		name = self.params['name'].val

		buff.writeIndented("import rusocsci.utils, rusocsci.buttonbox\n")
		buff.writeIndented("try:\n") 
		buff.writeIndented("    rusocsciBoxList\n") 
		buff.writeIndented("except NameError:\n") 
		buff.writeIndented("    rusocsciBoxList = [] # one list of all connected rusocsciBox devices\n") 
		
		# find rusocsciBox port
		if self.params['port'].val:
			buff.writeIndented("rusocsciPort = rusocsci.utils.getPort(port='{}')\n".
				format(self.params['port']))
		elif self.params['deviceNumber']:
			buff.writeIndented("rusocsciPort = rusocsci.utils.getPort({})\n".
				format(self.params['deviceNumber']))
		else:
			buff.writeIndented("rusocsciPort = rusocsci.utils.getPort()\n")
		buff.writeIndented("print('requested deviceNumber: {}, #{}#, port: #{}#')\n".
			format(name, self.params['deviceNumber'], self.params['port']))
		buff.writeIndented("print('found port: #{}#'.format(rusocsciPort))\n")
		
		# connect to rusocsciBox port
		buff.writeIndented("rusocsciPortList = [x._port for x in rusocsciBoxList]\n") # list of existing ports
		buff.writeIndented("if rusocsciPort in rusocsciPortList:\n") # device already open
		buff.writeIndented("    {} = rusocsciBoxList[rusocsciPortList.index(rusocsciPort)]\n".format(name))
		buff.writeIndented("else:\n") # open new buttonbox
		buff.writeIndented("    {} = rusocsci.buttonbox.Buttonbox(port=rusocsciPort)\n".format(name))
		
		#test successful connection
		buff.writeIndented("    if not {}._device:\n".format(name))
		buff.writeIndented("        myDlg = gui.Dlg(title='ERROR')\n")
		buff.writeIndented("        myDlg.addText('Could not open device {}')\n".format(name))
		buff.writeIndented("        myDlg.show()\n")
		buff.writeIndented("        raise Exception('ERROR connecting to rusocsciBox device: {}')\n".format(name))
		buff.writeIndented("    else:\n")
		buff.writeIndented("        rusocsciBoxList.append({})\n".format(name))


	def writeInitCode(self, buff):
		"""
		code for start of the experiment, after creation of window
		"""
		buff.writeIndented("#rusocsciBox writeInitCode\n")
		
		# for debugging during Component development:
		#buff.writeIndented("# self.params for Rusocsci Buttonbox:\n")
		#for p in self.params.keys():
			#buff.writeIndented("#{}: {} <type {}>\n".format(p, self.params[p].val, self.params[p].valType))
			
	
	def writeRoutineStartCode(self, buff):
		"""
		Write the code that will be called at routine (a builder tab) start
		"""
		buff.writeIndented("#rusocsciBox writeRoutineStartCode\n")
		name = self.params['name']
		buff.writeIndented("{}.status = NOT_STARTED\n".format(name))
		buff.writeIndented("{}.keys = []\n".format(name))
		buff.writeIndented("{}.rt = []\n".format(name))
		buff.writeIndented("{}.clock = core.Clock()\n".format(name))
		if self.params['store'].val=='nothing' and self.params['storeCorrect'].val==False:
			#the user doesn't want to store anything so don't bother
			return
		
	def writeFrameCode(self,buff):
		"""
		Write the code that will be called every frame
		"""
		buff.writeIndented("#rusocsciBox writeFrameCode\n")

		#some shortcuts
		store=self.params['store'].val
		storeCorr=self.params['storeCorrect'].val
		forceEnd=self.params['forceEndRoutine'].val
		allowedKeys = self.params['allowedKeys'].val.strip()
		name = self.params['name']

		buff.writeIndented("\n")
		buff.writeIndented("# *{}* updates\n".format(name))
		self.writeStartTestCode(buff)#writes an if statement to determine whether to draw etc
		buff.writeIndented("%(name)s.status = STARTED\n" %(self.params))
		allowedKeysIsVar = _valid_var_re.match(str(allowedKeys)) and not allowedKeys == 'None'
		if allowedKeysIsVar:
			# if it looks like a variable, check that the variable is suitable to eval at run-time
			buff.writeIndented("# AllowedKeys looks like a variable named `%s`\n" % allowedKeys)
			buff.writeIndented("if not '%s' in locals():\n" % allowedKeys)
			buff.writeIndented("	logging.error('AllowedKeys variable `%s` is not defined.')\n" % allowedKeys)
			buff.writeIndented("	core.quit()\n")
			buff.writeIndented("if not type(%s) in [list, tuple, np.ndarray]:\n" % allowedKeys)
			buff.writeIndented("	if not isinstance(%s, basestring):\n" % allowedKeys)
			buff.writeIndented("		logging.error('AllowedKeys variable `%s` is not string- or list-like.')\n" % allowedKeys)
			buff.writeIndented("		core.quit()\n")
			buff.writeIndented("	elif not ',' in %s: %s = (%s,)\n" % (allowedKeys, allowedKeys, allowedKeys))
			buff.writeIndented("	else:  %s = eval(%s)\n" % (allowedKeys, allowedKeys))
			keyListStr = "keyList=list(%s)" % allowedKeys  # eval() at run time
			
		
		buff.writeIndented("# keyboard checking is just starting\n")
		if self.params['markerValue'].val != "":
			markerValue = self.params['markerValue'].val
			buff.writeIndented("{}.setLeds(val=eval({}))\n".format(name, markerValue))
		else:
			markerList = [self.params['m0'].val, self.params['m1'].val, self.params['m2'].val,
				 self.params['m3'].val, self.params['m4'].val, self.params['m5'].val,
				 self.params['m6'].val, self.params['m7'].val]
			buff.writeIndented("{}.setLeds({})\n".format(name, markerList))
		#if store != 'nothing':
			#buff.writeIndented("%(name)s.clock.reset()  # now t=0\n" % self.params)
		if self.params['discard previous'].val:
			buff.writeIndented("{}.clearEvents()\n".format(name))
			
		buff.setIndentLevel(-1, relative=True)#to get out of the if statement
		#test for stop (only if there was some setting for duration or stop)
		if self.params['stopVal'].val not in ['', None, -1, 'None']:
			self.writeStopTestCode(buff)#writes an if statement to determine whether to draw etc
			buff.writeIndented("{}.status = STOPPED\n".format(name))
			buff.setIndentLevel(-1, relative=True) # end writeStopTestCode

		buff.writeIndented("if {}.status == STARTED:\n".format(name))
		buff.setIndentLevel(1, relative=True)
		dedentAtEnd = 1 #keep track of how far to dedent later
		#do we need a list of keys? (variable case is already handled)
		if allowedKeys in [None, "none", "None", "", "[]", "()"]:
			keyListStr=""
		elif not allowedKeysIsVar:
			try:
				keyList = eval(allowedKeys)
			except:
				raise CodeGenerationException(self.params["name"], "Allowed keys list is invalid.")
			if type(keyList)==tuple: #this means the user typed "left","right" not ["left","right"]
				keyList=list(keyList)
			elif isinstance(keyList, basestring): #a single string/key
				keyList=[keyList]
			keyListStr= "keyList=%s" %(repr(keyList))
		#check for keypresses
		buff.writeIndented("theseKeys = {}.getKeys({})\n".format(name, keyListStr))

		#how do we store it?
		if store!='nothing' or forceEnd:
			#we are going to store something
			buff.writeIndented("if len(theseKeys) > 0:  # at least one key was pressed\n")
			buff.setIndentLevel(1,True); dedentAtEnd+=1 #indent by 1

		if store=='first key':#then see if a key has already been pressed
			buff.writeIndented("if %(name)s.keys == []:  # then this was the first keypress\n" %(self.params))
			buff.setIndentLevel(1,True); dedentAtEnd+=1 #indent by 1
			buff.writeIndented("%(name)s.keys = theseKeys[0]  # just the first key pressed\n" %(self.params))
			buff.writeIndented("%(name)s.rt = t-%(name)s.tStart\n" %(self.params))
		elif store=='last key':
			buff.writeIndented("%(name)s.keys = theseKeys[-1]  # just the last key pressed\n" %(self.params))
			buff.writeIndented("%(name)s.rt = t-%(name)s.tStart\n" %(self.params))
		elif store=='all keys':
			buff.writeIndented("%(name)s.keys.extend(theseKeys)  # storing all keys\n" %(self.params))
			buff.writeIndented("%(name)s.rt.append(t-%(name)s.tStart)\n" %(self.params))

		if storeCorr:
			buff.writeIndented("# was this 'correct'?\n" %self.params)
			buff.writeIndented("if (%(name)s.keys == str(%(correctAns)s)) or (%(name)s.keys == %(correctAns)s):\n" %(self.params))
			# todo: both %(name)s.keys and %(correctAns)s may be lists
			buff.writeIndented("	%(name)s.corr = 1\n" %(self.params))
			buff.writeIndented("else:\n")
			buff.writeIndented("	%(name)s.corr = 0\n" %(self.params))

		if forceEnd==True:
			buff.writeIndented("# a response ends the routine\n" %self.params)
			buff.writeIndented("continueRoutine = False\n")

		buff.setIndentLevel(-(dedentAtEnd), relative=True)
	def writeRoutineEndCode(self, buff):
		#some shortcuts
		buff.writeIndented("#rusocsciBox writeRoutineEndCode\n")

		name = self.params['name']
		store=self.params['store'].val
		if self.params['resetMarker'].val:
			buff.writeIndented("{}.setLeds()\n".format(name))
		if store == 'nothing':
			return
		if len(self.exp.flow._loopList):
			currLoop=self.exp.flow._loopList[-1]  # last (outer-most) loop
		else:
			currLoop = self.exp._expHandler

		#write the actual code
		buff.writeIndented("# check responses\n" %self.params)
		buff.writeIndented("if %(name)s.keys in ['', [], None]:  # No response was made\n"%self.params)
		buff.writeIndented("   %(name)s.keys=None\n" %(self.params))
		if self.params['storeCorrect'].val:#check for correct NON-repsonse
			buff.writeIndented("   # was no response the correct answer?!\n" %(self.params))
			buff.writeIndented("   if str(%(correctAns)s).lower() == 'none': %(name)s.corr = 1  # correct non-response\n" %(self.params))
			buff.writeIndented("   else: %(name)s.corr = 0  # failed to respond (incorrectly)\n" %(self.params))
		buff.writeIndented("# store data for %s (%s)\n" %(currLoop.params['name'], currLoop.type))
		if currLoop.type in ['StairHandler', 'MultiStairHandler']:
			#data belongs to a Staircase-type of object
			if self.params['storeCorrect'].val==True:
				buff.writeIndented("%s.addResponse(%s.corr)\n" %(currLoop.params['name'], name))
				buff.writeIndented("%s.addOtherData('%s.rt', %s.rt)\n" %(currLoop.params['name'], rusocsciBox.psyexpname, name))
		else:
			#always add keys
			buff.writeIndented("%s.addData('%s.keys',%s.keys)\n" \
			   %(currLoop.params['name'],name,name))
			if self.params['storeCorrect'].val==True:
				buff.writeIndented("%s.addData('%s.corr', %s.corr)\n" \
								   %(currLoop.params['name'], name, name))
			#only add an RT if we had a response
			buff.writeIndented("if %(name)s.keys != None:  # we had a response\n" %(self.params))
			buff.writeIndented("    %s.addData('%s.rt', %s.rt)\n" \
							   %(currLoop.params['name'], name, name))
		if currLoop.params['name'].val == self.exp._expHandler.name:
			buff.writeIndented("%s.nextEntry()\n" % self.exp._expHandler.name)
			
		
	def writeExperimentEndCode(self, buff):
		buff.writeIndented("#rusocsciBox writeExperimentEndCode\n")
		
		name = self.params['name']
		buff.writeIndented("{}.close()\n".format(name))
		

