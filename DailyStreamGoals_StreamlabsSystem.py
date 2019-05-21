# ---------------------------
# Import Libraries
# ---------------------------
import json
import os
import codecs
import sys
import time
import clr

# ---------------------------
# Import any custom modules under the "sys.path.append(os.path.dirname(__file__))" line
# Required for importing modules from the main scripts directory
# StreamLabs Thread: https://ideas.streamlabs.com/ideas/SL-I-3971
# ---------------------------
sys.path.append(os.path.dirname(__file__))
from datetime import datetime, date, time, timedelta
clr.AddReference("IronPython.Modules.dll")
clr.AddReferenceToFileAndPath(os.path.join(os.path.dirname(os.path.realpath(__file__)), "StreamlabsEventReceiver.dll"))
from StreamlabsEventReceiver import StreamlabsEventClient


# ---------------------------
# [Required] Script Information
# ---------------------------
ScriptName = "Daily Stream Goals"
Website = "https://github.com/Vizionz/daily-stream-goals-streamlabs"
Description = "Track daily goals for subs, follows, cheers, and donations. Utilizes 'Streamlabs Event Receiver Boilerplate v1.0.1' from Ocgineer."
Creator = "Level Headed Gamers"
Version = "1.1.0"


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
subFullOutputPath = os.path.join(outputFileDir, "SubOutput.txt")
followCurrentFilePath = os.path.join(outputFileDir, "FollowCurrent.txt")
followTargetFilePath = os.path.join(outputFileDir, "FollowTarget.txt")
followFullOutputPath = os.path.join(outputFileDir, "FollowOutput.txt")

EventReceiver = None


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
			"resetHour": 3,
			"subTarget": 1,
			"subDivisor": "/",
			"followTarget": 5,
			"followDivisor": "/",
			"socket_token": ""
		}

	# Validate Files directory.
	if not os.path.exists(outputFileDir):
		os.mkdir(outputFileDir)

	settings["currentResetDate"] = ReadResetDate()
	settings["currentSubs"] = ReadCurrentSubs()
	settings["currentFollows"] = ReadCurrentFollows()

	SimpleWriteToFile(subTargetFilePath, settings["subTarget"])
	SimpleWriteToFile(followTargetFilePath, settings["followTarget"])
	SimpleWriteToFile(followFullOutputPath, str(settings["currentFollows"]) + settings["followDivisor"] + str(settings["followTarget"]))
	SimpleWriteToFile(subFullOutputPath, str(settings["currentSubs"]) + settings["subDivisor"] + str(settings["subTarget"]))

	CheckAndProcessReset()

	## Init the Streamlabs Event Receiver
	global EventReceiver
	EventReceiver = StreamlabsEventClient()
	EventReceiver.StreamlabsSocketConnected += EventReceiverConnected
	EventReceiver.StreamlabsSocketDisconnected += EventReceiverDisconnected
	EventReceiver.StreamlabsSocketEvent += EventReceiverEvent

	## Auto Connect if key is given in settings
	if settings["socket_token"]:
		EventReceiver.Connect(settings["socket_token"])
	else:
		Parent.Log("INIT", "Stream Labs Socket Token is required. This can be found on the website via the left-hand side menu -> API Settings -> API Tokens.")

	return


# ---------------------------
# [Required] Execute Data / Process messages
# ---------------------------
def Execute(data):
	return


# ---------------------------
# [Required] Tick method (Gets called during every iteration even when there is no incoming data)
# ---------------------------
def Tick():
	CheckAndProcessReset()
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


#---------------------------
#   [Optional] Unload (Called when a user reloads their scripts or closes the bot / cleanup stuff)
#---------------------------
def Unload():
	# Disconnect EventReceiver cleanly
	global EventReceiver
	if EventReceiver and EventReceiver.IsConnected:
		EventReceiver.Disconnect()
	EventReceiver = None
	return


#---------------------------
# File IO Functions
#---------------------------
def ReadResetDate():
	global resetDateFilePath
	resetDate = None
	if os.path.isfile(resetDateFilePath):
		Parent.Log("RESET DATE", "Reset Date File Found!")
		with open(resetDateFilePath) as f:
			resetDateText = f.readline()
			resetDateFromFile = datetime.strptime(resetDateText, "%Y-%m-%dT%H:%M:%S.%f")
			# Reset hour again in the event the user changed the reset hour after the file was created.
			resetDateFromFile = resetDateFromFile.replace(hour=int(settings["resetHour"]))
			resetDate = resetDateFromFile
			Parent.Log("RESET DATE", str(resetDate))
	else:
		Parent.Log("RESET DATE", "Reset Date File NOT Found!")
		resetDate = datetime.now().replace(hour=int(settings["resetHour"]), minute=0)
		resetDate += timedelta(days=1)

	WriteResetDate(resetDate)
	return resetDate


def WriteResetDate(dateToWrite):
	resetDateFile = open(resetDateFilePath, "w")
	resetDateFile.write(dateToWrite.isoformat())
	resetDateFile.close()


def SimpleWriteToFile(filePath, text):
	file = open(filePath, "w")
	file.write(str(text))
	file.close()


def ReadCurrentSubs():
	currentSubs = 0
	if os.path.isfile(subCurrentFilePath):
		with open(subCurrentFilePath) as f:
			currentSubs = int(f.readline())
	else:
		SimpleWriteToFile(subCurrentFilePath, currentSubs)
	return currentSubs


def ReadCurrentFollows():
	currentFollows = 0
	if os.path.isfile(followCurrentFilePath):
		with open(followCurrentFilePath) as f:
			currentFollows = int(f.readline())
	else:
		SimpleWriteToFile(followCurrentFilePath, currentFollows)
	return currentFollows


#---------------------------
# Handles resetting files based on date
#---------------------------
def CheckAndProcessReset():
	if datetime.now() >= settings["currentResetDate"]:
		# Reset settings
		nextDateTime = datetime.now().replace(hour=int(settings['resetHour']), minute=0)
		nextDateTime += timedelta(days=1)

		settings["currentResetDate"] = nextDateTime
		settings["currentSubs"] = 0
		settings["currentFollows"] = 0

		WriteResetDate(nextDateTime)
		SimpleWriteToFile(subCurrentFilePath, 0)
		SimpleWriteToFile(followCurrentFilePath, 0)
	return


#---------------------------------------
# Socket Event Handlers - Thanks to Ocgineer!
#---------------------------------------
def EventReceiverConnected(sender, args):
	Parent.Log(ScriptName, "Connected")
	return


def EventReceiverDisconnected(senmder, args):
	Parent.Log(ScriptName, "Disconnected")


def EventReceiverEvent(sender, args):
	evntdata = args.Data
	if evntdata and evntdata.For == "twitch_account":
		if evntdata.Type == "follow":
			for message in evntdata.Message:
				Parent.Log("follow", "{0} followed!!!".format(message.Name))
				currentFollows = int(settings["currentFollows"])
				currentFollows = currentFollows + 1
				settings["currentFollows"] = currentFollows
				SimpleWriteToFile(followCurrentFilePath, currentFollows)
				SimpleWriteToFile(followFullOutputPath, str(currentFollows) + settings["followDivisor"] + str(settings["followTarget"]))


		elif evntdata.Type == "bits":
			for message in evntdata.Message:
				Parent.Log("bits", message.Message)

		elif evntdata.Type == "subscription":
			for message in evntdata.Message:
				Parent.Log("subscription", "{0} subscribed!!!".format(message.Name))
				currentSubs = int(settings["currentSubs"])
				currentSubs = currentSubs + 1
				settings["currentSubs"] = currentSubs
				SimpleWriteToFile(subCurrentFilePath, currentSubs)
				SimpleWriteToFile(subFullOutputPath, str(currentSubs) + settings["subDivisor"] + str(settings["subTarget"]))

	return

# ---------------------------
# Helper method used by UI_Config.json to open the README.md file from script settings ui.
# ---------------------------
def OpenReadMe():
	location = os.path.join(os.path.dirname(__file__), "README.md")
	os.startfile(location)
	return
