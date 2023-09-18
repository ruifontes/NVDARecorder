# -*- coding: UTF-8 -*-
# Copyright (C) 2021-2023 Rui Fontes <rui.fontes@tiflotecnia.com> and Ângelo Abrantes <ampa4374@gmail.com>
# Based on the work of 高生旺 <coscell@gmail.com> with the same name
# This file is covered by the GNU General Public License.

# import the necessary modules.
import globalPluginHandler
try:
	import speech.speech as speech
except ModuleNotFoundError:
	import speech
import speechViewer
import gui
import core
import ui
import api
import os
import wx
import globalVars
import time
from scriptHandler import script
import addonHandler
# Start the translation process
addonHandler.initTranslation()

start = False
oldSpeak = speech.speak
contents = ""

# In the original work the file was stored in a path not easily accessed by the normal user, due to translation of the folder name in, at least, Windows 10 in portuguese...
_NRIniFile = os.path.join(globalVars.appArgs.configPath,"NVDARecord.txt")

def getSequenceText(sequence):
	return speechViewer.SPEECH_ITEM_SEPARATOR.join([x for x in sequence if isinstance(x, str)])

def mySpeak(sequence, *args, **kwargs):
	global contents
	oldSpeak(sequence, *args, **kwargs)
	text = getSequenceText(sequence)
	if text:
		if "\n" not in text:
			text += "\n"
		contents += text


class GlobalPlugin(globalPluginHandler.GlobalPlugin):
	# Creating the constructor of the newly created GlobalPlugin class.
	def __init__(self):
		# Call of the constructor of the parent class.
		super(GlobalPlugin, self).__init__()
		# Avoid use in secure screens
		if globalVars.appArgs.secure:
			return

	@script(
	# Translators: Message to be announced during Keyboard Help
	description=_("Activate/deactivate recording on NVDARecorder"),
	gesture="kb:alt+numpadplus")
	def script_record(self, gesture):
		global start
		start = not start
		if not start:
			speech.speak = oldSpeak
			global contents
			with open(_NRIniFile, "w", encoding = "utf-8") as file:
				file.write(contents)
				file.close()
				global recorded
				recorded = contents
				gui.mainFrame._popupSettingsDialog(ShowResults)
			ui.message(_("Recording stopped"))
			contents = ""
		else:
			ui.message(_("Start recording"))
			speech.speak = mySpeak


class ShowResults(wx.Dialog):
	def __init__(self, *args, **kwds):
		kwds["style"] = kwds.get("style", 0) | wx.DEFAULT_DIALOG_STYLE
		wx.Dialog.__init__(self, *args, **kwds)
		self.SetTitle(_("NVDA recorder"))

		sizer_1 = wx.BoxSizer(wx.VERTICAL)

		# Translators: Static text announcing the results
		label_1 = wx.StaticText(self, wx.ID_ANY, _("Here is the recorded text:"))
		sizer_1.Add(label_1, 0, 0, 0)

		global contents
		self.text_ctrl_1 = wx.TextCtrl(self, wx.ID_ANY, recorded, size = (550, 350), style=wx.TE_MULTILINE | wx.TE_READONLY)
		sizer_1.Add(self.text_ctrl_1, 0, 0, 0)

		sizer_2 = wx.StdDialogButtonSizer()
		sizer_1.Add(sizer_2, 0, wx.ALIGN_RIGHT | wx.ALL, 4)

		# Translators: Name of button to open the TXT file folder
		self.button_1 = wx.Button(self, wx.ID_ANY, _("Open NVDARecord.txt's folder"))
		self.button_1.SetDefault()
		sizer_2.Add(self.button_1, 0, 0, 0)

		# Translators: Name of button that allows to copy results to clipboard
		self.button_SAVE = wx.Button(self, wx.ID_ANY, _("Copy to clipboard"))
		sizer_2.Add(self.button_SAVE, 0, 0, 0)

		self.button_CLOSE = wx.Button(self, wx.ID_CLOSE, "")
		sizer_2.AddButton(self.button_CLOSE)

		sizer_2.Realize()

		self.SetSizer(sizer_1)
		sizer_1.Fit(self)

		self.SetEscapeId(self.button_CLOSE.GetId())
		self.Bind(wx.EVT_BUTTON, self.openFolder, self.button_1)
		self.Bind(wx.EVT_BUTTON, self.copyToClip, self.button_SAVE)
		self.Bind(wx.EVT_BUTTON, self.quit, self.button_CLOSE)

		self.Layout()
		self.CentreOnScreen()

	def openFolder(self, event):
		self.Destroy()
		event.Skip()
		os.startfile(os.path.join(globalVars.appArgs.configPath))

	def copyToClip(self, event):
		event.Skip()
		# Copy result to clipboard
		api.copyToClip(recorded)

	def quit(self, event):
		self.Destroy()
		event.Skip()

