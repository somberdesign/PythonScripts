
import random, math, PySimpleGUI as sg, SeriesManager_Data as data, contextlib
from tkinter import *
import datetime
import os

FILENAME_DB = "titles.db"
FONT_LABEL = ("Helvetica", 10, "bold")
KEY_LISTBOX_ACTIVETITLES = "__ACTIVETITLES__"
KEY_LISTBOX_INACTIVETITLES = "__INACTIVETITLES__"
KEY_DISPLAYTEXT = "__DISPLAYTEXT__"
LASTVIEWEDDATE_DISPLAY_COLUMN_WIDTH = 10
LOGFILE = os.path.join(os.path.dirname(__file__), "SeriesManage.log")


idx_title = 0
idx_totalViews = 1
idx_lastDateViewed = 2
idx_titleMultiplier = 3
idx_finalMultiplier = 4
idx_highTicketNumber = 5
idx_titleId = 6

activeRecordCount = None

DisplayColumns = [idx_highTicketNumber, idx_titleMultiplier, idx_totalViews, idx_title, idx_lastDateViewed]

def GetDisplayText(oData):
	global activeRecordCount

	def GetOutput(allRecordRows, maxColumnWidth):
		displayText = ""
		for row in allRecordRows:
			for i in DisplayColumns:
				if i == idx_lastDateViewed:
					displayText += "{0}".format(str(row[i])[:LASTVIEWEDDATE_DISPLAY_COLUMN_WIDTH].ljust(maxColumnWidth[i] + 2))
				else:
					displayText += "{0}".format(str(row[i]).ljust(maxColumnWidth[i] + 2))
			displayText += "\n"
		
		return displayText


	allRecordRows = oData.GetDisplayTitles()
	activeRecordCount = len(allRecordRows)
	maxColumnWidth = [0, 0, 0, 0, 0, 0, 0]
	PerformCalculations(allRecordRows, maxColumnWidth)

	return GetOutput(allRecordRows, maxColumnWidth);


def GetAddSeriesWindow():
	txtDisplay = sg.Text("", key=KEY_DISPLAYTEXT, font=("Courier New", 10), size=(50,1), text_color="red")
	sldMultiplier = sg.Slider(range=(1,40), default_value=10, orientation="horizontal")
	lblMultiplier = sg.Text("\nMultiplier", font=FONT_LABEL, size=(12,2))
	inputText = sg.InputText()

	lblTitle = sg.Text	 ("Series Name", font=FONT_LABEL, size=(12,1))
	
	
	layout = [
		[txtDisplay],
		[lblTitle, inputText],
		[lblMultiplier, sldMultiplier],
		[],
		[sg.Button('Ok'), sg.Button('Cancel')]
	]
	
	window = sg.Window("Add Series", layout, finalize=True)
	inputText.SetFocus()

	return window


def GetDisplayWindow():
	btnLotteryDraw = sg.Button("Lottery Draw")
	btnManageSeries = sg.Button("Manage Series")
	btnAddSeries = sg.Button("Add Series")
	btnExit = sg.Button("Exit")
	txtDisplay = sg.Text(GetDisplayText(oData), key=KEY_DISPLAYTEXT, font=("Courier New", 10))

	layout = [
				[txtDisplay],
				[btnLotteryDraw, btnAddSeries, btnManageSeries, btnExit]
			 ]
	return sg.Window("Series Picker", layout)

def GetManageSeriesWindow(oData):
	
	activeItems = oData.GetActiveTitles()
	inactiveItems = oData.GetInactiveTitles()
	
	activeTitles = []
	for row in activeItems:
		activeTitles.append(row[idx_title])

	inactiveTitles = []
	for row in inactiveItems:
		inactiveTitles.append(row[idx_title])

	cboActiveTitles = sg.Listbox(values=activeTitles, size=(30, 8), key=KEY_LISTBOX_ACTIVETITLES, enable_events=True)
	txtMarkInactive = sg.Text("Active Items", font=FONT_LABEL, justification="center")
	cboInactiveTitles = sg.Listbox(values=inactiveTitles, size=(30, 8), key=KEY_LISTBOX_INACTIVETITLES, enable_events=True)
	txtMarkActive = sg.Text("Inactive Items", font=FONT_LABEL, justification="center")
	btnDone = sg.Button("Done")

	activeLayout = [
		[txtMarkInactive],
		[cboActiveTitles]
		]

	inactiveLayout = [
		[txtMarkActive],
		[cboInactiveTitles]
		]
	layout = [
			[sg.Column(activeLayout), sg.Column(inactiveLayout)],
			[btnDone]
		]

	return sg.Window("Manage Series", layout)

def PerformAddSeries(oData):
	addWindow = GetAddSeriesWindow()
	doneWithSeries = False

	while not doneWithSeries:
		addEvent, addValues = addWindow.Read()

		if addEvent == "Ok":
			title = addValues[0]
			multiplier = addValues[1] / 10
			seriesExists = oData.SeriesExists(title)
			if seriesExists == True:
				addWindow[KEY_DISPLAYTEXT]("That series already exists")
			else:
				oData.InsertTitle(title, multiplier)
				addWindow.close()
				return

		if addEvent is None or addEvent == "Cancel":
			addWindow.close()
			return


def PerformCalculations(allRecordRows, maxColumnWidth):
	baseMultiplier = 0.1
	baseMultiplierValue = 1
	highTicketTotal = 0
	for row in allRecordRows:
		
		# calculate multiplier
		row[idx_finalMultiplier] = round(baseMultiplierValue * row[idx_titleMultiplier], 2)
		highTicketTotal += row[idx_finalMultiplier] * 100
		row[idx_highTicketNumber] = highTicketTotal
		baseMultiplierValue += baseMultiplierValue * baseMultiplier

		# find max column widths
		for i in range(0, len(allRecordRows[0])):
			if i == idx_lastDateViewed:
				maxColumnWidth[i] = LASTVIEWEDDATE_DISPLAY_COLUMN_WIDTH
			else:
				maxColumnWidth[i] = len(str(row[i])) if len(str(row[i])) > maxColumnWidth[i] else maxColumnWidth[i]



def PerformDraw(oData):
	allRecordRows = oData.GetDisplayTitles() # this must be the same function that appears in GetDisplayText
	maxColumnWidth = [0, 0, 0, 0, 0, 0, 0]
	PerformCalculations(allRecordRows, maxColumnWidth)

	highestTicketNumber = 0
	for row in allRecordRows:
		highestTicketNumber = row[idx_highTicketNumber] if row[idx_highTicketNumber] > highestTicketNumber else highestTicketNumber
	highestTicketNumber = math.floor(highestTicketNumber + highestTicketNumber * 0.1)

	goldenTicket = random.randrange(highestTicketNumber)
	Log_Message(f'highestTicketNumber={highestTicketNumber}, goldenTicket={goldenTicket}')

	selectedIdx = 0
	outText = ""
	for i in range(0, len(allRecordRows)):
		if goldenTicket <= allRecordRows[i][idx_highTicketNumber]:
			selectedIdx = i
			break

	oData.InsertUse(allRecordRows[selectedIdx][idx_titleId])


def PerformManageSeries(oData):

	while True:
		manageWindow = GetManageSeriesWindow(oData)
		manageEvent, manageValues = manageWindow.Read()

		if manageEvent is None or manageEvent == "Done": # go back to main display window
			manageWindow.close()
			return

		if len(manageValues[KEY_LISTBOX_ACTIVETITLES]) > 0:
			oData.SetTitleIsActive(manageValues[KEY_LISTBOX_ACTIVETITLES][0], 0)
			manageWindow.close()

		if len(manageValues[KEY_LISTBOX_INACTIVETITLES]) > 0:
			oData.SetTitleIsActive(manageValues[KEY_LISTBOX_INACTIVETITLES][0], 1)
			manageWindow.close()

def Log_Message(message:str):
	with open(LOGFILE, 'a') as file:
		file.write(f'{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")} - {message}\n')
	print(message)

###########################################################################################

Log_Message('Executing Series Manager')

with data.SeriesManager_Data() as oData:

	displayWindow = GetDisplayWindow()

	while True:

		event, values = displayWindow.Read()
		
		if isinstance(activeRecordCount, int):
			displayWindow.TKroot.title = (f'Series Manager ({activeRecordCount} active titles')

		if event is None or event == "Exit":
			break

		if event == "Add Series":
			displayWindow.close()
			PerformAddSeries(oData)
			displayWindow = GetDisplayWindow()

		if event == "Lottery Draw":
			PerformDraw(oData)
			displayWindow[KEY_DISPLAYTEXT](GetDisplayText(oData))

		if event == "Manage Series":
			displayWindow.close()
			PerformManageSeries(oData)
			displayWindow = GetDisplayWindow()

Log_Message('Terminated Series Manager')



