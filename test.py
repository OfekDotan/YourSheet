r"""
from music21 import *
us = environment.UserSettings()
us['musicxmlPath'] = r'C:\\Program Files\\MuseScore 3\\bin\\MuseScore3.exe'
us['musescoreDirectPNGPath'] = r'C:\\Program Files\\MuseScore 3\\bin\\MuseScore3.exe'
us['musicxmlPath']
parsed = converter.parse(r"C:\Users\Ofek\Desktop\FinalProject\YourSheet\13-limit_just_decatonic_scale_on_C.mid")
print(type(parsed))
parsed.show('musicxml.png')
"""

from logging import exception
import os
import mingus as mingus
import mingus.extra.lilypond
import mingus.midi.midi_file_in



myMIDI = r"midiResults\result.mid"

def MidiToSheet():
    myMIDI = r"midiResults\result.mid"
    fullPath = os.path.abspath(myMIDI)
    fullPath = (os.path.dirname(fullPath))
    fullPath = os.path.join(fullPath, "result.mid")
    print(fullPath)
    pdfFolder = r"sheetsPdf"
    pdfFullPath = os.path.abspath(pdfFolder)
    pdfFullPath = os.path.dirname(os.path.dirname(pdfFullPath))
    pdfFullPath = os.path.join(pdfFullPath, "YourSheet",pdfFolder)
    print(pdfFullPath)
    try:
        composition = mingus.midi.midi_file_in.MIDI_to_Composition(r"C:\Users\Ofek\Desktop\FinalProject\YourSheet\YourSheet\midiResults\result.mid")
    except:
        print("Oops!error occurred.")
    else:
        sheet = mingus.extra.lilypond.from_Composition(composition[0])
        print (sheet)
        param = mingus.extra.lilypond.to_pdf(sheet, r"C:\Users\Ofek\Desktop\FinalProject\YourSheet\YourSheet\sheetsPdf")
        print (param)


MidiToSheet()