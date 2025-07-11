
# load pygaze libraries and custom pygaze libraries
import pygaze
from pygaze import libscreen, libinput, eyetracker, libtime
from pygaze.plugins import aoi
from stimPresPyGaze import *

# import constants for pygaze
import constants
import tobii_research as tr

# load psychopy and custom psychopy libraries
from baseDefsPsychoPy import *
from stimPresPsychoPy import *
from psychopy.hardware import keyboard
from psychopy import logging

logging.console.setLevel(logging.CRITICAL)

# load other utility functions
import csv
import os
import random

class Exp:
	def __init__(self):
		self.expName = "BounCES"
		self.path = os.getcwd()
		self.subjInfo = {
			'1': {'name': 'subjCode',
				  'prompt': 'EXP_XXX',
				  'options': 'any',
				  'default': self.expName + '_001'},
			'2': {'name': 'sex',
				  'prompt': 'Subject sex m/f: ',
				  'options': ("m","f"),
				  'default': '',
				  'type' : str},
			'3' : {	'name' : 'age',
					   'prompt' : 'Subject Age: ',
					   'options' : 'any',
					   'default':'',
					   'type' : str},
			'4': {'name': 'order',
                   'prompt': '(test / 1 / 2 / 3 / 4)',
                   'options': ("test", "1", "2", "3", "4"),
                   'default': "test",
                   'type': str},
			'5' : {'name' : 'expInitials',
				   'prompt' : 'Experimenter Initials: ',
				   'options' : 'any',
				   'default' : '',
				   'type' : str},
			'6': {	'name' : 'mainMonitor',
					  'prompt' : 'Screen Index (0,1,2,3): ',
					  'options' : (0,1,2,3),
					  'default': 2,
					  'type' : int},
			'7': {	'name' : 'sideMonitor',
					  'prompt' : 'Screen Index (0,1,2,3): ',
					  'options' : (0,1,2,3),
					  'default': 1,
					  'type' : int},
			'8': {'name': 'eyetracker',
                   'prompt': '(yes / no)',
                   'options': ("yes", "no"),
                   'default': "yes",
                   'type': str},
			'9': {'name': 'activeMode',
				  'prompt': 'input / gaze',
				  'options': ("input", "gaze"),
				  'default': "input",
				  'type': str},
			'10': {'name': 'responseDevice',
				  'prompt': 'keyboard / mouse',
				  'options': ("keyboard", "mouse"),
				  'default': 'keyboard'}
		}

		optionsReceived = False
		fileOpened = False

		# open data files to save while checking to make sure that no data is overwritten
		while not fileOpened:
			[optionsReceived, self.subjVariables] = enterSubjInfo(self.expName, self.subjInfo)
			print(self.subjVariables)

			from pygaze import settings
			print(constants.LOGFILE)
			settings.LOGFILE = constants.LOGFILEPATH + self.subjVariables['subjCode']
			print("settings logfile: " + settings.LOGFILE)

			print("Tracker type: " + constants.TRACKERTYPE)
			if not optionsReceived:
				popupError(self.subjVariables)

			elif not os.path.isfile('data/training/' + 'tracking_data_' + self.subjVariables['subjCode'] + '.txt'):

				# if using an eyetracker
				if self.subjVariables['eyetracker'] == "yes":
					# import eyetracking package from pygaze
					from pygaze import eyetracker

					if not os.path.isfile(settings.LOGFILE + '_TOBII_output.tsv'):
						fileOpened = True
						self.activeTrainingOutputFile = open(
							'data/activeTraining/' + 'tracking_data_' + self.subjVariables['subjCode'] + '.txt', 'w')

						self.trainingOutputFile = open('data/training/' + 'tracking_data_' + self.subjVariables['subjCode'] + '.txt',
												   'w')
						self. activeOutputFile = open(
							'data/' + 'activeTest/tracking_data_' + self.subjVariables['subjCode'] + '.txt',
							'w')

					else:
						fileOpened = False
						popupError(
							'That subject code for the eyetracking data already exists! The prompt will now close!')
						core.quit()
				else:
					#if eyetracker is no, only track the training output
					fileOpened = True
					self.trainingOutputFile = open(
						'data/training/' + 'tracking_data_' + self.subjVariables['subjCode'] + '.txt', 'w')

			else:
				fileOpened = False
				popupError('That subject code already exists!')

		self.disp = libscreen.Display(disptype='psychopy', fgc="black", bgc="black", screennr=self.subjVariables['mainMonitor'])
		self.blackScreen = libscreen.Screen(fgc="black", bgc="black")
		self.win = pygaze.expdisplay
		# Stim Paths
		self.imagePath = self.path + '/stimuli/images/'
		self.soundPath = self.path + '/stimuli/sounds/'

		self.activeSoundPath = self.path + '/stimuli/sounds/'
		self.moviePath = self.path + '/stimuli/movies/'
		self.AGPath = self.path + '/stimuli/movies/AGStims/'
		self.imageExt = ['jpg', 'png', 'gif', 'jpeg']

		# Inputs

		if self.subjVariables['eyetracker'] == 'yes':

			attempts = 0
			self.eyetrackers = tr.find_all_eyetrackers()

			while len(self.eyetrackers) == 0 and attempts < 50:
				print("trying to find eyetracker...")
				attempts += 1
				self.eyetrackers = tr.find_all_eyetrackers()

			self.tracker = pygaze.eyetracker.EyeTracker(self.disp)
			print("Eyetracker connected? " + str(self.tracker.connected()))

		# We will always use the keyboard to start the experiment, but it won't always be the main input
		if self.subjVariables['responseDevice'] == 'keyboard':
			print("Using keyboard...")
			self.inputDevice = "keyboard"
			self.validResponses = {'1': 'space', '2': 'left', '3': 'right', '4': 'z', '5': 'enter'}
		# create keyboard object
			self.input = keyboard.Keyboard()

		else:
			self.inputDevice = "mouse"
			print("using mouse...")
			#self.input = libinput.Mouse(mousebuttonlist = [1], timeout = None)


class ExpPresentation(Exp):
	def __init__(self, experiment):
		self.experiment = experiment

	def initializeExperiment(self):
		
		# Loading Files Screen
		loadScreen = libscreen.Screen()
		loadScreen.draw_text(text = "Loading Files...", color = "white", fontsize = 48)
		self.experiment.disp.fill(loadScreen)
		self.experiment.disp.show()

		# Load Trials
		familiarizationTrialPath = 'orders/familiarizationTrialOrders/BounCES_Order' + self.experiment.subjVariables['order'] +".csv"
		activeTrainingTrialPath = 'orders/activeTrainingOrders/BounCES_ActiveTrainingOrder' + self.experiment.subjVariables['order'] +".csv"
		activeTestTrialPath = 'orders/activeOrders/BounCES_ActiveOrder' + self.experiment.subjVariables['order'] +".csv"
		lwlTrialPath = 'orders/lwlOrders/BounCES_LWLOrder' + self.experiment.subjVariables['order'] +".csv"

		(self.familTrialListMatrix, self.trialFieldNames) = importTrials(familiarizationTrialPath, method="sequential")
		(self.activeTrainingTrialsMatrix, self.activeTrainingTrialFieldNames) = importTrials(activeTrainingTrialPath, method="sequential")
		(self.activeTestTrialsMatrix, self.activeTrialFieldNames) = importTrials(activeTestTrialPath, method="sequential")
		(self.lwlTestTrialsMatrix, self.lwlTrialFieldNames) = importTrials(lwlTrialPath, method="sequential")

		self.movieMatrix = loadFilesMovie(self.experiment.moviePath, ['mp4', 'mov'], 'movie', self.experiment.win)
		self.AGmovieMatrix = loadFilesMovie(self.experiment.AGPath, ['mp4'], 'movie', self.experiment.win)
		self.soundMatrix = loadFiles(self.experiment.soundPath, ['.mp3', '.wav'], 'sound')
		self.AGsoundMatrix = loadFiles(self.experiment.AGPath, ['.mp3', '.wav'], 'sound')
		self.imageMatrix = loadFiles(self.experiment.imagePath, ['.png', ".jpg", ".jpeg"], 'image', win = self.experiment.win)
		self.stars = loadFiles(self.experiment.AGPath, ['.jpg'], 'image', self.experiment.win)

		self.locations = ['left', 'right']
		self.trigger = 0 # start trigger for eyetracker (0) vs keyboard (1)

		# dimensions MATH ugh

		self.x_length = constants.DISPSIZE[0]
		self.y_length = constants.DISPSIZE[1]
		print(self.x_length, self.y_length)

		self.pos = {'bottomLeft': (-self.x_length/4, -self.y_length/4), 
			  'bottomRight': (self.x_length/4, -self.y_length/4),
					'centerLeft': (-480, 0), 'centerRight': (480, 0),
					'topLeft': (-self.x_length/4, self.y_length/4),
					'topRight': (self.x_length/4, self.y_length/4),
					'center': (0, 0),
					'sampleStimLeft': (-600, -150),
					'sampleStimRight': (600, -150),
					'stimleft': (-self.x_length/4, -350),
					'stimright': (self.x_length/4, -350)
					}

		# Contingent Timing Settings
		self.firstTriggerThreshold = 150  # (ms) time to accumulate looks before triggering image
		self.awayThreshold = 250  # (ms) time of NA/away looks for contingent ends - should account for blinks. Lower is more sensitive, higher is more forgiving.
		self.noneThreshold = 1  # (ms) time of look to on-screen but non-trigger AOI before contingent ends - should account for shifts

		self.timeoutTime = 10000  # (ms) 30s, length of trial
		self.rect_size = (800, 700)
		self.fam_rect_size = (600, 500)
		self.fam_stim_size = (400, 400)
		self.stim_size = (500,500)
		self.aoiLeft = aoi.AOI('rectangle', pos = (0, 190), size = self.rect_size)
		self.aoiRight = aoi.AOI('rectangle', pos= (1120, 190), size=self.rect_size)
		self.ISI = 500
		self.startSilence = 0
		self.endSilence = 1000

		# sampling threshold - when the gaze will trigger (20 samples = 333.333 ms)
		self.lookAwayPos = (-1,-1)
		self.maxLabelTime = 10000 # (ms) Maximum length of time each image can be sampled before the screen resets.

        # Animation settings for looming
		self.loomDuration = 1  # seconds for full loom cycle
		self.jiggleAmplitude = 5  # degrees
		self.jiggleFrequency = 1  # Hz
		self.wiggleDuration = 2.0 #s
		self.targetSizeFactor = 1.25  # Grow to 150% of original size

		# Build Screens for Image Based Displays (Initial Screen and Active Stuff)

		# INITIAL SCREEN #
		self.initialScreen = libscreen.Screen()
		self.initialImageName = self.experiment.imagePath + "bunnies.gif"
		initialImage = visual.ImageStim(self.experiment.win, self.initialImageName, mask=None, interpolate=True)
		initialImage.setPos(self.pos['center'])
		buildScreenPsychoPy(self.initialScreen, [initialImage])


		print("Files Loaded!")

	# Active Sampling Test Screen #

	def presentScreen(self, screen):
		setAndPresentScreen(self.experiment.disp, screen)
		self.experiment.input.waitKeys(keyList=['space', 'enter', 'left', 'right', 'down'])
		self.experiment.disp.show()

	def cycleThroughTrials(self, whichPart):
		curFamilTrialIndex = 1

		if whichPart == "familiarizationPhase":
			for curTrial in self.familTrialListMatrix.trialList:
				print(curTrial)
				if curTrial['trialType'] == "training":
					self.presentTrial(curTrial, curFamilTrialIndex, stage = "familiarization", getInput = "no")

					self.experiment.win.flip()
				if curTrial['trialType'] == 'AG':
					self.presentAGTrial(curTrial, self.trialFieldNames, getInput = "no", duration = curTrial['AGTime'])
					print("flip")
					self.experiment.win.flip()
				if curTrial['trialType'] == 'PauseAG':
					self.presentAGTrial(curTrial, self.trialFieldNames ,getInput = "yes", duration = 0)
					self.experiment.win.flip()
				curFamilTrialIndex += 1

		elif whichPart == "activeTraining":
			curActiveTrainingIndex = 1
			for curTrial in self.activeTrainingTrialsMatrix.trialList:
				print(curTrial)
				if curTrial['trialType'] == 'AG':
					self.presentAGTrial(curTrial, self.activeTrainingTrialFieldNames ,getInput = "no", duration = curTrial['AGTime'])
					self.experiment.win.flip()
				if curTrial['trialType'] == 'activeTraining':
					self.presentActiveTrial(curTrial, curActiveTrainingIndex, self.activeTrainingTrialFieldNames, "activeTraining")
					curActiveTrainingIndex += 1

		elif whichPart == "lwlTest":
			curlwlTestIndex = 1
			for curTrial in self.lwlTestTrialsMatrix.trialList:
				print(curTrial)
				if curTrial['trialType'] == 'AG':
					self.presentAGTrial(curTrial, self.lwlTrialFieldNames ,getInput = "no", duration = curTrial['AGTime'])
					self.experiment.win.flip()
				if curTrial['trialType'] == 'test':
					self.presentLWLTrial(curTrial, curlwlTestIndex, self.lwlTrialFieldNames,  
						  curTrial['trialStartSilence'],
						   curTrial['trialAudioDuration'], 
						   curTrial['trialEndSilence'],"LWLTest")
					curlwlTestIndex += 1

		elif whichPart == "activeTest":
			curActiveTestIndex = 1
			for curTrial in self.activeTestTrialsMatrix.trialList:
				print(curTrial)

				self.presentActiveTrial(curTrial, curActiveTestIndex, self.activeTrialFieldNames, "activeTest")
				curActiveTestIndex += 1

	def presentAGTrial(self, curTrial, trialFieldNames, getInput, duration):

		# flip screen
		self.experiment.disp.fill(self.experiment.blackScreen)
		self.experiment.disp.show()

		# pause for duration of ISI
		libtime.pause(self.ISI)
		if self.experiment.subjVariables['eyetracker'] == "yes":
			self.experiment.tracker.start_recording()
			logData = "Experiment %s subjCode %s trialOrder %s" % (
			self.experiment.expName, self.experiment.subjVariables['subjCode'], self.experiment.subjVariables['order'])
			print(trialFieldNames)
			for field in trialFieldNames:
				logData += " "+field+" "+str(curTrial[field])
			#print("would have logged " + logData)
			self.experiment.tracker.log(logData)

		if curTrial['AGType'] == "image":
			# create picture
			curPic = self.imageMatrix[curTrial['AGImage']][0]
			# position in center of screen
			curPic.pos = self.pos['center']
			# create screen
			agScreen = libscreen.Screen()
			# build screen
			buildScreenPsychoPy(agScreen, [curPic])

			# present screen
			# see stimPresPyGaze to see details on setAndPresentScreen
			# basically, it simply fills the display with the specified screen (setting) and then flips (shows) the screen (presenting)
			setAndPresentScreen(self.experiment.disp, agScreen)
			if self.experiment.subjVariables['eyetracker'] == "yes":
				# log event
				self.experiment.tracker.log("presentAGImage")

			if curTrial['AGAudio'] != "none":
				playAndWait(self.soundMatrix[curTrial['AGAudio']], waitFor=0)

				if self.experiment.subjVariables['eyetracker'] == "yes":
					# log event
					self.experiment.tracker.log("presentAGAudio")

			# display for rest of ag Time
			libtime.pause(duration)

		elif curTrial['AGType'] == "movie":

			if curTrial['AGAudio'] != "none":
				curSound = self.AGsoundMatrix[curTrial['AGAudio']]
				#just use the psychopy prefs, not the winsound stuff...
				curSound.play()

			# load movie stim

			mov = self.AGmovieMatrix[curTrial['AGVideo']]
			mov.size = (self.x_length, self.y_length)

			mov.play()

			while not mov.isFinished:
				mov.draw()
				self.experiment.win.flip()
			
			mov.stop()

			#if curTrial['AGAudio'] != "none":
		#		curSound = self.AGsoundMatrix[curTrial['AGAudio']]

		if self.experiment.subjVariables['eyetracker'] == "yes":
			# stop eye tracking
			self.experiment.tracker.log("endAG")
			self.experiment.tracker.stop_recording()

		self.experiment.disp.fill(self.experiment.blackScreen)

	def presentTrial(self, curTrial, curTrialIndex, stage, getInput):
		"""
		Present a familiarization trial with looming PNG images rather than videos.
		
		Parameters:
		-----------
		curTrial : dict
			Current trial information from the CSV
		curTrialIndex : int
			Index of the current trial
		stage : str
			Current experimental stage
		getInput : str
			Whether to get input from participant
		"""
		self.experiment.disp.show()
		libtime.pause(self.ISI)

		# start eyetracking
		if self.experiment.subjVariables['eyetracker'] == "yes":
			self.experiment.tracker.start_recording()
			logData = "Experiment %s subjCode %s trialOrder %s" % (
				self.experiment.expName, self.experiment.subjVariables['subjCode'],
				self.experiment.subjVariables['order'])

			for field in self.trialFieldNames:
				logData += " "+field+" "+str(curTrial[field])
			#print("would have logged " + logData)
			self.experiment.tracker.log(logData)

		#grab correct movie, sound, and images
		curSound = self.soundMatrix[curTrial['label']]

		trial_duration = curTrial["trialDuration"] #ms

		# set image sizes

		topLeftImageName = curTrial['topLeftImage']
		topRightImageName = curTrial['topRightImage']
		bottomRightImageName = curTrial['bottomRightImage']
		bottomLeftImageName = curTrial['bottomLeftImage']

		topRightImage = self.imageMatrix[topRightImageName][0]
		topLeftImage = self.imageMatrix[topLeftImageName][0]
		bottomRightImage = self.imageMatrix[bottomRightImageName][0]
		bottomLeftImage = self.imageMatrix[bottomLeftImageName][0]

		topRightImage.pos = self.pos['topRight']
		topLeftImage.pos = self.pos['topLeft']
		bottomRightImage.pos = self.pos['bottomRight']
		bottomLeftImage.pos = self.pos['bottomLeft']

		topRightImage.size = self.fam_stim_size
		topLeftImage.size = self.fam_stim_size
		bottomRightImage.size = self.fam_stim_size
		bottomLeftImage.size = self.fam_stim_size

		topRightRect = visual.Rect(
						self.experiment.win,
						width=self.fam_rect_size[0], height=self.fam_rect_size[1],
						fillColor="lightgray", lineColor=None,
						pos=self.pos['topRight'])
		
		topLeftRect = visual.Rect(
						self.experiment.win,
						width=self.fam_rect_size[0], height=self.fam_rect_size[1],
						fillColor="lightgray", lineColor=None,
						pos=self.pos['topLeft'])
		
		bottomRightRect = visual.Rect(
						self.experiment.win,
						width=self.fam_rect_size[0], height=self.fam_rect_size[1],
						fillColor="lightgray", lineColor=None,
						pos=self.pos['bottomLeft'])
		bottomLeftRect = visual.Rect(
						self.experiment.win,
						width=self.fam_rect_size[0], height=self.fam_rect_size[1],
						fillColor="lightgray", lineColor=None,
						pos=self.pos['bottomRight'])

		# Draw initial images
		topRightRect.draw()
		topLeftRect.draw()
		bottomRightRect.draw()
		bottomLeftRect.draw()

		topRightImage.draw()
		topLeftImage.draw()
		bottomRightImage.draw()
		bottomLeftImage.draw()
		self.experiment.win.flip()

		topRightAnimation = LoomAnimation(
			stim=topRightImage,
			win=self.experiment.win,
			init_size=topRightImage.size,
			target_size_factor=self.targetSizeFactor,
			loom_in_duration=self.loomDuration,
			loom_out_duration=self.loomDuration,
			wiggle_duration=self.wiggleDuration,
			jiggle_amplitude=self.jiggleAmplitude,
			jiggle_frequency=self.jiggleFrequency,
			looping= True
		)

		topLeftAnimation = LoomAnimation(
			stim=topLeftImage,
			win=self.experiment.win,
			init_size=topLeftImage.size,
			target_size_factor=self.targetSizeFactor,
			loom_in_duration=self.loomDuration,
			loom_out_duration=self.loomDuration,
			wiggle_duration=self.wiggleDuration,
			jiggle_amplitude=self.jiggleAmplitude,
			jiggle_frequency=self.jiggleFrequency,
			looping= True
		)

		bottomRightAnimation = LoomAnimation(
			stim=bottomRightImage,
			win=self.experiment.win,
			init_size=bottomRightImage.size,
			target_size_factor=self.targetSizeFactor,
			loom_in_duration=self.loomDuration,
			loom_out_duration=self.loomDuration,
			wiggle_duration=self.wiggleDuration,
			jiggle_amplitude=self.jiggleAmplitude,
			jiggle_frequency=self.jiggleFrequency,
			looping= True
		)

		bottomLeftAnimation = LoomAnimation(
			stim=bottomLeftImage,
			win=self.experiment.win,
			init_size=bottomLeftImage.size,
			target_size_factor=self.targetSizeFactor,
			loom_in_duration=self.loomDuration,
			loom_out_duration=self.loomDuration,
			wiggle_duration=self.wiggleDuration,
			jiggle_amplitude=self.jiggleAmplitude,
			jiggle_frequency=self.jiggleFrequency,
			looping= True
		)
		
		trialTimerStart = libtime.get_time()
		libtime.pause(self.startSilence)

		curSound.play()
		
		if self.experiment.subjVariables['eyetracker'] == "yes":
			# log event
			self.experiment.tracker.log("startScreen")

		while (libtime.get_time() - trialTimerStart) < trial_duration:
			elapsed_time = libtime.get_time() - trialTimerStart
			
			topRightRect.draw()
			topLeftRect.draw()
			bottomRightRect.draw()
			bottomLeftRect.draw()

			topLeftAnimation.update()
			topRightAnimation.update()
			bottomLeftAnimation.update()
			bottomRightAnimation.update()
			

			self.experiment.win.flip()

			keys = event.getKeys()
			if 'escape' in keys:
				break

		curSound.stop()
		
		libtime.pause(self.endSilence)

		######Stop Eyetracking######

		# trialEndTime
		trialTimerEnd = libtime.get_time()
		# trial time
		trialTime = trialTimerEnd - trialTimerStart
		if self.experiment.subjVariables['eyetracker'] == "yes":
			# stop eye tracking
			self.experiment.tracker.log("endScreen")
			self.experiment.tracker.stop_recording()

		self.experiment.disp.fill()

		fieldVars = []
		for curField in self.trialFieldNames:
			fieldVars.append(curTrial[curField])

		[header, curLine] = createRespNew(self.experiment.subjInfo, self.experiment.subjVariables, self.trialFieldNames,
										  fieldVars,
										  a_curTrialIndex=curTrialIndex,
										  b_trialStart=trialTimerStart,
										  c_expTimer=trialTimerEnd,
										  d_trialTime=trialTime)

		writeToFile(self.experiment.trainingOutputFile, curLine)

	def presentActiveTrial(self, curTrial, curActiveTrialIndex, trialFieldNames, stage):
		print("Start active")
		csv_header = ["timestamp","eyetrackerLog",  "sampledLook", "avgPOS", "curLook",  "response"]
		trigger_filename = 'data/' + stage + '/' + 'tracking_data_' + self.experiment.subjVariables['subjCode'] + '.txt'


		with open(trigger_filename, "w", newline='') as file:
			writer = csv.writer(file)
			writer.writerow(csv_header)

		self.experiment.disp.show()

		leftStimName = curTrial['leftStim']
		rightStimName = curTrial['rightStim']

		# Find Psychopy Stim from image matrix
		# Left
		self.leftStimImage  = self.imageMatrix[leftStimName][0]
		self.leftStimImage.pos = self.pos['centerLeft']
		self.leftStimImage.size = self.stim_size

		# Right
		self.rightStimImage = self.imageMatrix[rightStimName][0]
		self.rightStimImage.pos = self.pos['centerRight']
		self.rightStimImage.size = self.stim_size
		self.leftRect = visual.Rect(
			self.experiment.win,
			width=600, height=600,
			fillColor="lightgray", lineColor=None,
			pos=self.pos['centerLeft']
		)

		self.rightRect = visual.Rect(
			self.experiment.win,
			width=600, height=600,
			fillColor="lightgray", lineColor=None,
			pos=self.pos['centerRight']
		)

		# Draw background rectangles first, then the images
		#self.leftRect.draw()
		#self.rightRect.draw()
		#self.leftStimImage.draw()
		#self.rightStimImage.draw()
		
		self.experiment.win.flip()

		# Initialize eyetracker

		#libtime.pause(self.ISI)

		if self.experiment.subjVariables['eyetracker'] == 'yes':
			self.experiment.tracker.start_recording()
			logData = "Experiment %s subjCode %s trialOrder %s" % (
				self.experiment.expName, self.experiment.subjVariables['subjCode'],
				self.experiment.subjVariables['order'])
			for field in trialFieldNames:
				logData += " " + field + " " + str(curTrial[field])
			self.experiment.tracker.log(logData)

		if self.experiment.subjVariables['eyetracker'] == "yes":
			# log event
			self.experiment.tracker.log("startScreen")

		# Create adnimations
		leftAnimation = LoomAnimation(
			stim=self.leftStimImage,
			win=self.experiment.win,
			init_size=self.leftStimImage.size,
			target_size_factor=self.targetSizeFactor,
			loom_in_duration=self.loomDuration,
			loom_out_duration=self.loomDuration,
			wiggle_duration=self.wiggleDuration,
			jiggle_amplitude=self.jiggleAmplitude,
			jiggle_frequency=self.jiggleFrequency,
			looping= True  # Enable looping for continuous animation
		)
		rightAnimation = LoomAnimation(
			stim=self.rightStimImage,
			win=self.experiment.win,
			init_size=self.rightStimImage.size,
			target_size_factor=self.targetSizeFactor,
			loom_in_duration=self.loomDuration,
			loom_out_duration=self.loomDuration,
			wiggle_duration=self.wiggleDuration,
			jiggle_amplitude=self.jiggleAmplitude,
			jiggle_frequency=self.jiggleFrequency,
			looping= True   # Enable looping for continuous animation
		)

		# pause for non-contingent frozen display
		
		# start playing each video for 1 sec
		activefamstartleft = libtime.get_time()
		self.activefamtimeoutTime = 2000
		while libtime.get_time() - activefamstartleft < self.activefamtimeoutTime:
			self.leftRect.draw()
			self.leftStimImage.draw()
			self.experiment.win.flip()

		activefamstartright = libtime.get_time()
		while libtime.get_time() - activefamstartright < self.activefamtimeoutTime:
			self.rightRect.draw()
			self.rightStimImage.draw() 
			self.experiment.win.flip()

		libtime.pause(500)

		start = libtime.get_time()
		while libtime.get_time() - start < 1500:
			stim = visual.TextStim(self.experiment.win, '+',
                       color="white")
			stim.size = 300
			#self.rightStimMov.draw()
			#self.leftStimMov.draw()
			stim.draw()
			self.experiment.win.flip()

		if self.experiment.subjVariables['eyetracker'] == "yes":
			# log event
			self.experiment.tracker.log("startContingent")
		log_file_list = [libtime.get_time(), "startContingent", None
							 , None, None
							 , None]
		with open(trigger_filename, 'a', newline='') as file:
			writer = csv.writer(file)
			writer.writerow(log_file_list)

		#### Contingent Start #
		trialTimerStart = libtime.get_time()
		selectionNum = 0
		t0Left = None
		t0Right = None
		t0None = None
		t0Away = None
		countLeft = 0
		countRight = 0
		countDiff = 0
		countAway = 0
		response = None
		gazeCon = False
		contingent = False
		eventTriggered = 0
		firstTrigger = 0
		lastms = []

		# list of events
		rt_list = []
		response_list = []
		chosenStim_list = []
		chosenLabel_list = []
		chosenAudio_list = []
		chosenRole_list = []
		audioPlayTime_list = []
		audioStartTime_list = []
		audioStopTime_list = []
		eventStartTime_list = []

		leftAnimationActive = False
		rightAnimationActive = False
		activeAnimation = None
		animating = False

		# Main trial loop
		while libtime.get_time() - trialTimerStart < self.timeoutTime:

			# Update animations based on current state
			if leftAnimationActive:
				leftAnimation.update()
			if rightAnimationActive:
				rightAnimation.update()

			self.leftRect.draw()
			self.rightRect.draw()
			self.leftStimImage.draw()
			self.rightStimImage.draw()
			self.experiment.win.flip()

			if self.experiment.subjVariables['activeMode'] == 'gaze':
				# get gaze position
				# get current sampled gaze position
				sampledGazePos = self.experiment.tracker.sample()
				print(sampledGazePos)

				if self.aoiLeft.contains(sampledGazePos):
					if t0Left == None:
						t0Left = libtime.get_time()
					curLook = "left"
				elif self.aoiRight.contains(sampledGazePos):
					#countRight += 1
					if t0Right == None:
						t0Right = libtime.get_time()
					curLook = "right"
				elif sampledGazePos == self.lookAwayPos:
					if t0Away == None:
						t0Away = libtime.get_time()
					curLook = "away"
				else:
					if t0None == None:
						t0None = libtime.get_time()
					curLook = "none"

			if self.experiment.subjVariables['activeMode'] == 'input':
				curLook = "away"
				keys = self.experiment.input.getKeys(waitRelease=False, clear=False)
				keynames = [key.name for key in keys]


				if (keys and not keys[-1].duration): #if key is being held down
					currkey = keys[-1].name

					if currkey == 'left':
						if t0Left == None:
							t0Left = libtime.get_time()
						curLook = "left"
					elif currkey == 'right':
						#countRight += 1
						if t0Right == None:
							t0Right = libtime.get_time()
						curLook = "right"
					elif currkey == None:
						if t0None == None:
							t0None = libtime.get_time()
						curLook = "none"
					else:
						if t0Away == None:
							t0Away = libtime.get_time()
						curLook = "away"
					print(curLook)

			# If an event has already been triggered, it can not be the first trigger
			if eventTriggered == 1:
				firstTrigger = 0

			# If an event is not currently triggered...
			elif eventTriggered == 0:

				if (t0Left is not None) and libtime.get_time() - t0Left >= self.firstTriggerThreshold:

					selectionNum += 1
					eventTriggered = 1
					animating = True
					if firstTrigger == 0:
						firstTrigger = 1

					response = "left"	

					eventTriggerTime = libtime.get_time()
					eventStartTime_list.append(eventTriggerTime)
					rt = eventTriggerTime - trialTimerStart
					rt_list.append(rt)
					selectionTime = libtime.get_time()
					response_list.append(response)
					leftAnimationActive = True
					activeAnimation = leftAnimation

					# log event
					if self.experiment.subjVariables['eyetracker'] == 'yes':
						self.experiment.tracker.log("selection" + str(selectionNum) + "    " + curLook)
					log_file_list = [libtime.get_time(), "selection" + str(selectionNum) + "    " + curLook,
										 curLook, response]

					with open(trigger_filename, 'a', newline='') as file:
						writer = csv.writer(file)
						writer.writerow(log_file_list)

				elif (t0Right is not None) and libtime.get_time() - t0Right >= self.firstTriggerThreshold:
					selectionNum += 1
					eventTriggered = 1
					animating = True
					if firstTrigger == 0:
						firstTrigger = 1

					eventTriggerTime = libtime.get_time()
					eventStartTime_list.append(eventTriggerTime)
					rt = eventTriggerTime - trialTimerStart
					rt_list.append(rt)

					# log event
					if self.experiment.subjVariables['eyetracker'] == 'yes':
						self.experiment.tracker.log("selection" + str(selectionNum) + "    " + curLook)
					log_file_list = [libtime.get_time(), "selection" + str(selectionNum) + "    " + curLook,
										 curLook, response]

					with open(trigger_filename, 'a', newline='') as file:
						writer = csv.writer(file)
						writer.writerow(log_file_list)
					selectionTime = libtime.get_time()
					gazeCon = True
					contingent = True
					response = "right"
					response_list.append(response)
					rightAnimationActive = True
					activeAnimation = rightAnimation

			if firstTrigger == 1:
				chosenAudio = curTrial[response + 'Audio']
				chosenStim_list.append(response + 'Image')  # Store which image was chosen
				chosenAudio_list.append(chosenAudio)

				self.soundMatrix[chosenAudio].setLoops(-1)
				self.soundMatrix[chosenAudio].play(loops=3)

				if activeAnimation:
					activeAnimation.resume()

				audioTime = libtime.get_time()
				audioStartTime_list.append(audioTime)

				if self.experiment.subjVariables['eyetracker'] == "yes":
					# log audio event
					self.experiment.tracker.log("audio" + str(selectionNum))
				log_file_list = [libtime.get_time(), "audio" + str(selectionNum),
									 curLook, response]

				with open(trigger_filename, 'a', newline='') as file:
					writer = csv.writer(file)
					writer.writerow(log_file_list)
				
				firstTrigger = 0

			if eventTriggered == 1 and animating:
				# Handle looking away
				if curLook == "away" and (response == "left" or response == "right"):
					if t0Away == None:
						t0Away = libtime.get_time()
						# Pause the animation when gaze moves away
						if response == "left" and leftAnimationActive:
							leftAnimation.pause()
						elif response == "right" and rightAnimationActive:
							rightAnimation.pause()

				# If the eyetracker refinds, reset to none?
				elif curLook == response:
					t0Away = None
					t0None = None
					if response == "left" and leftAnimationActive:
						leftAnimation.resume()
					elif response == "right" and rightAnimationActive:
						rightAnimation.resume()
			
				elif curLook == "none" and (response == "left" or response == "right"):
					if t0None == None:
						t0None = libtime.get_time()
						# Pause the animation
						if response == "left" and leftAnimationActive:
							leftAnimation.pause()
						elif response == "right" and rightAnimationActive:
							rightAnimation.pause()

				# Build threshold booleans outside if statement for clarity
				triggerEnd = False
				if t0Away != None:
					if libtime.get_time() - t0Away >= self.awayThreshold:
						triggerEnd = True
						print("End Away:", libtime.get_time() - t0Away)
				elif t0None != None:
					if libtime.get_time() - t0None >= self.noneThreshold:
						triggerEnd = True
						print("End None:", libtime.get_time() - t0None)

				# check if the infant has switched
				if (curLook != response and triggerEnd) or libtime.get_time() - audioTime > self.maxLabelTime:
					t0None = None
					t0Away = None
					t0Right = None
					t0Left = None

					eventTriggered = 0
					animating = False

					# Stop sound
					self.soundMatrix[chosenAudio].stop()
					
					# Reset animations
					if leftAnimationActive:
						leftAnimation.pause()
						leftAnimation.reset_stimulus()
						leftAnimationActive = False
					if rightAnimationActive:
						rightAnimation.pause()
						rightAnimation.reset_stimulus()
						rightAnimationActive = False
					
					activeAnimation = None

					# Record timing data
					audioStopTime = libtime.get_time()
					audioPlayTime_list.append(audioStopTime - audioTime)
					audioStopTime_list.append(audioStopTime)

					# reset screen
					if self.experiment.subjVariables['eyetracker'] == "yes":
						# log audio event end
						self.experiment.tracker.log(
							"audioEnd" + str(selectionNum))
					log_file_list = [libtime.get_time(), "audioEnd" + str(selectionNum),  curLook, response]

					with open(trigger_filename, 'a', newline='') as file:
						writer = csv.writer(file)
						writer.writerow(log_file_list)

			log_file_list = [libtime.get_time(), None, curLook, response]

			with open(trigger_filename, 'a', newline='') as file:
				writer = csv.writer(file)
				writer.writerow(log_file_list)

		if eventTriggered == 1:
			# Stop sound
			if 'chosenAudio' in locals() and chosenAudio in self.soundMatrix:
				self.soundMatrix[chosenAudio].stop()
				
			# Record animation end
			if 'audioTime' in locals():
				audioStopTime = libtime.get_time()
				audioPlayTime_list.append(audioStopTime - audioTime)
				audioStopTime_list.append(audioStopTime)
			
			# Reset animations
			if leftAnimationActive:
				leftAnimation.reset_stimulus()
			if rightAnimationActive:
				rightAnimation.reset_stimulus()
		self.experiment.disp.fill(self.experiment.blackScreen)
		self.experiment.disp.show()
		# Clear screen
		self.experiment.disp.fill(self.experiment.blackScreen)
		self.experiment.disp.show()

		# Record trial end
		trialTimerEnd = libtime.get_time()
		trialTime = trialTimerEnd - trialTimerStart
		
		if self.experiment.subjVariables['eyetracker'] == "yes":
			# Stop eye tracking
			self.experiment.tracker.log("stopScreen")
			self.experiment.tracker.stop_recording()

	def presentLWLTrial(self, curTrial, culwlTestIndex, trialFieldNames, 
					 trialStartSilence, trialAudioDuration, trialEndSilence, stage):
		print("start LWL")
		self.experiment.disp.show()
		libtime.pause(self.ISI + random.choice([0, 100, 200]))

		print(curTrial)
		if self.experiment.subjVariables['eyetracker'] == "yes":
			self.experiment.tracker.start_recording()
			logData = "Experiment %s subjCode %s trialOrder %s" % (
				self.experiment.expName, self.experiment.subjVariables['subjCode'],
				self.experiment.subjVariables['order'])

			for field in trialFieldNames:
				logData += " "+field+" "+str(curTrial[field])
			print("would have logged " + logData)
			self.experiment.tracker.log(logData)
		
		curTargetLocation = curTrial['TargetObjectPos']
		curTargetTrialCoordinates = self.pos[curTargetLocation]

		curDistracterLocation = curTrial['DistracterObjectPos']
		curDistracterTrialCoordinates = self.pos[curDistracterLocation]

		curTargetPic = self.imageMatrix[curTrial['TargetImage']][0]  # psychopy image stimulus
		curDistracterPic = self.imageMatrix[curTrial['DistracterImage']][0]  # psychopy image stimulus
		curTargetPic.size = self.stim_size
		curTargetPic.pos = curTargetTrialCoordinates
		curDistracterPic.size = self.stim_size
		curDistracterPic.pos = curDistracterTrialCoordinates
		targetRect = visual.Rect(
			self.experiment.win,
			width=600, height=600,
			fillColor="lightgray", lineColor=None,
			pos=curTargetTrialCoordinates
		)

		distracterRect = visual.Rect(
			self.experiment.win,
			width=600, height=600,
			fillColor="lightgray", lineColor=None,
			pos=curDistracterTrialCoordinates
		)
		testScreen = libscreen.Screen()
		buildScreenPsychoPy(testScreen, [targetRect, distracterRect])
		buildScreenPsychoPy(testScreen, [curTargetPic, curDistracterPic])

		trialTimerStart = libtime.get_time()
		setAndPresentScreen(self.experiment.disp, testScreen)

		if self.experiment.subjVariables['eyetracker'] == "yes":
            # log event
			self.experiment.tracker.log("testScreen")
		
		libtime.pause(trialStartSilence)

		playAndWait(self.soundMatrix[curTrial['Audio']], waitFor=0)

		if self.experiment.subjVariables['eyetracker'] == "yes":
            # log event
			self.experiment.tracker.log("audioOnset")

		libtime.pause(trialAudioDuration)

		if self.experiment.subjVariables['eyetracker'] == "yes":
			self.experiment.tracker.log("audioOffset")
        # silence at end of trial

		libtime.pause(trialEndSilence)

		self.experiment.disp.fill()
	

	def EndDisp(self):
		# show the screen with no stars filled in
		# self.stars['0'][0].draw()
		# print(self.stars)
		# win.flip()

		curStar = self.stars['0'][0]
		curStar.size = (self.x_length, self.y_length)
		# create screen
		endScreen = libscreen.Screen()
		# build screen
		buildScreenPsychoPy(endScreen, [curStar])

		# present screen
		setAndPresentScreen(self.experiment.disp, endScreen)

		core.wait(1)

		# iterate to fill in each star
		for i in range(1, 6, 1):
			# self.stars[str(i)][0].draw()
			#  win.flip()
			curStar = self.stars[str(i)][0]
			curStar.size = (self.x_length, self.y_length)
			# build screen
			buildScreenPsychoPy(endScreen, [curStar])
			# present screen
			setAndPresentScreen(self.experiment.disp, endScreen)

			self.AGsoundMatrix['ding'].play()
			core.wait(.5)
			self.AGsoundMatrix['ding'].stop()

		# have the stars jiggle
		self.AGsoundMatrix['applause'].play()
		self.AGsoundMatrix['done'].volume = 2
		self.AGsoundMatrix['done'].play()

		for i in range(4):
			# self.stars['5'][0].draw()
			# win.flip()
			curStar = self.stars['5'][0]
			curStar.size = (self.x_length, self.y_length)
			# build screen
			buildScreenPsychoPy(endScreen, [curStar])
			# present screen
			setAndPresentScreen(self.experiment.disp, endScreen)

			core.wait(.5)
			# self.stars['5_left'][0].draw()
			# win.flip()

			curStar = self.stars['5_left'][0]
			curStar.size = (self.x_length, self.y_length)
			# build screen
			buildScreenPsychoPy(endScreen, [curStar])
			# present screen
			setAndPresentScreen(self.experiment.disp, endScreen)
			core.wait(.5)

			# self.stars['5'][0].draw()
			# win.flip()
			# core.wait(.5)
			# self.stars['5_right'][0].draw()
			# win.flip()
			# core.wait(.5)

			curStar = self.stars['5'][0]
			curStar.size = (self.x_length, self.y_length)
			# build screen
			buildScreenPsychoPy(endScreen, [curStar])
			# present screen
			setAndPresentScreen(self.experiment.disp, endScreen)

			core.wait(.5)
			# self.stars['5_left'][0].draw()
			# win.flip()

			curStar = self.stars['5_right'][0]
			curStar.size = (self.x_length, self.y_length)
			# build screen
			buildScreenPsychoPy(endScreen, [curStar])
			# present screen
			setAndPresentScreen(self.experiment.disp, endScreen)
			core.wait(.5)


currentExp = Exp()

currentPresentation = ExpPresentation(currentExp)

currentPresentation.initializeExperiment()
currentPresentation.presentScreen(currentPresentation.initialScreen)
currentPresentation.cycleThroughTrials(whichPart = "familiarizationPhase")
currentPresentation.cycleThroughTrials(whichPart= "lwlTest")
currentPresentation.cycleThroughTrials(whichPart = "activeTraining")
currentPresentation.cycleThroughTrials(whichPart = "activeTest")
currentPresentation.EndDisp()