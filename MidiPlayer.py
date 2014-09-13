# contains fluidsynth server, which starts upon creation
# Also contains methods to:
#   set tempo
#   play a note for a predefined duration
#   change instrument
# 
# basically, has methods that the tablature window should be exposed to
# 
# alternatively, a Playback object can coordinate playback by calling
# midiplayer methods


import threading
import fluidsynth
import math

# these two are used when connecting to JACK or seeing if the platform 
# is linux
import os
import sys

import PlayNote
#import AudioPlayer


from PyQt4 import QtGui, QtCore

class MidiPlayer:
    def __init__(self):        
        self.fs = fluidsynth.Synth()
        self.fs.start()
        
        # connect fluidsynth to JACK audio output if this is linux
        if 'linux' in sys.platform: 
            print('Since this is linux, we assume JACK is installed and use it to connect audio.')
            os.system("jack_connect fluidsynth:l_00 system:playback_1")
            os.system("jack_connect fluidsynth:r_00 system:playback_2")

#        self.sfid = self.fs.sfload("FluidR3_GM.sf2")
        self.sfid = self.fs.sfload("/usr/share/sounds/sf2/Scc1t2.sf2")
        
        # track number, sfid, bank number, instrument number
        self.fs.program_select(0, self.sfid, 0, 0)
        
        self.setTempo(120)
        
    def setTempo(self, tempo):
        self.tempo = tempo
                
    def playNote(self, parent, trackNum, pitch, volume=96, duration=-1, sameNote='False'):
        worker = PlayNote.PlayNote(self, self.fs, trackNum, pitch, volume, duration, sameNote)
        worker.start()
        
        return worker
        
    def changeInstrument(self, trackNum, instNum):
        self.fs.program_select(trackNum, self.sfid, 0, instNum-1)
        
#    def stopEverything(self):
#        self.fs.system_reset()      # stops everything  
        

    


