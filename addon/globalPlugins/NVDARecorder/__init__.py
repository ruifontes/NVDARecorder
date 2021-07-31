# -*- coding: UTF-8 -*-
# Copyright (C) 2021 Rui Fontes <rui.fontes@tiflotecnia.com> and Ângelo Abrantes <ampa4374@gmail.com>
# Based on the work of 高生旺 <coscell@gmail.com> with the same name
# This file is covered by the GNU General Public License.

# import the necessary modules.
import globalPluginHandler
try:
	import speech.speech as speech
except ModuleNotFoundError:
	import speech
import speechViewer
import ui
import os
import globalVars
import ctypes
import time
import addonHandler
# For translation
addonHandler.initTranslation()

start = False
oldSpeak = speech.speak
contents = ""

# In the original work the file was stored in a path not easily accessed by the normal user, due to translation of the folder name in, at least, Windows 10 in portuguese...
_NRIniFile = os.path.join(globalVars.appArgs.configPath, "NVDARecord.txt")

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
  def script_record(self, gesture):
    global start
    start = not start
    if not start:
      speech.speak = oldSpeak
      global contents
      with open(_NRIniFile, "w", encoding = "utf-8") as file:
        file.write(contents)
      contents = ""
      ui.message(_("Recording stopped"))
      time.sleep(0.4)
      z = ctypes.windll.shell32.ShellExecuteW(None, "open", _NRIniFile, None, None, 10)
    else:
      ui.message(_("Start recording"))
      speech.speak = mySpeak

  script_record.__doc__ = _("Activate/deactivate recording on NVDARecorder")

  __gestures = { "kb:alt+numpadplus":"record" }
