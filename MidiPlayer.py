# contains classes and methods that do the actual midi performance
import threading
import fluidsynth
import time
import os
import sys
import math

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

        sfid = self.fs.sfload("FluidR3_GM.sf2")
#        sfid = self.fs.sfload("/usr/share/sounds/sf2/Scc1t2.sf2")
        
        self.fs.program_select(0, sfid, 0, 0)
        
        self.setTempo(120)
        
    def setTempo(self, tempo):
        self.tempo = tempo
                
    def playNote(self, parent, trackNum, pitch, volume=96, duration=0.3):
        worker = PlayNote(self, self.fs, trackNum, pitch, volume, duration)
        worker.start()
        
        return worker
        
    def stopNote(self):
        self.fs.system_reset()      # stops everything  
        

class Playback:
    def __init__(self, parent):
        self._parent = parent
        self.midiPlayer = self._parent.midiPlayer
        self.cursorItem = self._parent.cursorItem
        self.tracks = self._parent.tracks
        self.tempo = self.midiPlayer.tempo
        
        self.doStopThread = False

        self.timer = QtCore.QTimer()
        QtCore.QObject.connect(
            self.timer, 
            QtCore.SIGNAL("timeout()"),
            self.doStuff)
            
        dt = int(1000.0 * 60.0 / (4.0 * self.tempo))
        self.timer.start(dt)
        
    def doStuff(self):
        # find all notes on all tracks at current cursor position
        iPos = self.cursorItem.iCursor
        for i in range(0, len(self.tracks)):
            for j in range(0, self.tracks[i].numYGrid):
                val = self.tracks[i].getFromTab(iPos, j)
                if val > -1:
                    pitch = self.tracks[i].convertNumberToPitch(j, val)
                    self.midiPlayer.playNote(self, i, pitch)

#                    worker = PlayNote(self, self.fs, i, 
                        
        self.cursorItem.moveRight()
        
    def stopPlayback(self):
        self.timer.stop()


class PlayNote(threading.Thread):
    def __init__(self, parent, fs, trackNum, pitch, volume, duration):
        threading.Thread.__init__(self)
        self._parent = parent
        self.trackNum = trackNum
        self.pitch = pitch
        self.volume = volume
        self.duration = duration
        self.fs = fs        # fluidsynth object
        
        self.event = threading.Event()
        
    def run(self):
        self.startTime = time.time()
        self.fs.noteon(0, self.pitch, self.volume)

        # wait and check roughly every 100 ms to see if something stops it by calling self.event.set()
        num = int(math.ceil(self.duration / 0.1));
        dt = self.duration / num
        for i in range(num):
            if self.event.is_set() or (self.duration < time.time() - self.startTime):
                break
            self.event.wait(dt)

        self.fs.noteoff(0, self.pitch)
    
    def stopNote(self):
        self.event.set()
