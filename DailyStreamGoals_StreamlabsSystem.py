# ---------------------------
# Import Libraries
# ---------------------------
import json
import os
import codecs
import sys
import time


# ---------------------------
# Import any custom modules under the "sys.path.append(os.path.dirname(__file__))" line
# Required for importing modules from the main scripts directory
# StreamLabs Thread: https://ideas.streamlabs.com/ideas/SL-I-3971
# ---------------------------
sys.path.append(os.path.dirname(__file__))
from datetime import datetime, date, time, timedelta


# ---------------------------
# [Required] Script Information
# ---------------------------
ScriptName = "Daily Stream Goals"
Website = "NA"
Description = "Track daily goals subs, follows, cheers, and donations."
Creator = "Level Headed Gamers"
Version = "0.1.0"


# ---------------------------
# Define Global Variables
# ---------------------------
configFile = "config.json"
settings = {}

path = os.path.dirname(__file__)
outputFileDir = os.path.join(path, "Files")
resetDateFilePath = os.path.join(outputFileDir, "ResetDate.txt")
subCurrentFilePath = os.path.join(outputFileDir, "SubCurrent.txt")
subTargetFilePath = os.path.join(outputFileDir, "SubTarget.txt")
followCurrentFilePath = os.path.join(outputFileDir, "FollowCurrent.txt")
followTargetFilePath = os.path.join(outputFileDir, "FollowTarget.txt")

# ---------------------------
# [Required] Initialize Data (Only called on load)
# ---------------------------
def Init():
	global settings
	global path

	try:
		with codecs.open(os.path.join(path, configFile), encoding='utf-8-sig', mode='r') as file:
			settings = json.load(file, encoding='utf-8-sig')
	except:
		settings = {
			"resetHour": 0,
			"subTarget": 1,
			"followTarget": 5
		}

	# Validate Files directory.
	if not os.path.exists(outputFileDir):
		os.mkdir(outputFileDir)

	settings["currentResetDate"] = ReadResetDate()
	settings["currentSubs"] = ReadCurrentSubs()
	settings["currentFollows"] = ReadCurrentFollows()

	WriteTargetSubs(settings["subTarget"])
	WriteTargetFollows(settings["followTarget"])
	
	CheckAndProcessReset()

	return

# ---------------------------
# [Required] Execute Data / Process messages
# ---------------------------
def Execute(data):

	# TODO - Capture twitch events here.

	return


# ---------------------------
# [Optional] ScriptToggled (Notifies you when a user disables your script or enables it)
# ---------------------------
def ScriptToggled(state):
	return


# ---------------------------
# [Optional] Reload Settings (Called when a user clicks the Save Settings button in the Chatbot UI)
# ---------------------------
def ReloadSettings(jsonData):
	Init()
	return


# ---------------------------
# [Required] Tick method (Gets called during every iteration even when there is no incoming data)
# ---------------------------
def Tick():
	return


# ---------------------------
# Helper method used by UI_Config.json to open the README.md file from script settings ui.
# ---------------------------
def OpenReadMe():
	location = os.path.join(os.path.dirname(__file__), "README.md")
	os.startfile(location)
	return

############################################

def ReadResetDate():
	resetDate = None
	if os.path.isfile(resetDateFilePath):
		with open(resetDateFilePath) as f:
			resetDateText = f.readline()
			resetDateFromFile = datetime.strptime(resetDateText, "%Y-%m-%dT%H:%M:%S.%f")
			# Reset hour again in the event the user changed the reset hour after the file was created.
			resetDateFromFile.replace(hour=int(settings["resetHour"]))
			resetDate = resetDateFromFile
	else:
		resetDate = datetime.now().replace(hour=int(settings["resetHour"]), minute=0)
		resetDate += timedelta(days=1)

		WriteResetDate(resetDate)
	return resetDate


def WriteResetDate(dateToWrite):
	resetDateFile = open(resetDateFilePath, "w")
	resetDateFile.write(dateToWrite.isoformat())
	resetDateFile.close()


def ReadCurrentSubs():
	currentSubs = 0
	if os.path.isfile(subCurrentFilePath):
		with open(subCurrentFilePath) as f:
			currentSubs = int(f.readline())
	else:
		WriteCurrentSubs(currentSubs)
	return currentSubs


def WriteCurrentSubs(count):
	subsFile = open(subCurrentFilePath, "w")
	subsFile.write(str(count))
	subsFile.close()


def WriteTargetSubs(count):
	subsFile = open(subTargetFilePath, "w")
	subsFile.write(str(count))
	subsFile.close()


def ReadCurrentFollows():
	currentFollows = 0
	if os.path.isfile(followCurrentFilePath):
		with open(followCurrentFilePath) as f:
			currentFollows = int(f.readline())
	else:
		WriteCurrentFollows(currentFollows)
	return currentFollows


def WriteCurrentFollows(count):
	followsFile = open(followCurrentFilePath, "w")
	followsFile.write(str(count))
	followsFile.close()


def WriteTargetFollows(count):
	followsFile = open(followTargetFilePath, "w")
	followsFile.write(str(count))
	followsFile.close()

##########################################

def CheckAndProcessReset():
	if datetime.now() >= settings["currentResetDate"]:
		# Reset settings
		nextDateTime = datetime.now().replace(hour=int(settings['resetHour']), minute=0)
		nextDateTime += timedelta(days=1)

		settings["currentResetDate"] = nextDateTime
		settings["currentSubs"] = 0
		settings["currentFollows"] = 0

		WriteResetDate(nextDateTime)
		WriteCurrentSubs(0)
		WriteCurrentFollows(0)
	return